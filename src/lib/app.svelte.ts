/**
 * Globaler App-Zustand (Svelte 5 Runes): Screen-Routing, laufende Partie,
 * Abspielen der Engine-Ereignisse als Animation, Computerzüge, Toasts.
 */
import {
  applyAction,
  computerAction,
  createGame,
  defaultRng,
  getItem,
  type Action,
  type GameEvent,
  type GameMode,
  type GameState,
  type PlayerSetup,
  type Tank,
} from '../engine';

export type Screen = 'menu' | 'setup' | 'battle' | 'load' | 'help';

export interface Toast {
  text: string;
  kind: 'error' | 'info';
}

export interface Fx {
  id: number;
  tankId: string;
  kind: 'damage' | 'miss' | 'dodge' | 'malfunction' | 'credits' | 'shop' | 'wait';
  text: string;
}

export interface LogEntry {
  id: number;
  kind: 'turn' | 'hit' | 'explode' | 'miss' | 'dodge' | 'malfunction' | 'shop' | 'credits' | 'end' | 'info';
  text: string;
}

export interface Projectile {
  from: string;
  to: string;
  color: string;
}

/** Animationsdauern in ms */
const T = {
  fire: 450,
  impact: 650,
  explode: 900,
  short: 500,
  turn: 350,
  computerThink: 700,
  fx: 1300,
  banner: 1100,
  toast: 3000,
};

class App {
  screen = $state<Screen>('menu');
  setupMode = $state<GameMode>('pvc');
  toast = $state<Toast | null>(null);

  /** Tatsächlicher Spielzustand (Engine-Wahrheit) */
  state = $state.raw<GameState | null>(null);
  /** Angezeigter Zustand – läuft während Animationen dem echten Zustand hinterher */
  view = $state<GameState | null>(null);

  busy = $state(false);
  log = $state<LogEntry[]>([]);
  fx = $state<Fx[]>([]);
  projectile = $state<Projectile | null>(null);
  shaking = $state<string | null>(null);
  exploding = $state<string | null>(null);
  firing = $state<string | null>(null);
  banner = $state<string | null>(null);

  current = $derived.by<Tank | undefined>(() => {
    const v = this.view;
    return v && !v.finished ? v.tanks[v.currentIndex] : undefined;
  });

  canAct = $derived(!this.busy && !!this.current && !this.current.isComputer);

  #seq = 0;
  #toastTimer: ReturnType<typeof setTimeout> | undefined;
  #lastSetup: { mode: GameMode; players: PlayerSetup[] } | null = null;
  /** Erhöht sich bei jedem Spielwechsel – laufende Abspielschleifen brechen dann ab. */
  #epoch = 0;
  #skipping = false;
  #wake: (() => void) | null = null;

  // ---------- Navigation ----------

  go(screen: Screen) {
    if (screen !== 'battle') this.#stopGame();
    this.screen = screen;
  }

  openSetup(mode: GameMode) {
    this.setupMode = mode;
    this.go('setup');
  }

  showToast(text: string, kind: Toast['kind'] = 'error') {
    clearTimeout(this.#toastTimer);
    this.toast = { text, kind };
    this.#toastTimer = setTimeout(() => (this.toast = null), T.toast);
  }

  // ---------- Partie ----------

  startGame(mode: GameMode, players: PlayerSetup[]) {
    this.#lastSetup = { mode, players: players.map((p) => ({ ...p, stats: { ...p.stats } })) };
    this.#begin(createGame(mode, players, defaultRng), true);
  }

  rematch() {
    const setup = this.#lastSetup ?? (this.state ? setupFromState(this.state) : null);
    if (!setup) return this.go('menu');
    this.startGame(setup.mode, setup.players);
  }

  loadState(state: GameState) {
    this.#lastSetup = null;
    this.#begin(state, false);
    this.#addLog('info', `Spielstand geladen – Runde ${state.round}`);
  }

  async act(action: Action): Promise<void> {
    if (!this.state || this.state.finished || this.busy) return;
    const epoch = this.#epoch;
    this.busy = true;
    try {
      await this.#perform(action, epoch);
      await this.#runComputers(epoch);
    } finally {
      if (epoch === this.#epoch) {
        this.busy = false;
        this.#skipping = false;
      }
    }
  }

  /** Laufende Animation vorspulen (Klick während `busy`). */
  skip() {
    if (!this.busy) return;
    this.#skipping = true;
    this.#wake?.();
  }

  // ---------- intern ----------

  #begin(state: GameState, fresh: boolean) {
    this.#stopGame();
    this.state = state;
    this.view = structuredClone(state);
    this.screen = 'battle';
    if (fresh) {
      this.#addLog('info', `Neues Spiel – ${state.tanks.length} Panzer`);
      this.#addLog('turn', `Runde ${state.round}: ${state.tanks[state.currentIndex]!.name} ist am Zug`);
    }
    const epoch = this.#epoch;
    const cur = state.tanks[state.currentIndex];
    if (!state.finished && cur?.isComputer) {
      this.busy = true;
      void this.#runComputers(epoch).finally(() => {
        if (epoch === this.#epoch) {
          this.busy = false;
          this.#skipping = false;
        }
      });
    }
  }

  #stopGame() {
    this.#epoch++;
    this.#wake?.();
    this.#wake = null;
    this.busy = false;
    this.#skipping = false;
    this.log = [];
    this.fx = [];
    this.projectile = null;
    this.shaking = this.exploding = this.firing = this.banner = null;
  }

  async #runComputers(epoch: number) {
    while (epoch === this.#epoch && this.state && !this.state.finished) {
      const cur = this.state.tanks[this.state.currentIndex]!;
      if (!cur.isComputer) break;
      await this.#sleep(T.computerThink);
      if (epoch !== this.#epoch) return;
      await this.#perform(computerAction(this.state), epoch);
    }
  }

  async #perform(action: Action, epoch: number) {
    let result;
    try {
      result = applyAction(this.state!, action, defaultRng);
    } catch (e) {
      this.showToast(e instanceof Error ? e.message : String(e));
      return;
    }
    this.state = result.state;
    for (const ev of result.events) {
      if (epoch !== this.#epoch) return;
      await this.#play(ev, result.state);
    }
    if (epoch === this.#epoch) this.view = structuredClone(result.state);
  }

  #name(id: string): string {
    return this.state?.tanks.find((t) => t.id === id)?.name ?? id;
  }

  #viewTank(id: string): Tank | undefined {
    return this.view?.tanks.find((t) => t.id === id);
  }

  async #play(ev: GameEvent, final: GameState) {
    switch (ev.type) {
      case 'turnStart': {
        this.view = structuredClone(final);
        this.#addLog('turn', `Runde ${ev.round}: ${this.#name(ev.tankId)} ist am Zug`);
        await this.#sleep(T.turn);
        break;
      }
      case 'malfunction': {
        this.#addLog('malfunction', `${this.#name(ev.tankId)}: Fehlfunktion! Der Schuss bleibt aus.`);
        this.#addFx(ev.tankId, 'malfunction', '⚙️ Fehlfunktion');
        this.shaking = ev.tankId;
        await this.#sleep(T.short);
        this.shaking = null;
        break;
      }
      case 'shot': {
        const from = this.#viewTank(ev.from);
        if (from) from.ammo = Math.max(0, from.ammo - 1);
        this.firing = ev.from;
        this.projectile = { from: ev.from, to: ev.to, color: from?.color ?? '#ffd54f' };
        await this.#sleep(T.fire);
        this.firing = null;
        this.projectile = null;
        break;
      }
      case 'miss': {
        this.#addLog('miss', `${this.#name(ev.from)} schießt daneben.`);
        this.#addFx(ev.to, 'miss', 'Daneben');
        await this.#sleep(T.short);
        break;
      }
      case 'dodge': {
        this.#addLog('dodge', `${this.#name(ev.to)} weicht dem Schuss von ${this.#name(ev.from)} aus.`);
        this.#addFx(ev.to, 'dodge', 'Ausgewichen!');
        await this.#sleep(T.short);
        break;
      }
      case 'hit': {
        const target = this.#viewTank(ev.to);
        const real = final.tanks.find((t) => t.id === ev.to);
        if (target && real) {
          target.armor = real.armor;
          target.dmgMitigation = real.dmgMitigation;
          target.malfunction = real.malfunction;
        }
        this.#addLog('hit', `${this.#name(ev.from)} trifft ${this.#name(ev.to)}: −${ev.damage} Panzerung`);
        this.#addFx(ev.to, 'damage', `−${ev.damage}`);
        this.shaking = ev.to;
        await this.#sleep(T.impact);
        this.shaking = null;
        break;
      }
      case 'explode': {
        this.exploding = ev.tankId;
        this.#addLog('explode', `💥 ${this.#name(ev.tankId)} wurde von ${this.#name(ev.by)} zerstört!`);
        await this.#sleep(T.explode / 2);
        const t = this.#viewTank(ev.tankId);
        if (t) t.alive = false;
        await this.#sleep(T.explode / 2);
        this.exploding = null;
        break;
      }
      case 'credits': {
        const t = this.#viewTank(ev.tankId);
        if (t) t.credits += ev.amount;
        const why = ev.reason === 'kill' ? ' (Abschuss)' : ev.reason === 'hit' ? ' (Treffer)' : '';
        this.#addLog('credits', `${this.#name(ev.tankId)}: +${ev.amount} Credit${ev.amount === 1 ? '' : 's'}${why}`);
        this.#addFx(ev.tankId, 'credits', `+${ev.amount} 💰`);
        break;
      }
      case 'bought': {
        const item = getItem(ev.itemId);
        const t = this.#viewTank(ev.tankId);
        const real = final.tanks.find((x) => x.id === ev.tankId);
        if (t && real) Object.assign(t, { armor: real.armor, ammo: real.ammo, malfunction: real.malfunction, credits: real.credits });
        this.#addLog('shop', `${this.#name(ev.tankId)} kauft ${item?.name ?? ev.itemId}.`);
        this.#addFx(ev.tankId, 'shop', `🛒 ${item?.name ?? ''}`);
        await this.#sleep(T.short);
        break;
      }
      case 'waited': {
        this.#addLog('info', `${this.#name(ev.tankId)} wartet.`);
        this.#addFx(ev.tankId, 'wait', '⏳');
        await this.#sleep(T.short);
        break;
      }
      case 'gameOver': {
        this.view = structuredClone(final);
        const text = ev.winnerId ? `🏆 ${this.#name(ev.winnerId)} gewinnt!` : 'Kein Panzer überlebt – Unentschieden.';
        this.#addLog('end', text);
        this.banner = text;
        await this.#sleep(T.banner);
        this.banner = null;
        break;
      }
    }
  }

  #addLog(kind: LogEntry['kind'], text: string) {
    this.log.push({ id: ++this.#seq, kind, text });
  }

  #addFx(tankId: string, kind: Fx['kind'], text: string) {
    const id = ++this.#seq;
    this.fx.push({ id, tankId, kind, text });
    setTimeout(() => {
      this.fx = this.fx.filter((f) => f.id !== id);
    }, T.fx);
  }

  /** Wartet `ms`, außer es wird vorgespult. */
  #sleep(ms: number): Promise<void> {
    if (this.#skipping) return Promise.resolve();
    return new Promise((resolve) => {
      const timer = setTimeout(done, ms);
      const self = this;
      function done() {
        clearTimeout(timer);
        if (self.#wake === done) self.#wake = null;
        resolve();
      }
      this.#wake = done;
    });
  }
}

/** Für Revanche nach geladenem Spiel: Startwerte möglichst gut rekonstruieren. */
function setupFromState(state: GameState): { mode: GameMode; players: PlayerSetup[] } {
  const players = [...state.tanks]
    .sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }))
    .map((t) => ({
      name: t.name,
      isComputer: t.isComputer,
      stats: {
        armor: t.armorStart,
        ammo: t.ammo + t.record.shots,
        power: t.power,
        dmgMitigation: t.dmgMitigation + t.record.hitsTaken,
      },
    }));
  return { mode: state.mode, players };
}

export const app = new App();
