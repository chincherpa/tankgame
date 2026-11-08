<script lang="ts">
  import { untrack } from 'svelte';
  import { saveExists, saveGame } from '../lib/persistence';
  import { app } from '../lib/app.svelte';
  import type { GameState } from '../engine';
  import Modal from './Modal.svelte';

  interface Props { game: GameState; onclose: () => void; onsaved?: () => void }
  let { game, onclose, onsaved }: Props = $props();

  let name = $state(untrack(() => `${game.tanks.map((t) => t.name).join(' vs ')} R${game.round}`.slice(0, 40)));
  let confirmOverwrite = $state(false);
  let saving = $state(false);

  async function save() {
    saving = true;
    try {
      if (!confirmOverwrite && (await saveExists(name))) {
        confirmOverwrite = true;
        return;
      }
      const saved = await saveGame(name, game);
      app.showToast(`Gespeichert als „${saved}“`, 'info');
      onsaved?.();
      onclose();
    } catch (e) {
      app.showToast(`Speichern fehlgeschlagen: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      saving = false;
    }
  }
</script>

<Modal title="Spiel speichern" {onclose} width="480px">
  <label>
    <span class="muted">Name des Spielstands</span>
    <!-- svelte-ignore a11y_autofocus -->
    <input type="text" bind:value={name} maxlength="40" autofocus oninput={() => (confirmOverwrite = false)}
      onkeydown={(e) => e.key === 'Enter' && save()} />
  </label>
  {#if confirmOverwrite}
    <p class="warn">Ein Spielstand mit diesem Namen existiert bereits. Überschreiben?</p>
  {/if}
  {#snippet footer()}
    <span style="flex:1"></span>
    <button class="btn ghost" onclick={onclose}>Abbrechen</button>
    <button class="btn primary" class:danger={confirmOverwrite} disabled={saving} onclick={save}>
      {confirmOverwrite ? 'Überschreiben' : '💾 Speichern'}
    </button>
  {/snippet}
</Modal>

<style>
  label { display: flex; flex-direction: column; gap: 0.4rem; }
  .warn { color: var(--accent); margin: 0.8rem 0 0; }
</style>
