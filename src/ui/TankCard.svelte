<script lang="ts">
  import { armorPercent, type Tank } from '../engine';
  import type { Fx } from '../lib/app.svelte';
  import StatBar from './StatBar.svelte';
  import TankSprite from './TankSprite.svelte';

  interface Props {
    tank: Tank;
    flip: boolean;
    isCurrent: boolean;
    targetable: boolean;
    aiming: boolean;
    shaking: boolean;
    exploding: boolean;
    firing: boolean;
    fx: Fx[];
    onshoot: () => void;
    el?: HTMLElement;
  }
  let { tank, flip, isCurrent, targetable, aiming, shaking, exploding, firing, fx, onshoot, el = $bindable() }: Props =
    $props();

  const tip = $derived(
    [
      `Panzerung: ${tank.armor} / ${tank.armorStart} (${armorPercent(tank)} %)`,
      `Feuerkraft: ${tank.power}`,
      `Schadensreduktion: ${tank.dmgMitigation} %`,
      `Fehlschuss-Chance: ${tank.miss} %`,
      `Fehlfunktions-Chance: ${tank.malfunction} %`,
      `Ausweich-Chance: ${tank.dodgeChance} %`,
      targetable ? '\n🎯 Klicken zum Schießen' : '',
    ]
      .filter(Boolean)
      .join('\n'),
  );
</script>

<button
  bind:this={el}
  class="card"
  class:current={isCurrent}
  class:targetable
  class:aiming={aiming && targetable}
  class:shake={shaking}
  class:dead={!tank.alive}
  class:flip
  style:--c={tank.color}
  onclick={() => targetable && onshoot()}
  aria-label="{tank.name}{targetable ? ' – anvisieren' : ''}"
  tabindex={targetable ? 0 : -1}
>
  <div class="head">
    <span class="dot"></span>
    <span class="name">{tank.name}</span>
    {#if tank.isComputer}<span class="tag">KI</span>{/if}
    {#if isCurrent}<span class="tag turn">am Zug</span>{/if}
  </div>

  <div class="sprite" data-tip={tip} data-tip-pos="below">
    <TankSprite color={tank.color} {flip} destroyed={!tank.alive} {firing} size={150} />
    {#if exploding}
      <div class="boom"><span></span><span></span><span></span></div>
    {/if}
    {#if aiming && targetable}
      <div class="crosshair">⌖</div>
    {/if}
    {#each fx as f (f.id)}
      <div class="fx {f.kind}">{f.text}</div>
    {/each}
  </div>

  {#if tank.alive}
    <StatBar value={tank.armor} max={Math.max(tank.armorStart, tank.armor)} label="Panzerung" />
    <div class="nums">
      <span title="Panzerung">🛡️ {tank.armor}</span>
      <span title="Munition" class:empty={tank.ammo === 0}>💣 {tank.ammo}</span>
      <span title="Credits">💰 {tank.credits}</span>
      <span title="Fehlfunktion" class:warn={tank.malfunction >= 25}>⚙️ {tank.malfunction} %</span>
    </div>
  {:else}
    <div class="destroyed">ZERSTÖRT</div>
  {/if}
</button>

<style>
  .card {
    all: unset;
    box-sizing: border-box;
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    padding: 0.7rem 0.9rem 0.8rem;
    background: var(--panel);
    border: 2px solid var(--line);
    border-radius: var(--radius);
    min-width: 220px;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s, opacity 0.3s;
    cursor: default;
  }
  .card.current { border-color: var(--c); box-shadow: 0 0 0 3px color-mix(in srgb, var(--c) 30%, transparent), 0 0 30px color-mix(in srgb, var(--c) 25%, transparent); }
  .card.targetable { cursor: crosshair; }
  .card.targetable:hover { border-color: var(--danger); transform: translateY(-2px); }
  .card.aiming { animation: pulse 1s ease-in-out infinite; border-color: var(--danger); }
  .card.dead { opacity: 0.55; }
  .card.shake { animation: shake 0.45s; }

  .head { display: flex; align-items: center; gap: 0.45rem; }
  .dot { width: 12px; height: 12px; border-radius: 50%; background: var(--c); flex: none; }
  .name { font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .tag { font-size: 0.7rem; padding: 0.05rem 0.4rem; border-radius: 4px; background: var(--panel-2); color: var(--muted); }
  .tag.turn { background: var(--c); color: #111; font-weight: 700; margin-left: auto; }

  .sprite { position: relative; display: flex; justify-content: center; padding: 0.3rem 0; }

  .nums { display: flex; justify-content: space-between; font-size: 0.9rem; gap: 0.4rem; }
  .nums .empty { color: var(--danger); font-weight: 700; }
  .nums .warn { color: var(--accent); }
  .destroyed { text-align: center; font-weight: 800; letter-spacing: 0.3em; color: var(--danger); padding: 0.3rem 0; }

  .crosshair {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 4rem; color: var(--danger);
    pointer-events: none;
    animation: spin 2.5s linear infinite;
    text-shadow: 0 0 10px rgba(0,0,0,0.8);
  }

  .fx {
    position: absolute;
    left: 50%; top: 22%;
    transform: translateX(-50%);
    font-weight: 900;
    font-size: 1.6rem;
    white-space: nowrap;
    pointer-events: none;
    text-shadow: 0 2px 0 #000, 0 0 12px rgba(0,0,0,0.8);
    animation: float 1.3s ease-out forwards;
    z-index: 5;
  }
  .fx.damage { color: #ff6b6b; font-size: 2.2rem; }
  .fx.miss { color: #cfd8dc; }
  .fx.dodge { color: var(--info); }
  .fx.malfunction { color: var(--accent); }
  .fx.credits { color: #ffe082; font-size: 1.1rem; top: 45%; }
  .fx.shop { color: var(--ok); }
  .fx.wait { color: var(--muted); }

  .boom { position: absolute; inset: 0; pointer-events: none; }
  .boom span {
    position: absolute; left: 50%; top: 50%;
    width: 40px; height: 40px; margin: -20px;
    border-radius: 50%;
    background: radial-gradient(circle, #fff7c2 0%, #ffb300 35%, #e53935 65%, transparent 70%);
    animation: boom 0.9s ease-out forwards;
  }
  .boom span:nth-child(2) { animation-delay: 0.15s; left: 35%; top: 40%; }
  .boom span:nth-child(3) { animation-delay: 0.3s; left: 65%; top: 60%; }

  @keyframes float { 0% { opacity: 0; transform: translate(-50%, 10px) scale(0.7); } 15% { opacity: 1; transform: translate(-50%, 0) scale(1.1); } 100% { opacity: 0; transform: translate(-50%, -40px) scale(1); } }
  @keyframes shake { 0%, 100% { transform: translateX(0); } 20% { transform: translateX(-8px) rotate(-1deg); } 40% { transform: translateX(7px) rotate(1deg); } 60% { transform: translateX(-5px); } 80% { transform: translateX(3px); } }
  @keyframes pulse { 50% { box-shadow: 0 0 0 4px rgba(239, 83, 80, 0.45); } }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes boom { 0% { transform: scale(0.2); opacity: 1; } 100% { transform: scale(4.5); opacity: 0; } }
</style>
