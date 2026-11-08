import { describe, expect, it } from 'vitest';
import { ITEMS, applyAction, getItem, validateAction } from '../../src/engine';
import { game, seeded, tank } from './helpers';

const withCredits = (credits: number) => {
  const a = tank('a');
  a.credits = credits;
  return game([a, tank('b')]);
};

describe('Shop', () => {
  it('hat Artikel mit allen Feldern', () => {
    expect(ITEMS.length).toBeGreaterThan(0);
    for (const i of ITEMS) {
      expect(i.price).toBeGreaterThan(0);
      expect(i.value).toBeGreaterThan(0);
      expect(['armor', 'ammo', 'malfunction']).toContain(i.attribute);
    }
    expect(new Set(ITEMS.map((i) => i.id)).size).toBe(ITEMS.length);
  });

  it.each([
    ['armor10', 'armor', 110],
    ['armor20', 'armor', 120],
    ['ammo2', 'ammo', 12],
  ] as const)('%s erhöht %s', (itemId, key, expected) => {
    const { state } = applyAction(withCredits(10), { type: 'buy', itemId }, seeded());
    expect(state.tanks[0]![key]).toBe(expected);
    expect(state.tanks[0]!.credits).toBe(10 - getItem(itemId)!.price);
  });

  it('Reparatur senkt Fehlfunktion um 3, nicht unter 0', () => {
    const s = withCredits(10);
    const { state } = applyAction(s, { type: 'buy', itemId: 'repair' }, seeded());
    expect(state.tanks[0]!.malfunction).toBe(s.tanks[0]!.malfunction - 3);

    s.tanks[0]!.malfunction = 1;
    expect(applyAction(s, { type: 'buy', itemId: 'repair' }, seeded()).state.tanks[0]!.malfunction).toBe(0);
  });

  it('zu wenig Credits wird abgelehnt', () => {
    expect(validateAction(withCredits(2), { type: 'buy', itemId: 'armor20' })).toMatch(/Credits/);
    expect(() => applyAction(withCredits(2), { type: 'buy', itemId: 'armor20' }, seeded())).toThrow();
  });

  it('unbekannter Artikel wird abgelehnt', () => {
    expect(validateAction(withCredits(99), { type: 'buy', itemId: 'nope' })).toMatch(/existiert nicht/);
  });

  it('Kauf beendet den Zug', () => {
    const { state, events } = applyAction(withCredits(10), { type: 'buy', itemId: 'ammo2' }, seeded());
    expect(state.currentIndex).toBe(1);
    expect(events.map((e) => e.type)).toEqual(['bought', 'turnStart']);
  });
});
