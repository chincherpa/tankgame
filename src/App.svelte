<script lang="ts">
  import { app } from './lib/app.svelte';
  import MainMenu from './ui/MainMenu.svelte';
  import Setup from './ui/Setup.svelte';
  import Battle from './ui/Battle.svelte';
  import LoadMenu from './ui/LoadMenu.svelte';
  import Help from './ui/Help.svelte';
</script>

<svelte:document oncontextmenu={(e) => e.preventDefault()} />

{#if app.screen === 'menu'}
  <MainMenu />
{:else if app.screen === 'setup'}
  <Setup />
{:else if app.screen === 'battle'}
  <Battle />
{:else if app.screen === 'load'}
  <LoadMenu />
{:else if app.screen === 'help'}
  <Help />
{/if}

{#if app.toast}
  <div class="toast {app.toast.kind}" role="status">{app.toast.text}</div>
{/if}

<style>
  .toast {
    position: fixed;
    top: 1rem;
    left: 50%;
    transform: translateX(-50%);
    background: #1d2b20;
    border: 1px solid var(--ok);
    padding: 0.7rem 1.2rem;
    border-radius: 10px;
    z-index: 100;
    animation: pop 0.2s ease-out;
  }
  .toast.error { background: #2b1d1d; border-color: var(--danger); }
  @keyframes pop { from { opacity: 0; transform: translate(-50%, -10px); } }
</style>
