/**
 * Computer-Gegner. Python-Original: "immer schießen, sonst warten".
 * Neu: kauft Munition, wenn leer; repariert bei hoher Fehlfunktionsrate;
 * zielt auf den Gegner, der am schnellsten zu zerstören ist.
 */
import { ITEMS } from './config';
import { currentTank, validTargets } from './game';
import { calcDamage } from './tank';
import type { Action, GameState, Tank } from './types';

/** Ab dieser Fehlfunktions-Chance (in %) repariert die KI, sofern sie Credits hat. */
export const AI_REPAIR_THRESHOLD = 30;

function shotsToKill(attacker: Tank, target: Tank): number {
  return Math.ceil(target.armor / calcDamage(attacker.power, target.dmgMitigation));
}

export function chooseTarget(state: GameState, attacker: Tank): Tank | undefined {
  const targets = validTargets(state, attacker.id);
  // Am wenigsten Schüsse bis zur Zerstörung; bei Gleichstand Menschen vor Computern, dann gefährlichster.
  return [...targets].sort(
    (a, b) =>
      shotsToKill(attacker, a) - shotsToKill(attacker, b) ||
      Number(a.isComputer) - Number(b.isComputer) ||
      b.power - a.power,
  )[0];
}

export function computerAction(state: GameState): Action {
  const me = currentTank(state);
  const price = (id: string) => ITEMS.find((i) => i.id === id)!.price;

  if (me.ammo <= 0) {
    return me.credits >= price('ammo2') ? { type: 'buy', itemId: 'ammo2' } : { type: 'wait' };
  }

  if (me.malfunction >= AI_REPAIR_THRESHOLD && me.credits >= price('repair')) {
    return { type: 'buy', itemId: 'repair' };
  }

  const target = chooseTarget(state, me);
  return target ? { type: 'shoot', targetId: target.id } : { type: 'wait' };
}
