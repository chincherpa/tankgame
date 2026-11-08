/**
 * Panzer-Erzeugung und Kampfregeln. Portiert aus python/src/tank.py –
 * ohne UI-Aufrufe: alle Funktionen mutieren nur die übergebenen Objekte
 * (die Engine arbeitet auf einer Kopie des Zustands) und melden Ereignisse.
 */
import {
  ATTRIBUTE_FACTORS,
  BASE_STATS,
  CUSTOM_TANK_POINTS,
  SETTINGS,
  type StatKey,
  type TankStats,
} from './config';
import { chance, randInt, type Rng } from './rng';
import type { GameEvent, Tank } from './types';

/** Ausweichchance aus der Start-Panzerung: leichte Panzer sind wendiger. */
export function dodgeChanceFor(armorStart: number): number {
  const bonus = Math.floor(Math.max(0, SETTINGS.heavyArmor - armorStart) / SETTINGS.dodgeArmorStep);
  return SETTINGS.baseDodgeChance + bonus;
}

export function createTank(id: string, name: string, stats: TankStats, isComputer: boolean, color: string): Tank {
  return {
    id,
    name,
    isComputer,
    color,
    armor: stats.armor,
    armorStart: stats.armor,
    ammo: stats.ammo,
    power: stats.power,
    dmgMitigation: stats.dmgMitigation,
    miss: SETTINGS.probabilityToMiss,
    malfunction: SETTINGS.probabilityOfMalfunction,
    dodgeChance: dodgeChanceFor(stats.armor),
    credits: SETTINGS.startCredits,
    alive: true,
    record: {
      shots: 0,
      hitsTaken: 0,
      hitsLanded: 0,
      misses: 0,
      dodges: 0,
      malfunctions: 0,
      damageTaken: 0,
      damageDealt: 0,
      kills: 0,
    },
  };
}

export function armorPercent(tank: Tank): number {
  return Math.round((tank.armor / tank.armorStart) * 100);
}

export function calcDamage(power: number, dmgMitigation: number): number {
  const mitigation = Math.min(100, Math.max(0, dmgMitigation));
  return Math.max(SETTINGS.minDamage, Math.floor((power * (100 - mitigation)) / 100));
}

export type PointAllocation = Record<StatKey, number>;

export const EMPTY_ALLOCATION: PointAllocation = { armor: 0, ammo: 0, power: 0, dmgMitigation: 0 };

export function allocatedPoints(points: PointAllocation): number {
  return points.armor + points.ammo + points.power + points.dmgMitigation;
}

export function statsFromPoints(points: PointAllocation): TankStats {
  const total = allocatedPoints(points);
  if (Object.values(points).some((p) => p < 0 || !Number.isInteger(p)) || total > CUSTOM_TANK_POINTS) {
    throw new Error(`Ungültige Punkteverteilung (${total}/${CUSTOM_TANK_POINTS})`);
  }
  return {
    armor: BASE_STATS.armor + points.armor * ATTRIBUTE_FACTORS.armor,
    ammo: BASE_STATS.ammo + points.ammo * ATTRIBUTE_FACTORS.ammo,
    power: BASE_STATS.power + points.power * ATTRIBUTE_FACTORS.power,
    dmgMitigation: BASE_STATS.dmgMitigation + points.dmgMitigation * ATTRIBUTE_FACTORS.dmgMitigation,
  };
}

/** Verteilt alle Punkte zufällig (entspricht get_4_randoms). */
export function randomAllocation(rng: Rng, total = CUSTOM_TANK_POINTS): PointAllocation {
  const keys: StatKey[] = ['armor', 'ammo', 'power', 'dmgMitigation'];
  const points: PointAllocation = { ...EMPTY_ALLOCATION };
  for (let i = 0; i < total; i++) {
    points[keys[randInt(rng, 0, 3)]!] += 1;
  }
  return points;
}

/** Schuss von `attacker` auf `target`. Setzt voraus, dass der Zug gültig ist. */
export function resolveShot(attacker: Tank, target: Tank, rng: Rng, events: GameEvent[]): void {
  if (chance(rng, attacker.malfunction)) {
    attacker.record.malfunctions += 1;
    events.push({ type: 'malfunction', tankId: attacker.id });
    return;
  }

  attacker.ammo -= 1;
  attacker.record.shots += 1;
  events.push({ type: 'shot', from: attacker.id, to: target.id });

  if (chance(rng, attacker.miss)) {
    attacker.record.misses += 1;
    events.push({ type: 'miss', from: attacker.id, to: target.id });
    return;
  }

  if (chance(rng, target.dodgeChance)) {
    target.record.dodges += 1;
    events.push({ type: 'dodge', from: attacker.id, to: target.id });
    return;
  }

  const damage = calcDamage(attacker.power, target.dmgMitigation);
  target.armor = Math.max(0, target.armor - damage);
  target.dmgMitigation = Math.max(0, target.dmgMitigation - 1);
  target.malfunction += 1;
  target.record.hitsTaken += 1;
  target.record.damageTaken += damage;
  attacker.record.hitsLanded += 1;
  attacker.record.damageDealt += damage;
  events.push({ type: 'hit', from: attacker.id, to: target.id, damage });

  attacker.credits += SETTINGS.hitReward;
  events.push({ type: 'credits', tankId: attacker.id, amount: SETTINGS.hitReward, reason: 'hit' });

  if (target.armor === 0) {
    target.alive = false;
    attacker.record.kills += 1;
    events.push({ type: 'explode', tankId: target.id, by: attacker.id });
    attacker.credits += SETTINGS.killReward;
    events.push({ type: 'credits', tankId: attacker.id, amount: SETTINGS.killReward, reason: 'kill' });
  }
}
