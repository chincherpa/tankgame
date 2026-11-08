import { describe, expect, it } from 'vitest';
import {
  CUSTOM_TANK_POINTS,
  EMPTY_ALLOCATION,
  SETTINGS,
  allocatedPoints,
  armorPercent,
  calcDamage,
  createTank,
  dodgeChanceFor,
  randomAllocation,
  resolveShot,
  statsFromPoints,
  type GameEvent,
} from '../../src/engine';
import { rolls, seeded, stats, tank } from './helpers';

describe('createTank', () => {
  it('übernimmt Werte und Standardeinstellungen', () => {
    const t = createTank('p1', 'Anna', stats(120, 7, 15, 13), true, '#f00');
    expect(t).toMatchObject({
      id: 'p1', name: 'Anna', isComputer: true, armor: 120, armorStart: 120, ammo: 7, power: 15, dmgMitigation: 13,
      miss: SETTINGS.probabilityToMiss, malfunction: SETTINGS.probabilityOfMalfunction, credits: SETTINGS.startCredits, alive: true,
    });
    expect(Object.values(t.record).every((v) => v === 0)).toBe(true);
  });

  it('Ausweichchance steigt bei leichten Panzern', () => {
    expect(dodgeChanceFor(120)).toBe(5);
    expect(dodgeChanceFor(200)).toBe(5);
    expect(dodgeChanceFor(110)).toBe(11);
    expect(dodgeChanceFor(95)).toBe(21);
    expect(dodgeChanceFor(80)).toBe(31);
  });

  it('armorPercent bezieht sich auf die Start-Panzerung', () => {
    const t = tank('a', stats(80));
    t.armor = 40;
    expect(armorPercent(t)).toBe(50);
  });
});

describe('calcDamage', () => {
  it('ohne Reduktion voller Schaden', () => expect(calcDamage(15, 0)).toBe(15));
  it('mit Reduktion abgerundet', () => expect(calcDamage(15, 10)).toBe(13));
  it('Mindestschaden 1', () => expect(calcDamage(1, 90)).toBe(1));
  it('Reduktion über 100 % wird begrenzt', () => expect(calcDamage(10, 150)).toBe(1));
});

describe('resolveShot', () => {
  it('Treffer: Schaden, Reduktion -1, Fehlfunktion +1, Credits, Statistik', () => {
    const a = tank('a');
    const b = tank('b', stats(100, 10, 15, 10));
    const events: GameEvent[] = [];
    resolveShot(a, b, rolls.hit(), events);
    expect(b.armor).toBe(100 - 13);
    expect(b.dmgMitigation).toBe(9);
    expect(b.malfunction).toBe(SETTINGS.probabilityOfMalfunction + 1);
    expect(b.record).toMatchObject({ hitsTaken: 1, damageTaken: 13 });
    expect(a).toMatchObject({ ammo: 9, credits: SETTINGS.hitReward });
    expect(a.record).toMatchObject({ shots: 1, hitsLanded: 1, damageDealt: 13 });
    expect(events.map((e) => e.type)).toEqual(['shot', 'hit', 'credits']);
  });

  it('Fehlfunktion: kein Schuss, keine Munition verbraucht', () => {
    const a = tank('a');
    const b = tank('b');
    const events: GameEvent[] = [];
    resolveShot(a, b, rolls.malfunction(), events);
    expect(a.ammo).toBe(10);
    expect(a.record.malfunctions).toBe(1);
    expect(b.armor).toBe(100);
    expect(events).toEqual([{ type: 'malfunction', tankId: 'a' }]);
  });

  it('Fehlschuss: Munition weg, kein Schaden', () => {
    const a = tank('a');
    const b = tank('b');
    const events: GameEvent[] = [];
    resolveShot(a, b, rolls.miss(), events);
    expect(a.ammo).toBe(9);
    expect(a.record.misses).toBe(1);
    expect(b.armor).toBe(100);
    expect(events.at(-1)?.type).toBe('miss');
  });

  it('Ausweichen: kein Schaden, Ausweichen gezählt', () => {
    const a = tank('a');
    const b = tank('b');
    const events: GameEvent[] = [];
    resolveShot(a, b, rolls.dodge(), events);
    expect(b.armor).toBe(100);
    expect(b.record.dodges).toBe(1);
    expect(events.at(-1)?.type).toBe('dodge');
  });

  it('Panzerung fällt nicht unter 0, Zerstörung gibt Abschussbonus', () => {
    const a = tank('a', stats(100, 10, 50, 0));
    const b = tank('b', stats(10, 10, 10, 0));
    const events: GameEvent[] = [];
    resolveShot(a, b, rolls.hit(), events);
    expect(b.armor).toBe(0);
    expect(b.alive).toBe(false);
    expect(a.record.kills).toBe(1);
    expect(a.credits).toBe(SETTINGS.hitReward + SETTINGS.killReward);
    expect(events.map((e) => e.type)).toEqual(['shot', 'hit', 'credits', 'explode', 'credits']);
  });

  it('Schadensreduktion fällt nicht unter 0', () => {
    const a = tank('a');
    const b = tank('b', stats(100, 10, 10, 0));
    resolveShot(a, b, rolls.hit(), []);
    expect(b.dmgMitigation).toBe(0);
  });
});

describe('Punkteverteilung', () => {
  it('statsFromPoints wendet die Faktoren an', () => {
    expect(statsFromPoints({ armor: 4, ammo: 3, power: 2, dmgMitigation: 1 })).toEqual({
      armor: 120, ammo: 13, power: 12, dmgMitigation: 11,
    });
  });

  it('zu viele oder negative Punkte werden abgelehnt', () => {
    expect(() => statsFromPoints({ ...EMPTY_ALLOCATION, armor: CUSTOM_TANK_POINTS + 1 })).toThrow();
    expect(() => statsFromPoints({ ...EMPTY_ALLOCATION, ammo: -1 })).toThrow();
  });

  it('randomAllocation verteilt genau alle Punkte und variiert', () => {
    const rng = seeded(1);
    const results = Array.from({ length: 10 }, () => randomAllocation(rng));
    for (const r of results) expect(allocatedPoints(r)).toBe(CUSTOM_TANK_POINTS);
    expect(new Set(results.map((r) => JSON.stringify(r))).size).toBeGreaterThan(1);
  });
});
