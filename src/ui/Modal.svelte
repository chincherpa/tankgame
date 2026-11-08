<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    title: string;
    onclose: () => void;
    children: Snippet;
    footer?: Snippet;
    width?: string;
  }
  let { title, onclose, children, footer, width = '760px' }: Props = $props();
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onclose()} />

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="backdrop" onclick={(e) => e.target === e.currentTarget && onclose()} oncontextmenu={onclose}>
  <div class="modal panel" style:width role="dialog" aria-modal="true" aria-label={title}>
    <header>
      <h2>{title}</h2>
      <button class="btn ghost close" onclick={onclose} aria-label="Schließen">✕</button>
    </header>
    <div class="body">{@render children()}</div>
    {#if footer}
      <footer>{@render footer()}</footer>
    {/if}
  </div>
</div>

<style>
  .backdrop {
    position: fixed; inset: 0;
    background: rgba(5, 8, 12, 0.7);
    display: flex; align-items: center; justify-content: center;
    z-index: 40;
    animation: fade 0.15s ease-out;
  }
  .modal { max-width: 94vw; max-height: 92vh; display: flex; flex-direction: column; box-shadow: 0 20px 60px rgba(0,0,0,0.5); animation: rise 0.18s ease-out; }
  header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.2rem 0.4rem; }
  h2 { margin: 0; font-size: 1.3rem; }
  .close { padding: 0.3rem 0.6rem; }
  .body { padding: 0.8rem 1.2rem; overflow-y: auto; }
  footer { display: flex; gap: 0.6rem; align-items: center; padding: 0.8rem 1.2rem 1.1rem; border-top: 1px solid var(--line); }
  @keyframes fade { from { opacity: 0; } }
  @keyframes rise { from { transform: translateY(12px); opacity: 0; } }
</style>
