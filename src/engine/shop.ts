import { ITEMS, type ShopItem } from './config';
import type { Tank } from './types';

export function getItem(itemId: string): ShopItem | undefined {
  return ITEMS.find((i) => i.id === itemId);
}

export function canAfford(tank: Tank, item: ShopItem): boolean {
  return tank.credits >= item.price;
}

/** Wendet den Kauf an. Setzt voraus, dass der Kauf gültig ist. */
export function applyPurchase(tank: Tank, item: ShopItem): void {
  tank.credits -= item.price;
  switch (item.attribute) {
    case 'armor':
      tank.armor += item.value;
      break;
    case 'ammo':
      tank.ammo += item.value;
      break;
    case 'malfunction':
      tank.malfunction = Math.max(0, tank.malfunction - item.value);
      break;
  }
}
