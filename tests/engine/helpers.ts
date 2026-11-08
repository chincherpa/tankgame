import { createTank, mulberry32, sequenceRng, type GameState, type Tank, type TankStats } from '../../src/engine';

export const stats = (armor = 100, ammo = 10, power = 15, dmgMitigation = 10): TankStats => ({ armor, ammo, power, dmgMitigation });

export const tank = (id: string, s: TankStats = stats(), isComputer = false): Tank => createTank(id, `Tank ${id}`, s, isComputer, '#fff');

export function game(tanks: Tank[], currentIndex = 0, mode: GameState['mode'] = 'pvp'): GameState {
  return { version: 1, mode, tanks, currentIndex, round: 1, finished: false, winnerId: null };
}

/** Würfe in Reihenfolge: Fehlfunktion, Fehlschuss, Ausweichen. 0 = Ereignis tritt ein, 0.999 = tritt nicht ein. */
const NO = 0.999;
const YES = 0;
export const rolls = {
  hit: () => sequenceRng([NO, NO, NO]),
  malfunction: () => sequenceRng([YES]),
  miss: () => sequenceRng([NO, YES]),
  dodge: () => sequenceRng([NO, NO, YES]),
};

export const seeded = (seed = 42) => mulberry32(seed);
