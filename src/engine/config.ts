/**
 * Spielkonfiguration: Grundwerte, Shop-Artikel, vordefinierte Panzer.
 * Portiert aus python/src/config.py, Regeländerungen siehe RULES.md.
 */

export const SETTINGS = {
  /** Fehlschuss-Wahrscheinlichkeit in % */
  probabilityToMiss: 20,
  /** Start-Fehlfunktions-Wahrscheinlichkeit in % */
  probabilityOfMalfunction: 15,
  startCredits: 0,
  /** Ausweichchance eines Panzers mit maximaler Start-Panzerung (≥ HEAVY_ARMOR) */
  baseDodgeChance: 5,
  /** Start-Panzerung, ab der es keinen Ausweich-Bonus mehr gibt */
  heavyArmor: 120,
  /** Je so viele Punkte Start-Panzerung unter heavyArmor gibt es +1 % Ausweichchance (= +2 % je 3 Punkte) */
  dodgeArmorStep: 1.5,
  /** Credits für einen Treffer */
  hitReward: 1,
  /** Zusätzliche Credits für die Zerstörung eines Panzers */
  killReward: 3,
  /** Credits für "Warten" */
  waitReward: 1,
  /** Mindestschaden eines Treffers */
  minDamage: 1,
} as const;

export interface TankStats {
  armor: number;
  ammo: number;
  power: number;
  dmgMitigation: number;
}

export type StatKey = keyof TankStats;

export const STAT_LABELS: Record<StatKey, string> = {
  armor: 'Panzerung',
  ammo: 'Munition',
  power: 'Feuerkraft',
  dmgMitigation: 'Schadensreduktion',
};

export type ItemAttribute = 'armor' | 'ammo' | 'malfunction';

export interface ShopItem {
  id: string;
  name: string;
  description: string;
  value: number;
  price: number;
  attribute: ItemAttribute;
}

export const ITEMS: readonly ShopItem[] = [
  { id: 'armor10', name: 'Panzerung +10', description: 'Erhöht die Panzerung um 10', value: 10, price: 3, attribute: 'armor' },
  { id: 'armor20', name: 'Panzerung +20', description: 'Erhöht die Panzerung um 20', value: 20, price: 5, attribute: 'armor' },
  { id: 'ammo2', name: 'Munition +2', description: 'Zwei zusätzliche Granaten', value: 2, price: 4, attribute: 'ammo' },
  { id: 'repair', name: 'Reparatur', description: 'Senkt die Fehlfunktions-Chance um 3 %', value: 3, price: 2, attribute: 'malfunction' },
];

export interface PresetTank {
  id: string;
  name: string;
  stats: TankStats;
}

export const PRESET_TANKS: readonly PresetTank[] = [
  { id: 'heavy', name: 'Schwerer Panzer', stats: { armor: 120, ammo: 7, power: 15, dmgMitigation: 13 } },
  { id: 'middle', name: 'Mittlerer Panzer', stats: { armor: 110, ammo: 9, power: 14, dmgMitigation: 11 } },
  { id: 'light', name: 'Leichter Panzer', stats: { armor: 95, ammo: 11, power: 12, dmgMitigation: 9 } },
  { id: 'ultralight', name: 'Ultraleichter Panzer', stats: { armor: 80, ammo: 15, power: 10, dmgMitigation: 7 } },
];

/** Wie viel ein verteilter Punkt bei der Panzer-Konfiguration bringt. */
export const ATTRIBUTE_FACTORS: Record<StatKey, number> = {
  armor: 5,
  ammo: 1,
  power: 1,
  dmgMitigation: 1,
};

export const BASE_STATS: TankStats = { armor: 100, ammo: 10, power: 10, dmgMitigation: 10 };

export const CUSTOM_TANK_POINTS = 20;

export const MIN_PLAYERS = 2;
export const MAX_PLAYERS = 8;

export const TANK_COLORS = ['#4caf50', '#e53935', '#1e88e5', '#fdd835', '#8e24aa', '#fb8c00', '#00acc1', '#d81b60'] as const;
