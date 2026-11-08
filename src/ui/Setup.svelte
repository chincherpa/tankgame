<script lang="ts">
  import { app } from '../lib/app.svelte';
  import {
    EMPTY_ALLOCATION,
    MAX_PLAYERS,
    MIN_PLAYERS,
    PRESET_TANKS,
    TANK_COLORS,
    defaultRng,
    dodgeChanceFor,
    randomAllocation,
    statsFromPoints,
    type PlayerSetup,
    type PointAllocation,
    type TankStats,
  } from '../engine';
  import TankBuilder from './TankBuilder.svelte';
  import TankSprite from './TankSprite.svelte';

  type Choice = string; // Preset-id | 'custom' | 'random'

  interface Draft {
    key: number;
    name: string;
    isComputer: boolean;
    choice: Choice;
    points: PointAllocation;
  }

  let keySeq = 0;
  const draft = (name: string, isComputer: boolean, choice: Choice = 'middle'): Draft => ({
    key: keySeq++,
    name,
    isComputer,
    choice,
    points: { ...EMPTY_ALLOCATION },
  });

  let players = $state<Draft[]>(
    app.setupMode === 'pvc'
      ? [draft('Spieler', false), draft('Computer', true, 'random')]
      : [draft('Spieler 1', false), draft('Spieler 2', false)],
  );
  let editing = $state<number | null>(null);

  const colorOf = (i: number) => TANK_COLORS[i % TANK_COLORS.length]!;

  function preview(d: Draft): TankStats | null {
    if (d.choice === 'random') return null;
    if (d.choice === 'custom') return statsFromPoints(d.points);
    return PRESET_TANKS.find((p) => p.id === d.choice)!.stats;
  }

  function addPlayer() {
    if (players.length >= MAX_PLAYERS) return;
    const computer = app.setupMode === 'pvc';
    players.push(
      draft(computer ? `Computer ${players.length}` : `Spieler ${players.length + 1}`, computer, computer ? 'random' : 'middle'),
    );
  }

  function toggleComputer(d: Draft, isComputer: boolean) {
    d.isComputer = isComputer;
    if (isComputer && /^Spieler( \d+)?$/.test(d.name)) d.name = 'Computer';
    if (!isComputer && /^Computer( \d+)?$/.test(d.name)) d.name = 'Spieler';
  }

  const humans = $derived(players.filter((p) => !p.isComputer).length);
  const startHint = $derived(
    humans === 0 ? 'Mindestens ein menschlicher Spieler wird benötigt' : null,
  );

  function start() {
    if (startHint) return;
    const setups: PlayerSetup[] = players.map((d) => ({
      name: d.name,
      isComputer: d.isComputer,
      stats: preview(d) ?? statsFromPoints(randomAllocation(defaultRng)),
    }));
    app.startGame(players.some((p) => p.isComputer) ? 'pvc' : 'pvp', setups);
  }
</script>

<main>
  <header>
    <button class="btn" onclick={() => app.go('menu')}>← Menü</button>
    <h2>{app.setupMode === 'pvc' ? 'Gegen Computer' : 'Mehrspieler'} – Aufstellung</h2>
    <span style="flex:1"></span>
    <span data-tip={startHint}>
      <button class="btn primary big" disabled={!!startHint} onclick={start}>Spiel starten ▶</button>
    </span>
  </header>

  <div class="grid">
    {#each players as d, i (d.key)}
      {@const stats = preview(d)}
      <section class="card panel" style:--c={colorOf(i)}>
        <div class="top">
          <TankSprite color={colorOf(i)} size={96} />
          <div class="ident">
            <input type="text" bind:value={d.name} maxlength="20" placeholder="Name" aria-label="Name" />
            <div class="seg" role="radiogroup" aria-label="Steuerung">
              <button class:active={!d.isComputer} onclick={() => toggleComputer(d, false)}>👤 Mensch</button>
              <button class:active={d.isComputer} onclick={() => toggleComputer(d, true)}>🤖 Computer</button>
            </div>
          </div>
          {#if players.length > MIN_PLAYERS}
            <button class="btn ghost remove" onclick={() => players.splice(i, 1)} aria-label="Spieler entfernen" data-tip="Entfernen">✕</button>
          {/if}
        </div>

        <div class="choices">
          {#each PRESET_TANKS as p}
            <button class="choice" class:active={d.choice === p.id} onclick={() => (d.choice = p.id)}>
              {p.name.replace(' Panzer', '')}
            </button>
          {/each}
          <button
            class="choice"
            class:active={d.choice === 'custom'}
            onclick={() => {
              d.choice = 'custom';
              editing = d.key;
            }}>✏️ Eigener …</button>
          <button class="choice" class:active={d.choice === 'random'} onclick={() => (d.choice = 'random')}>🎲 Zufall</button>
        </div>

        <div class="stats">
          {#if stats}
            <div><span class="muted">Panzerung</span><b>{stats.armor}</b></div>
            <div><span class="muted">Munition</span><b>{stats.ammo}</b></div>
            <div><span class="muted">Feuerkraft</span><b>{stats.power}</b></div>
            <div><span class="muted">Schadensred.</span><b>{stats.dmgMitigation} %</b></div>
            <div><span class="muted">Ausweichen</span><b>{dodgeChanceFor(stats.armor)} %</b></div>
          {:else}
            <p class="muted">Werte werden beim Start zufällig verteilt.</p>
          {/if}
        </div>
      </section>
    {/each}

    {#if players.length < MAX_PLAYERS}
      <button class="add panel" onclick={addPlayer}>
        <span>＋</span>
        {app.setupMode === 'pvc' ? 'Weiteren Gegner hinzufügen' : 'Spieler hinzufügen'}
      </button>
    {/if}
  </div>
</main>

{#if editing !== null}
  {@const idx = players.findIndex((p) => p.key === editing)}
  {@const d = players[idx]}
  {#if d}
    <TankBuilder
      name={d.name}
      color={colorOf(idx)}
      initial={d.points}
      onapply={(p) => {
        d.points = p;
        editing = null;
      }}
      oncancel={() => {
        if (d.points === EMPTY_ALLOCATION || Object.values(d.points).every((v) => v === 0)) d.choice = 'middle';
        editing = null;
      }}
    />
  {/if}
{/if}

<style>
  main { height: 100%; display: flex; flex-direction: column; padding: 1.5rem 2rem; gap: 1.2rem; }
  header { display: flex; align-items: center; gap: 1rem; }
  h2 { margin: 0; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 1rem;
    overflow-y: auto;
    padding-bottom: 1rem;
    align-content: start;
  }
  .card { padding: 1rem; display: flex; flex-direction: column; gap: 0.8rem; border-top: 4px solid var(--c); }
  .top { display: flex; gap: 1rem; align-items: center; }
  .ident { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; }
  .remove { align-self: flex-start; padding: 0.3rem 0.55rem; }
  .seg { display: flex; background: var(--bg-2); border-radius: 8px; padding: 3px; border: 1px solid var(--line); }
  .seg button { flex: 1; border: 0; background: transparent; padding: 0.35rem 0.5rem; border-radius: 6px; font-size: 0.9rem; white-space: nowrap; }
  .seg button.active { background: var(--panel-2); box-shadow: inset 0 0 0 1px var(--c); }
  .choices { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.4rem; }
  .choice {
    border: 1px solid var(--line);
    background: var(--bg-2);
    border-radius: 8px;
    padding: 0.45rem 0.3rem;
    font-size: 0.88rem;
  }
  .choice:hover { border-color: #4b6080; }
  .choice.active { border-color: var(--accent); background: #3a3010; color: var(--accent-2); font-weight: 600; }
  .stats { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.3rem; min-height: 46px; }
  .stats div { display: flex; flex-direction: column; align-items: center; font-size: 0.78rem; }
  .stats b { font-size: 1.05rem; }
  .stats p { grid-column: 1 / -1; margin: auto; font-size: 0.88rem; }
  .add {
    min-height: 200px;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.4rem;
    border-style: dashed;
    color: var(--muted);
    background: transparent;
  }
  .add span { font-size: 2.4rem; }
  .add:hover { color: var(--text); border-color: var(--accent); }
</style>
