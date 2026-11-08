/**
 * Spielablauf als reine Funktionen: Zustand + Aktion -> neuer Zustand + Ereignisse.
 * Portiert aus python/src/game.py (ohne input()/sleep()).
 */
import { MAX_PLAYERS, MIN_PLAYERS, SETTINGS, TANK_COLORS } from './config';
import { randInt, type Rng } from './rng';
import { applyPurchase, canAfford, getItem } from './shop';
import { createTank, resolveShot } from './tank';
import type { Action, ActionResult, GameEvent, GameMode, GameState, PlayerSetup, Tank } from './types';

export function createGame(mode: GameMode, players: PlayerSetup[], rng: Rng): GameState {
  if (players.length < MIN_PLAYERS || players.length > MAX_PLAYERS) {
    throw new Error(`Spielerzahl muss zwischen ${MIN_PLAYERS} und ${MAX_PLAYERS} liegen`);
  }
  const created = players.map((p, i) =>
    createTank(`p${i + 1}`, p.name.trim() || `Spieler ${i + 1}`, p.stats, p.isComputer, TANK_COLORS[i % TANK_COLORS.length]!),
  );
  // Startspieler wird ausgelost, damit Spieler 1 keinen festen Vorteil hat.
  // Die Liste wird so rotiert, dass er vorne steht – damit beginnt eine neue Runde
  // immer beim Umlauf über das Listenende.
  const start = randInt(rng, 0, created.length - 1);
  const tanks = [...created.slice(start), ...created.slice(0, start)];
  return {
    version: 1,
    mode,
    tanks,
    currentIndex: 0,
    round: 1,
    finished: false,
    winnerId: null,
  };
}

export function getTank(state: GameState, id: string): Tank | undefined {
  return state.tanks.find((t) => t.id === id);
}

export function currentTank(state: GameState): Tank {
  const t = state.tanks[state.currentIndex];
  if (!t) throw new Error('Ungültiger currentIndex');
  return t;
}

export function aliveTanks(state: GameState): Tank[] {
  return state.tanks.filter((t) => t.alive);
}

export function validTargets(state: GameState, attackerId: string): Tank[] {
  return state.tanks.filter((t) => t.alive && t.id !== attackerId);
}

/** Liefert eine Fehlermeldung oder null, wenn die Aktion erlaubt ist. */
export function validateAction(state: GameState, action: Action): string | null {
  if (state.finished) return 'Das Spiel ist beendet.';
  const tank = currentTank(state);
  switch (action.type) {
    case 'shoot': {
      if (tank.ammo <= 0) return 'Keine Munition mehr.';
      const target = getTank(state, action.targetId);
      if (!target || !target.alive || target.id === tank.id) return 'Ungültiges Ziel.';
      return null;
    }
    case 'buy': {
      const item = getItem(action.itemId);
      if (!item) return 'Artikel existiert nicht.';
      if (!canAfford(tank, item)) return `Nicht genug Credits (${item.price} benötigt).`;
      return null;
    }
    case 'wait':
      return null;
  }
}

function advanceTurn(state: GameState, events: GameEvent[]): void {
  const n = state.tanks.length;
  for (let step = 1; step <= n; step++) {
    const idx = (state.currentIndex + step) % n;
    if (state.tanks[idx]!.alive) {
      // Umlauf über das Listenende -> neue Runde
      if (state.currentIndex + step >= n) state.round += 1;
      state.currentIndex = idx;
      events.push({ type: 'turnStart', tankId: state.tanks[idx]!.id, round: state.round });
      return;
    }
  }
}

function checkGameOver(state: GameState, events: GameEvent[]): boolean {
  const alive = aliveTanks(state);
  if (alive.length > 1) return false;
  state.finished = true;
  state.winnerId = alive[0]?.id ?? null;
  events.push({ type: 'gameOver', winnerId: state.winnerId });
  return true;
}

export function applyAction(prev: GameState, action: Action, rng: Rng): ActionResult {
  const error = validateAction(prev, action);
  if (error) throw new Error(error);

  const state = structuredClone(prev);
  const events: GameEvent[] = [];
  const tank = currentTank(state);

  switch (action.type) {
    case 'shoot':
      resolveShot(tank, getTank(state, action.targetId)!, rng, events);
      break;
    case 'buy':
      applyPurchase(tank, getItem(action.itemId)!);
      events.push({ type: 'bought', tankId: tank.id, itemId: action.itemId });
      break;
    case 'wait':
      tank.credits += SETTINGS.waitReward;
      events.push({ type: 'waited', tankId: tank.id });
      events.push({ type: 'credits', tankId: tank.id, amount: SETTINGS.waitReward, reason: 'wait' });
      break;
  }

  if (!checkGameOver(state, events)) advanceTurn(state, events);
  return { state, events };
}
