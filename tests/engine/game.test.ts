import { describe, expect, it } from 'vitest';
import {
  PRESET_TANKS,
  SETTINGS,
  aliveTanks,
  applyAction,
  computerAction,
  createGame,
  currentTank,
  deserialize,
  sanitizeSaveName,
  serialize,
  validTargets,
  validateAction,
  type PlayerSetup,
} from '../../src/engine';
import { game, rolls, seeded, stats, tank } from './helpers';

const setup = (n: number, computerIdx: number[] = []): PlayerSetup[] =>
  Array.from({ length: n }, (_, i) => ({ name: `P${i + 1}`, isComputer: computerIdx.includes(i), stats: PRESET_TANKS[i % 4]!.stats }));

describe('createGame', () => {
  it('legt Panzer an, Startspieler steht vorne', () => {
    const s = createGame('pvc', setup(2, [1]), seeded());
    expect(s.tanks).toHaveLength(2);
    expect(s.currentIndex).toBe(0);
    expect(s.round).toBe(1);
    expect(s.tanks.find((t) => t.name === 'P2')!.isComputer).toBe(true);
  });

  it('Startspieler wird ausgelost', () => {
    const starters = new Set(Array.from({ length: 30 }, (_, i) => createGame('pvp', setup(4), seeded(i)).tanks[0]!.name));
    expect(starters.size).toBeGreaterThan(1);
  });

  it('Spielerzahl wird geprüft', () => {
    expect(() => createGame('pvp', setup(1), seeded())).toThrow();
    expect(() => createGame('pvp', setup(9), seeded())).toThrow();
  });

  it('leere Namen werden ersetzt', () => {
    const s = createGame('pvp', [{ ...setup(1)[0]!, name: '  ' }, setup(2)[1]!], seeded(3));
    expect(s.tanks.map((t) => t.name)).toContain('Spieler 1');
  });
});

describe('Zugfolge', () => {
  it('nach dem Zug ist der nächste dran', () => {
    const { state } = applyAction(game([tank('a'), tank('b'), tank('c')]), { type: 'wait' }, seeded());
    expect(currentTank(state).id).toBe('b');
  });

  it('Umlauf erhöht die Runde', () => {
    const { state } = applyAction(game([tank('a'), tank('b')], 1), { type: 'wait' }, seeded());
    expect(state.currentIndex).toBe(0);
    expect(state.round).toBe(2);
  });

  it('zerstörte Panzer werden übersprungen', () => {
    const s = game([tank('a'), tank('b'), tank('c')]);
    s.tanks[1]!.alive = false;
    const { state } = applyAction(s, { type: 'wait' }, seeded());
    expect(currentTank(state).id).toBe('c');
  });

  it('Eingabezustand bleibt unverändert (immutabel)', () => {
    const s = game([tank('a'), tank('b')]);
    const before = structuredClone(s);
    applyAction(s, { type: 'shoot', targetId: 'b' }, rolls.hit());
    expect(s).toEqual(before);
  });

  it('Warten gibt Credits', () => {
    const { state } = applyAction(game([tank('a'), tank('b')]), { type: 'wait' }, seeded());
    expect(state.tanks[0]!.credits).toBe(SETTINGS.waitReward);
  });
});

describe('Schießen', () => {
  it('ohne Munition nicht erlaubt', () => {
    const a = tank('a', stats(100, 0));
    expect(validateAction(game([a, tank('b')]), { type: 'shoot', targetId: 'b' })).toMatch(/Munition/);
  });

  it('nicht auf sich selbst oder zerstörte Panzer', () => {
    const s = game([tank('a'), tank('b'), tank('c')]);
    s.tanks[2]!.alive = false;
    expect(validateAction(s, { type: 'shoot', targetId: 'a' })).toMatch(/Ziel/);
    expect(validateAction(s, { type: 'shoot', targetId: 'c' })).toMatch(/Ziel/);
    expect(validTargets(s, 'a').map((t) => t.id)).toEqual(['b']);
  });

  it('freie Zielwahl bei mehreren Gegnern', () => {
    const { state } = applyAction(game([tank('a'), tank('b'), tank('c')]), { type: 'shoot', targetId: 'c' }, rolls.hit());
    expect(state.tanks[1]!.armor).toBe(100);
    expect(state.tanks[2]!.armor).toBeLessThan(100);
  });

  it('letzter Abschuss beendet das Spiel', () => {
    const a = tank('a', stats(100, 10, 50, 0));
    const b = tank('b', stats(10, 10, 10, 0));
    const { state, events } = applyAction(game([a, b]), { type: 'shoot', targetId: 'b' }, rolls.hit());
    expect(state.finished).toBe(true);
    expect(state.winnerId).toBe('a');
    expect(events.at(-1)).toEqual({ type: 'gameOver', winnerId: 'a' });
    expect(aliveTanks(state)).toHaveLength(1);
    expect(() => applyAction(state, { type: 'wait' }, seeded())).toThrow();
  });
});

describe('KI', () => {
  it('schießt, wenn möglich', () => {
    expect(computerAction(game([tank('a', stats(), true), tank('b')]))).toEqual({ type: 'shoot', targetId: 'b' });
  });

  it('kauft Munition, wenn leer und genug Credits', () => {
    const me = tank('a', stats(100, 0), true);
    me.credits = 4;
    expect(computerAction(game([me, tank('b')]))).toEqual({ type: 'buy', itemId: 'ammo2' });
  });

  it('wartet, wenn leer und pleite', () => {
    expect(computerAction(game([tank('a', stats(100, 0), true), tank('b')]))).toEqual({ type: 'wait' });
  });

  it('repariert bei hoher Fehlfunktion', () => {
    const me = tank('a', stats(), true);
    me.malfunction = 40;
    me.credits = 2;
    expect(computerAction(game([me, tank('b')]))).toEqual({ type: 'buy', itemId: 'repair' });
  });

  it('zielt auf den am schnellsten zerstörbaren Gegner', () => {
    const strong = tank('b', stats(200));
    const weak = tank('c', stats(30));
    expect(computerAction(game([tank('a', stats(), true), strong, weak]))).toEqual({ type: 'shoot', targetId: 'c' });
  });

  it('KI gegen KI spielt eine Partie zu Ende', () => {
    let s = createGame('pvp', setup(4, [0, 1, 2, 3]), seeded(7));
    const rng = seeded(8);
    for (let i = 0; i < 2000 && !s.finished; i++) s = applyAction(s, computerAction(s), rng).state;
    expect(s.finished).toBe(true);
    expect(aliveTanks(s)).toHaveLength(1);
  });
});

describe('Spielstände', () => {
  it('Roundtrip erhält den Zustand', () => {
    const s = createGame('pvc', setup(2, [1]), seeded());
    const file = deserialize(serialize('Mein Spiel', s, new Date('2026-01-01T00:00:00Z')));
    expect(file.name).toBe('Mein Spiel');
    expect(file.savedAt).toBe('2026-01-01T00:00:00.000Z');
    expect(file.state).toEqual(s);
  });

  it('beschädigte Daten werden abgelehnt', () => {
    expect(() => deserialize('{}')).toThrow();
    expect(() => deserialize('{"state":{"version":2}}')).toThrow(/Version/);
    expect(() => deserialize('kein json')).toThrow();
  });

  it('Dateinamen werden bereinigt', () => {
    expect(sanitizeSaveName('../../etc/passwd')).toBe('etcpasswd');
    expect(sanitizeSaveName('   ')).toBe('quicksave');
    expect(sanitizeSaveName('Runde 3 – Anna')).toBe('Runde 3 Anna');
  });
});
