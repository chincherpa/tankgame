/** (De-)Serialisierung von Spielständen – rein, ohne Dateizugriff. */
import type { GameState } from './types';

export interface SaveFile {
  name: string;
  savedAt: string;
  state: GameState;
}

export interface SaveSummary {
  name: string;
  savedAt: string;
  mode: GameState['mode'];
  players: string[];
  round: number;
}

export function sanitizeSaveName(name: string): string {
  const cleaned = name.trim().replace(/[^\p{L}\p{N} _-]/gu, '').replace(/\s+/g, ' ').slice(0, 40);
  return cleaned || 'quicksave';
}

export function serialize(name: string, state: GameState, now = new Date()): string {
  const file: SaveFile = { name: sanitizeSaveName(name), savedAt: now.toISOString(), state };
  return JSON.stringify(file, null, 2);
}

function isObject(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null;
}

export function deserialize(json: string): SaveFile {
  const data: unknown = JSON.parse(json);
  if (!isObject(data) || !isObject(data.state)) throw new Error('Kein gültiger Spielstand');
  const state = data.state;
  if (state.version !== 1) throw new Error(`Unbekannte Spielstand-Version: ${String(state.version)}`);
  if (!Array.isArray(state.tanks) || state.tanks.length < 2) throw new Error('Spielstand enthält keine Panzer');
  if (typeof state.currentIndex !== 'number' || state.currentIndex < 0 || state.currentIndex >= state.tanks.length) {
    throw new Error('Spielstand ist beschädigt');
  }
  return {
    name: typeof data.name === 'string' ? data.name : 'unbenannt',
    savedAt: typeof data.savedAt === 'string' ? data.savedAt : '',
    state: state as unknown as GameState,
  };
}

export function summarize(file: SaveFile): SaveSummary {
  return {
    name: file.name,
    savedAt: file.savedAt,
    mode: file.state.mode,
    players: file.state.tanks.map((t) => t.name),
    round: file.state.round,
  };
}
