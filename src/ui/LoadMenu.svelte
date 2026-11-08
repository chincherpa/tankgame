<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { deleteSave, listSaves, loadGame } from '../lib/persistence';
  import type { SaveSummary } from '../engine';
  import Modal from './Modal.svelte';

  let saves = $state<SaveSummary[] | null>(null);
  let error = $state<string | null>(null);
  let toDelete = $state<SaveSummary | null>(null);

  async function refresh() {
    try {
      saves = await listSaves();
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
      saves = [];
    }
  }
  void refresh();

  async function load(s: SaveSummary) {
    try {
      app.loadState(await loadGame(s.name));
    } catch (e) {
      app.showToast(`Laden fehlgeschlagen: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  async function confirmDelete() {
    if (!toDelete) return;
    await deleteSave(toDelete.name);
    toDelete = null;
    await refresh();
  }

  const fmt = (iso: string) => (iso ? new Date(iso).toLocaleString('de-DE', { dateStyle: 'medium', timeStyle: 'short' }) : '–');
</script>

<main>
  <header>
    <button class="btn" onclick={() => app.go('menu')}>← Zurück</button>
    <h2>Spiel laden</h2>
  </header>

  <div class="list panel">
    {#if saves === null}
      <p class="muted">Lade …</p>
    {:else if saves.length === 0}
      <p class="muted empty">{error ?? 'Noch keine Spielstände vorhanden.'}</p>
    {:else}
      {#each saves as s (s.name)}
        <div class="row">
          <button class="open" onclick={() => load(s)}>
            <b>{s.name}</b>
            <span class="muted">{s.players.join(' · ')}</span>
            <span class="meta muted">Runde {s.round} · {s.mode === 'pvc' ? 'mit Computer' : 'Mehrspieler'} · {fmt(s.savedAt)}</span>
          </button>
          <button class="btn ghost del" onclick={() => (toDelete = s)} aria-label="Löschen" data-tip="Löschen">🗑️</button>
        </div>
      {/each}
    {/if}
  </div>
</main>

{#if toDelete}
  <Modal title="Spielstand löschen?" onclose={() => (toDelete = null)} width="440px">
    <p>„{toDelete.name}“ wird endgültig gelöscht.</p>
    {#snippet footer()}
      <span style="flex:1"></span>
      <button class="btn ghost" onclick={() => (toDelete = null)}>Abbrechen</button>
      <button class="btn danger" onclick={confirmDelete}>Löschen</button>
    {/snippet}
  </Modal>
{/if}

<style>
  main { height: 100%; display: flex; flex-direction: column; padding: 1.5rem 2rem; gap: 1rem; }
  header { display: flex; align-items: center; gap: 1rem; }
  h2 { margin: 0; }
  .list { max-width: 820px; width: 100%; align-self: center; padding: 0.6rem; overflow-y: auto; }
  .empty { text-align: center; padding: 2rem; }
  .row { display: flex; align-items: center; gap: 0.4rem; }
  .row + .row { border-top: 1px solid var(--line); }
  .open {
    flex: 1; text-align: left; display: flex; flex-direction: column; gap: 0.15rem;
    border: 0; background: transparent; padding: 0.8rem 1rem; border-radius: 8px;
  }
  .open:hover { background: var(--panel-2); }
  .meta { font-size: 0.82rem; }
  .del { padding: 0.5rem 0.7rem; }
</style>
