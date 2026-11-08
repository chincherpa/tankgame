<script lang="ts">
  import { app } from '../lib/app.svelte';
  import type { GameState } from '../engine';
  import TankSprite from './TankSprite.svelte';

  interface Props { state: GameState }
  let { state }: Props = $props();

  const winner = $derived(state.tanks.find((t) => t.id === state.winnerId));
  const ranked = $derived(
    [...state.tanks].sort((a, b) => Number(b.alive) - Number(a.alive) || b.record.damageDealt - a.record.damageDealt),
  );
  const pct = (a: number, b: number) => (b ? `${Math.round((a / b) * 100)} %` : '–');
</script>

<div class="backdrop">
  <div class="box panel">
    {#if winner}
      <TankSprite color={winner.color} size={180} />
      <h1>{winner.isComputer && state.tanks.filter((t) => !t.isComputer).length > 0 ? 'Niederlage' : 'Sieg!'}</h1>
      <p class="sub"><b style:color={winner.color}>{winner.name}</b> gewinnt nach {state.round} Runden.</p>
    {:else}
      <h1>Unentschieden</h1>
    {/if}

    <table>
      <thead>
        <tr><th>Panzer</th><th>Schüsse</th><th>Trefferquote</th><th>Schaden ausgeteilt</th><th>Schaden erlitten</th><th>Ausgewichen</th><th>Fehlfunktionen</th><th>Abschüsse</th></tr>
      </thead>
      <tbody>
        {#each ranked as t}
          <tr class:dead={!t.alive}>
            <td><span class="dot" style:background={t.color}></span>{t.name}</td>
            <td>{t.record.shots}</td>
            <td>{pct(t.record.hitsLanded, t.record.shots)}</td>
            <td>{t.record.damageDealt}</td>
            <td>{t.record.damageTaken}</td>
            <td>{t.record.dodges}</td>
            <td>{t.record.malfunctions}</td>
            <td>{t.record.kills}</td>
          </tr>
        {/each}
      </tbody>
    </table>

    <div class="actions">
      <button class="btn primary big" onclick={() => app.rematch()}>🔁 Revanche</button>
      <button class="btn big" onclick={() => app.openSetup(state.mode)}>Neue Aufstellung</button>
      <button class="btn big ghost" onclick={() => app.go('menu')}>Hauptmenü</button>
    </div>
  </div>
</div>

<style>
  .backdrop { position: fixed; inset: 0; background: rgba(5,8,12,0.78); display: flex; align-items: center; justify-content: center; z-index: 30; animation: fade 0.4s; }
  .box { padding: 2rem 2.5rem; display: flex; flex-direction: column; align-items: center; gap: 0.6rem; max-width: 95vw; animation: rise 0.4s ease-out; }
  h1 { margin: 0.3rem 0 0; font-size: 2.6rem; color: var(--accent); letter-spacing: 0.08em; }
  .sub { margin: 0 0 0.6rem; }
  table { border-collapse: collapse; font-size: 0.92rem; }
  th, td { padding: 0.4rem 0.7rem; border-bottom: 1px solid var(--line); text-align: center; }
  th { color: var(--muted); font-weight: 600; font-size: 0.82rem; }
  td:first-child { text-align: left; font-weight: 600; }
  tr.dead td { opacity: 0.6; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 0.5rem; }
  .actions { display: flex; gap: 0.8rem; margin-top: 1rem; }
  @keyframes fade { from { opacity: 0; } }
  @keyframes rise { from { transform: translateY(20px) scale(0.97); opacity: 0; } }
</style>
