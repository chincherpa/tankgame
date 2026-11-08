import type { TankStats } from './config';

export interface TankRecord {
  shots: number;
  hitsTaken: number;
  hitsLanded: number;
  misses: number;
  dodges: number;
  malfunctions: number;
  damageTaken: number;
  damageDealt: number;
  kills: number;
}

export interface Tank {
  id: string;
  name: string;
  isComputer: boolean;
  color: string;
  armor: number;
  armorStart: number;
  ammo: number;
  power: number;
  dmgMitigation: number;
  miss: number;
  malfunction: number;
  dodgeChance: number;
  credits: number;
  alive: boolean;
  record: TankRecord;
}

export type GameMode = 'pvc' | 'pvp';

export interface GameState {
  version: 1;
  mode: GameMode;
  /** Reihenfolge = Zugreihenfolge */
  tanks: Tank[];
  currentIndex: number;
  round: number;
  finished: boolean;
  /** id des Siegers; null = kein Überlebender */
  winnerId: string | null;
}

export interface PlayerSetup {
  name: string;
  isComputer: boolean;
  stats: TankStats;
}

export type Action =
  | { type: 'shoot'; targetId: string }
  | { type: 'buy'; itemId: string }
  | { type: 'wait' };

export type GameEvent =
  | { type: 'turnStart'; tankId: string; round: number }
  | { type: 'malfunction'; tankId: string }
  | { type: 'shot'; from: string; to: string }
  | { type: 'miss'; from: string; to: string }
  | { type: 'dodge'; from: string; to: string }
  | { type: 'hit'; from: string; to: string; damage: number }
  | { type: 'explode'; tankId: string; by: string }
  | { type: 'credits'; tankId: string; amount: number; reason: 'hit' | 'kill' | 'wait' }
  | { type: 'bought'; tankId: string; itemId: string }
  | { type: 'waited'; tankId: string }
  | { type: 'gameOver'; winnerId: string | null };

export interface ActionResult {
  state: GameState;
  events: GameEvent[];
}
