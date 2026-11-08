<script lang="ts">
  import { untrack } from 'svelte';
  import {
    ATTRIBUTE_FACTORS,
    BASE_STATS,
    CUSTOM_TANK_POINTS,
    STAT_LABELS,
    allocatedPoints,
    defaultRng,
    dodgeChanceFor,
    randomAllocation,
    statsFromPoints,
    EMPTY_ALLOCATION,
    type PointAllocation,
    type StatKey,
  } from '../engine';
  import Modal from './Modal.svelte';
  import TankSprite from './TankSprite.svelte';

  interface Props {
    name: string;
    color: string;
    initial: PointAllocation;
    onapply: (p: PointAllocation) => void;
    oncancel: () => void;
  }
  let { name, color, initial, onapply, oncancel }: Props = $props();

  let points = $state<PointAllocation>(untrack(() => ({ ...initial })));
  const left = $derived(CUSTOM_TANK_POINTS - allocatedPoints(points));
  const stats = $derived(statsFromPoints(points));
  const keys: StatKey[] = ['armor', 'ammo', 'power', 'dmgMitigation'];

  function change(key: StatKey, delta: number) {
    const next = points[key] + delta;
    if (next < 0 || (delta > 0 && left < delta)) return;
    points[key] = next;
  }

  function wheel(e: WheelEvent, key: StatKey) {
    e.preventDefault();
    change(key, e.deltaY < 0 ? 1 : -1);
  }
</script>

<Modal title="Eigener Panzer – {name}" onclose={oncancel}>
  <div class="layout">
    <div class="preview">
      <TankSprite {color} size={170} />
      <div class="points" class:done={left === 0}>
        <span class="num">{left}</span>
        <span class="muted">Punkte übrig</span>
      </div>
      <div class="dodge muted">Ausweichchance: <b>{dodgeChanceFor(stats.armor)} %</b></div>
    </div>

    <div class="rows">
      {#each keys as key}
        <div class="row" onwheel={(e) => wheel(e, key)} role="group" aria-label={STAT_LABELS[key]}>
          <div class="label">
            <b>{STAT_LABELS[key]}</b>
            <span class="muted">+{ATTRIBUTE_FACTORS[key]} pro Punkt</span>
          </div>
          <button class="step" onclick={() => change(key, -1)} disabled={points[key] === 0} aria-label="weniger">−</button>
          <div class="value">
            <span class="stat">{stats[key]}</span>
            <span class="pips">
              {#each { length: CUSTOM_TANK_POINTS } as _, i}
                <i class:on={i < points[key]}></i>
              {/each}
            </span>
          </div>
          <button class="step" onclick={() => change(key, 1)} disabled={left === 0} aria-label="mehr">+</button>
        </div>
      {/each}
      <p class="muted hint">Tipp: Mausrad über einer Zeile verteilt ebenfalls Punkte. Basiswerte: {BASE_STATS.armor} / {BASE_STATS.ammo} / {BASE_STATS.power} / {BASE_STATS.dmgMitigation}</p>
    </div>
  </div>

  {#snippet footer()}
    <button class="btn" onclick={() => (points = { ...EMPTY_ALLOCATION })}>Zurücksetzen</button>
    <button class="btn" onclick={() => (points = randomAllocation(defaultRng))}>🎲 Zufällig</button>
    <span style="flex: 1"></span>
    <button class="btn ghost" onclick={oncancel}>Abbrechen</button>
    <span data-tip={left > 0 ? `Noch ${left} Punkte verteilen` : null}>
      <button class="btn primary" disabled={left > 0} onclick={() => onapply({ ...points })}>Übernehmen</button>
    </span>
  {/snippet}
</Modal>

<style>
  .layout { display: flex; gap: 2rem; align-items: center; }
  .preview { display: flex; flex-direction: column; align-items: center; gap: 0.8rem; min-width: 190px; }
  .points { display: flex; flex-direction: column; align-items: center; }
  .points .num { font-size: 2.6rem; font-weight: 800; color: var(--accent); line-height: 1; }
  .points.done .num { color: var(--ok); }
  .rows { display: flex; flex-direction: column; gap: 0.6rem; flex: 1; }
  .row {
    display: grid;
    grid-template-columns: 1fr auto 170px auto;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.7rem;
    border-radius: 10px;
    background: var(--bg-2);
  }
  .label { display: flex; flex-direction: column; font-size: 0.95rem; }
  .label .muted { font-size: 0.78rem; }
  .step {
    width: 38px; height: 38px;
    border-radius: 50%;
    border: 1px solid var(--line);
    background: var(--panel-2);
    font-size: 1.3rem; font-weight: 700;
  }
  .step:hover:not(:disabled) { background: var(--accent); color: #1b1300; }
  .step:disabled { opacity: 0.3; }
  .value { display: flex; flex-direction: column; align-items: center; gap: 4px; }
  .stat { font-size: 1.3rem; font-weight: 700; }
  .pips { display: flex; gap: 2px; }
  .pips i { width: 6px; height: 6px; border-radius: 2px; background: #2c3a4c; }
  .pips i.on { background: var(--accent); }
  .hint { font-size: 0.8rem; margin: 0.2rem 0 0; }
</style>
