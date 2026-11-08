<script lang="ts">
  import { tick } from 'svelte';
  import { app } from '../lib/app.svelte';
  import { validTargets } from '../engine';
  import TankCard from './TankCard.svelte';
  import ShopModal from './ShopModal.svelte';
  import SaveDialog from './SaveDialog.svelte';
  import GameOver from './GameOver.svelte';
  import Modal from './Modal.svelte';

  let aiming = $state(false);
  let shopOpen = $state(false);
  let saveOpen = $state(false);
  let leaveOpen = $state(false);
  let leaveAfterSave = false;

  const cards: Record<string, HTMLElement | undefined> = $state({});
  let arena = $state<HTMLElement>();
  let shell = $state<HTMLElement>();
  let logEl = $state<HTMLElement>();

  const view = $derived(app.view!);
  const current = $derived(app.current);
  const targets = $derived(current ? validTargets(view, current.id) : []);
  // Anzeige in Aufstellungsreihenfolge (p1, p2, …) – unabhängig vom ausgelosten Startspieler.
  const ordered = $derived([...view.tanks].sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true })));
  const half = $derived(Math.ceil(ordered.length / 2));
  const left = $derived(ordered.slice(0, half));
  const right = $derived(ordered.slice(half));
  const humanTurn = $derived(app.canAct);
  const dialogOpen = $derived(shopOpen || saveOpen || leaveOpen);

  // Zielmodus endet automatisch, wenn der Mensch nicht mehr am Zug ist.
  $effect(() => {
    if (!humanTurn) aiming = false;
  });

  // Protokoll mitscrollen
  $effect(() => {
    void app.log.length;
    void tick().then(() => logEl?.scrollTo({ top: logEl.scrollHeight, behavior: 'smooth' }));
  });

  // Geschossflug zwischen zwei Karten
  $effect(() => {
    const p = app.projectile;
    if (!p || !shell) return;
    // Start an der Rohrmündung, Ziel Mitte des gegnerischen Panzers
    const fromSvg = cards[p.from]?.querySelector('svg');
    const toSvg = cards[p.to]?.querySelector('svg');
    const a = fromSvg?.getBoundingClientRect();
    const b = toSvg?.getBoundingClientRect();
    const box = shell.getBoundingClientRect();
    if (!a || !b || !fromSvg) return;
    const flipped = fromSvg.classList.contains('flip');
    const dot = document.createElement('div');
    dot.className = 'shell';
    dot.style.background = p.color;
    shell.appendChild(dot);
    const from = { x: a.left + a.width * (flipped ? 0.03 : 0.97) - box.left, y: a.top + a.height * 0.29 - box.top };
    const to = { x: b.left + b.width / 2 - box.left, y: b.top + b.height * 0.5 - box.top };
    const arc = Math.min(160, Math.abs(to.x - from.x) * 0.25 + 40);
    const anim = dot.animate(
      [
        { transform: `translate(${from.x}px, ${from.y}px) scale(0.6)` },
        { transform: `translate(${(from.x + to.x) / 2}px, ${Math.min(from.y, to.y) - arc}px) scale(1.2)`, offset: 0.5 },
        { transform: `translate(${to.x}px, ${to.y}px) scale(0.8)` },
      ],
      { duration: 420, easing: 'linear', fill: 'forwards' },
    );
    return () => {
      anim.cancel();
      dot.remove();
    };
  });

  function shoot(targetId: string) {
    aiming = false;
    void app.act({ type: 'shoot', targetId });
  }

  function onShootButton() {
    if (!current) return;
    if (targets.length === 1) shoot(targets[0]!.id);
    else aiming = !aiming;
  }

  function buy(itemId: string) {
    shopOpen = false;
    void app.act({ type: 'buy', itemId });
  }

  function onKey(e: KeyboardEvent) {
    if (dialogOpen || e.target instanceof HTMLInputElement) return;
    if (e.key === 'Escape') {
      aiming = false;
      return;
    }
    if (!humanTurn || !current) return;
    const k = e.key.toLowerCase();
    if (k === 's' && current.ammo > 0) onShootButton();
    else if (k === 'b') shopOpen = true;
    else if (k === 'n') void app.act({ type: 'wait' });
  }

  function onPointerDown(e: PointerEvent) {
    if (app.busy && e.button === 0) app.skip();
  }

  function leave() {
    leaveOpen = false;
    app.go('menu');
  }

  const shootTip = $derived(
    !current
      ? null
      : current.ammo === 0
        ? 'Keine Munition – im Shop nachkaufen'
        : targets.length > 1
          ? 'Danach ein Ziel anklicken (oder direkt auf einen Gegner klicken)'
          : null,
  );
</script>

<svelte:window onkeydown={onKey} />

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="battle"
  bind:this={shell}
  class:busy={app.busy}
  onpointerdowncapture={onPointerDown}
  oncontextmenu={() => (aiming = false)}
>
  <header>
    <div class="round">Runde <b>{view.round}</b></div>
    {#if current}
      <div class="who" style:--c={current.color}>
        <span class="dot"></span>{current.name}
        {#if current.isComputer}<span class="muted">denkt nach …</span>{/if}
      </div>
    {/if}
    <span style="flex:1"></span>
    <button class="btn" disabled={app.busy || view.finished} onclick={() => (saveOpen = true)}>💾 Speichern</button>
    <button class="btn" onclick={() => (view.finished ? app.go('menu') : (leaveOpen = true))}>☰ Menü</button>
  </header>

  <div class="main">
    <section class="arena" bind:this={arena} class:aiming>
      <div class="side">
        {#each left as t (t.id)}
          <TankCard
            tank={t}
            flip={false}
            isCurrent={current?.id === t.id}
            targetable={humanTurn && targets.some((x) => x.id === t.id) && (current?.ammo ?? 0) > 0}
            {aiming}
            shaking={app.shaking === t.id}
            exploding={app.exploding === t.id}
            firing={app.firing === t.id}
            fx={app.fx.filter((f) => f.tankId === t.id)}
            onshoot={() => shoot(t.id)}
            bind:el={cards[t.id]}
          />
        {/each}
      </div>
      <div class="nomans">
        {#if aiming}<div class="aimhint">🎯 Ziel anklicken<br /><span class="muted">Rechtsklick / Esc: abbrechen</span></div>{/if}
        {#if app.banner}<div class="banner">{app.banner}</div>{/if}
      </div>
      <div class="side">
        {#each right as t (t.id)}
          <TankCard
            tank={t}
            flip={true}
            isCurrent={current?.id === t.id}
            targetable={humanTurn && targets.some((x) => x.id === t.id) && (current?.ammo ?? 0) > 0}
            {aiming}
            shaking={app.shaking === t.id}
            exploding={app.exploding === t.id}
            firing={app.firing === t.id}
            fx={app.fx.filter((f) => f.tankId === t.id)}
            onshoot={() => shoot(t.id)}
            bind:el={cards[t.id]}
          />
        {/each}
      </div>
    </section>

    <aside class="log panel">
      <h3>Gefechtsprotokoll</h3>
      <ol bind:this={logEl}>
        {#each app.log as entry (entry.id)}
          <li class={entry.kind}>{entry.text}</li>
        {/each}
      </ol>
    </aside>
  </div>

  <footer class="actions panel">
    {#if current && !current.isComputer}
      <div class="me" style:--c={current.color}>
        <span class="dot"></span>
        <b>{current.name}</b>
        <span class="muted">💣 {current.ammo} · 💰 {current.credits}</span>
      </div>
      <span data-tip={shootTip}>
        <button class="btn big" class:primary={!aiming} class:danger={aiming} disabled={!humanTurn || current.ammo === 0} onclick={onShootButton}>
          {aiming ? '✕ Zielen abbrechen' : '🎯 Schießen'} <kbd>S</kbd>
        </button>
      </span>
      <button class="btn big" disabled={!humanTurn} onclick={() => (shopOpen = true)}>🛒 Shop <kbd>B</kbd></button>
      <span data-tip="+1 Credit">
        <button class="btn big" disabled={!humanTurn} onclick={() => app.act({ type: 'wait' })}>⏳ Warten <kbd>N</kbd></button>
      </span>
    {:else if current}
      <div class="me muted">🤖 {current.name} ist am Zug …</div>
    {/if}
    {#if app.busy}
      <span class="skip muted">Klick zum Vorspulen ⏩</span>
    {/if}
  </footer>
</div>

{#if shopOpen && current}
  <ShopModal tank={current} onbuy={buy} onclose={() => (shopOpen = false)} />
{/if}

{#if saveOpen && app.state}
  <SaveDialog
    game={app.state}
    onclose={() => (saveOpen = false)}
    onsaved={() => {
      if (leaveAfterSave) leave();
    }}
  />
{/if}

{#if leaveOpen}
  <Modal title="Spiel verlassen?" onclose={() => (leaveOpen = false)} width="460px">
    <p>Nicht gespeicherter Fortschritt geht verloren.</p>
    {#snippet footer()}
      <button class="btn ghost" onclick={() => (leaveOpen = false)}>Weiterspielen</button>
      <span style="flex:1"></span>
      <button class="btn danger" onclick={leave}>Verlassen</button>
      <button
        class="btn primary"
        disabled={app.busy}
        onclick={() => {
          leaveOpen = false;
          leaveAfterSave = true;
          saveOpen = true;
        }}>💾 Speichern & verlassen</button>
    {/snippet}
  </Modal>
{/if}

{#if view.finished && !app.busy}
  <GameOver state={view} />
{/if}

<style>
  .battle { height: 100%; display: flex; flex-direction: column; padding: 1rem 1.2rem; gap: 0.9rem; position: relative; }
  .battle.busy { cursor: progress; }
  header { display: flex; align-items: center; gap: 1rem; }
  .round { font-size: 1.1rem; }
  .round b { color: var(--accent); font-size: 1.3rem; }
  .who { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; padding: 0.3rem 0.8rem; border-radius: 999px; background: var(--panel); border: 1px solid var(--c); }
  .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--c); display: inline-block; }

  .main { flex: 1; display: grid; grid-template-columns: 1fr 300px; gap: 1rem; min-height: 0; }
  .arena {
    display: grid;
    grid-template-columns: minmax(220px, 300px) 1fr minmax(220px, 300px);
    align-items: center;
    gap: 1rem;
    min-height: 0;
    overflow-y: auto;
    padding: 0.5rem;
  }
  .side { display: flex; flex-direction: column; gap: 0.8rem; justify-content: center; }
  .nomans { height: 100%; position: relative; display: flex; align-items: center; justify-content: center; text-align: center;
    background: repeating-linear-gradient(90deg, transparent 0 18px, rgba(255,255,255,0.025) 18px 20px); border-radius: var(--radius); min-width: 120px; }
  .aimhint { font-weight: 700; color: var(--danger); font-size: 1.1rem; }
  .banner {
    position: absolute;
    padding: 1rem 1.6rem;
    background: var(--panel);
    border: 2px solid var(--accent);
    border-radius: 12px;
    font-size: 1.4rem; font-weight: 800;
    animation: pop 0.25s ease-out;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  }

  .log { display: flex; flex-direction: column; min-height: 0; padding: 0.6rem 0.2rem 0.6rem 0.9rem; }
  .log h3 { margin: 0 0 0.4rem; font-size: 0.95rem; color: var(--muted); }
  .log ol { list-style: none; margin: 0; padding: 0 0.6rem 0 0; overflow-y: auto; flex: 1; font-size: 0.88rem; }
  .log li { padding: 0.22rem 0; border-bottom: 1px dashed #2a3646; }
  .log li.turn { color: var(--muted); font-size: 0.8rem; padding-top: 0.5rem; }
  .log li.hit { color: #ff8a80; }
  .log li.explode { color: var(--danger); font-weight: 700; }
  .log li.miss { color: #b0bec5; }
  .log li.dodge { color: var(--info); }
  .log li.malfunction { color: var(--accent); }
  .log li.shop, .log li.credits { color: var(--ok); }
  .log li.end { color: var(--accent); font-weight: 800; }

  .actions { display: flex; align-items: center; gap: 0.8rem; padding: 0.8rem 1rem; min-height: 72px; }
  .me { display: flex; align-items: center; gap: 0.5rem; margin-right: auto; }
  .skip { margin-left: auto; font-size: 0.85rem; }

  :global(.shell) {
    position: absolute; left: -7px; top: -7px;
    width: 14px; height: 14px; border-radius: 50%;
    box-shadow: 0 0 12px 4px rgba(255, 213, 79, 0.8);
    pointer-events: none; z-index: 20;
  }
  @keyframes pop { from { transform: scale(0.85); opacity: 0; } }
</style>
