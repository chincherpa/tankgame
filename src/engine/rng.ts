/** Zufallsquelle: liefert Zahlen in [0, 1). Injizierbar, damit Tests deterministisch sind. */
export type Rng = () => number;

/** Kleiner, seedbarer PRNG (mulberry32). */
export function mulberry32(seed: number): Rng {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const defaultRng: Rng = Math.random;

/** Ganzzahl in [min, max] (inklusive), entspricht random.randint. */
export function randInt(rng: Rng, min: number, max: number): number {
  return min + Math.floor(rng() * (max - min + 1));
}

/** Wurf 1–100; Erfolg, wenn ≤ chance. */
export function chance(rng: Rng, percent: number): boolean {
  return randInt(rng, 1, 100) <= percent;
}

/** Feste Abfolge von Werten – für Tests. */
export function sequenceRng(values: number[]): Rng {
  let i = 0;
  return () => {
    if (i >= values.length) throw new Error('sequenceRng erschöpft');
    return values[i++]!;
  };
}
