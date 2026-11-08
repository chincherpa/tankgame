/**
 * Dateizugriff für Spielstände.
 * In Tauri: $APPDATA/saves/*.json über plugin-fs (Rechte in capabilities/default.json).
 * Im Browser (`pnpm dev` ohne Tauri): Fallback auf localStorage.
 */
import { isTauri } from '@tauri-apps/api/core';
import { BaseDirectory, exists, mkdir, readDir, readTextFile, remove, writeTextFile } from '@tauri-apps/plugin-fs';
import { deserialize, sanitizeSaveName, serialize, summarize, type GameState, type SaveSummary } from '../engine';

const DIR = 'saves';
const LS_PREFIX = 'tankgame:save:';
const opts = { baseDir: BaseDirectory.AppData } as const;

const fileOf = (name: string) => `${DIR}/${sanitizeSaveName(name)}.json`;

async function ensureDir(): Promise<void> {
  if (!(await exists(DIR, opts))) await mkdir(DIR, { ...opts, recursive: true });
}

export async function saveExists(name: string): Promise<boolean> {
  if (!isTauri()) return localStorage.getItem(LS_PREFIX + sanitizeSaveName(name)) !== null;
  return exists(fileOf(name), opts);
}

/** Speichert und liefert den tatsächlich verwendeten (bereinigten) Namen. */
export async function saveGame(name: string, state: GameState): Promise<string> {
  const clean = sanitizeSaveName(name);
  const json = serialize(clean, state);
  if (!isTauri()) {
    localStorage.setItem(LS_PREFIX + clean, json);
    return clean;
  }
  await ensureDir();
  await writeTextFile(fileOf(clean), json, opts);
  return clean;
}

export async function loadGame(name: string): Promise<GameState> {
  const json = isTauri() ? await readTextFile(fileOf(name), opts) : localStorage.getItem(LS_PREFIX + sanitizeSaveName(name));
  if (json === null) throw new Error('Spielstand nicht gefunden');
  return deserialize(json).state;
}

export async function deleteSave(name: string): Promise<void> {
  if (!isTauri()) {
    localStorage.removeItem(LS_PREFIX + sanitizeSaveName(name));
    return;
  }
  if (await exists(fileOf(name), opts)) await remove(fileOf(name), opts);
}

/** Alle lesbaren Spielstände, neueste zuerst. Defekte Dateien werden übersprungen. */
export async function listSaves(): Promise<SaveSummary[]> {
  const jsons: string[] = [];
  if (!isTauri()) {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(LS_PREFIX)) jsons.push(localStorage.getItem(key) ?? '');
    }
  } else {
    if (!(await exists(DIR, opts))) return [];
    for (const entry of await readDir(DIR, opts)) {
      if (!entry.isFile || !entry.name.endsWith('.json')) continue;
      try {
        jsons.push(await readTextFile(`${DIR}/${entry.name}`, opts));
      } catch {
        /* unlesbar – überspringen */
      }
    }
  }
  const out: SaveSummary[] = [];
  for (const json of jsons) {
    try {
      out.push(summarize(deserialize(json)));
    } catch {
      /* defekt – überspringen */
    }
  }
  return out.sort((a, b) => b.savedAt.localeCompare(a.savedAt));
}
