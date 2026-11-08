<script lang="ts">
  import { getCurrentWindow } from '@tauri-apps/api/window';
  import { isTauri } from '@tauri-apps/api/core';
  import { app } from '../lib/app.svelte';
  import TankSprite from './TankSprite.svelte';

  function quit() {
    if (isTauri()) void getCurrentWindow().close();
    else window.close();
  }
</script>

<main>
  <div class="hero">
    <TankSprite color="#6aa84f" size={220} />
    <h1>TANKGAME</h1>
    <p class="muted">Rundenbasierter Panzerkampf</p>
  </div>

  <nav class="panel">
    <button class="btn primary big" onclick={() => app.openSetup('pvc')}>🤖 Gegen Computer</button>
    <button class="btn big" onclick={() => app.openSetup('pvp')}>👥 Mehrspieler (2–8)</button>
    <button class="btn big" onclick={() => app.go('load')}>📂 Spiel laden</button>
    <button class="btn big" onclick={() => app.go('help')}>📖 Anleitung</button>
    <button class="btn big ghost" onclick={quit}>Beenden</button>
  </nav>
</main>

<style>
  main {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2rem;
  }
  .hero { display: flex; flex-direction: column; align-items: center; }
  h1 {
    margin: 0.6rem 0 0;
    font-size: 3.4rem;
    letter-spacing: 0.35em;
    margin-right: -0.35em;
    color: var(--accent);
    text-shadow: 0 4px 0 #6b4e00;
  }
  p { margin: 0.2rem 0 0; }
  nav {
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
    padding: 1.4rem;
    width: min(360px, 90vw);
  }
</style>
