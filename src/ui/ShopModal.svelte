<script lang="ts">
  import { ITEMS, canAfford, type Tank } from '../engine';
  import Modal from './Modal.svelte';

  interface Props { tank: Tank; onbuy: (itemId: string) => void; onclose: () => void }
  let { tank, onbuy, onclose }: Props = $props();

  const icons: Record<string, string> = { armor: '🛡️', ammo: '💣', malfunction: '🔧' };
</script>

<Modal title="Shop – {tank.name}" {onclose} width="680px">
  <p class="credits">Guthaben: <b>{tank.credits} 💰</b> <span class="muted">· Ein Kauf beendet deinen Zug.</span></p>
  <div class="items">
    {#each ITEMS as item}
      {@const ok = canAfford(tank, item)}
      <span data-tip={ok ? null : `Es fehl${item.price - tank.credits === 1 ? "t 1 Credit" : `en ${item.price - tank.credits} Credits`}`}>
        <button class="item" disabled={!ok} onclick={() => onbuy(item.id)}>
          <span class="icon">{icons[item.attribute]}</span>
          <b>{item.name}</b>
          <span class="muted desc">{item.description}</span>
          <span class="price" class:no={!ok}>{item.price} 💰</span>
        </button>
      </span>
    {/each}
  </div>
  {#snippet footer()}
    <span style="flex:1"></span>
    <button class="btn" onclick={onclose}>Schließen (Zug geht weiter)</button>
  {/snippet}
</Modal>

<style>
  .credits { margin: 0 0 1rem; }
  .items { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.8rem; }
  .items > span { display: block; }
  .item {
    width: 100%;
    display: grid;
    grid-template-columns: auto 1fr auto;
    grid-template-rows: auto auto;
    column-gap: 0.8rem;
    align-items: center;
    text-align: left;
    padding: 0.9rem 1rem;
    border-radius: 10px;
    border: 1px solid var(--line);
    background: var(--bg-2);
    transition: border-color 0.15s, transform 0.08s, background 0.15s;
  }
  .item:hover:not(:disabled) { border-color: var(--accent); background: #2a2614; }
  .item:active:not(:disabled) { transform: scale(0.98); }
  .item:disabled { opacity: 0.45; }
  .icon { grid-row: 1 / 3; font-size: 1.9rem; }
  .desc { grid-column: 2; font-size: 0.85rem; }
  .price { grid-row: 1 / 3; grid-column: 3; font-weight: 700; color: var(--accent-2); }
  .price.no { color: var(--danger); }
</style>
