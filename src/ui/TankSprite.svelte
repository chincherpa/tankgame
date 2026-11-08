<script lang="ts">
  interface Props {
    color: string;
    flip?: boolean;
    destroyed?: boolean;
    firing?: boolean;
    size?: number;
  }
  let { color, flip = false, destroyed = false, firing = false, size = 120 }: Props = $props();
</script>

<svg
  class:flip
  class:destroyed
  class:firing
  width={size}
  height={size * 0.62}
  viewBox="0 0 200 124"
  aria-hidden="true"
>
  <g class="body">
    <g class="barrel">
      <rect x="112" y="30" width="78" height="12" rx="4" fill="#9fb3c8" />
      {#if firing}
        <circle class="flash" cx="194" cy="36" r="13" fill="#ffd54f" />
      {/if}
    </g>
    <path d="M62 22 h52 a18 18 0 0 1 18 18 v14 h-88 v-14 a18 18 0 0 1 18 -18z" fill={color} />
    <path d="M62 22 h52 a18 18 0 0 1 18 18 v4 h-88 v-4 a18 18 0 0 1 18 -18z" fill="rgba(255,255,255,0.18)" />
    <rect x="18" y="50" width="164" height="38" rx="14" fill={color} />
    <rect x="18" y="50" width="164" height="38" rx="14" fill="rgba(0,0,0,0.25)" />
    <rect x="10" y="82" width="180" height="34" rx="17" fill="#2b3340" />
    {#each [32, 66, 100, 134, 168] as cx}
      <circle {cx} cy="99" r="11" fill="#7b8a9c" />
      <circle {cx} cy="99" r="4" fill="#2b3340" />
    {/each}
  </g>
</svg>

<style>
  svg { display: block; overflow: visible; transition: filter 0.4s, opacity 0.4s; }
  .flip { transform: scaleX(-1); }
  .destroyed { filter: grayscale(1) brightness(0.45); opacity: 0.7; }
  .destroyed .barrel { transform: rotate(18deg); transform-origin: 112px 36px; }
  .firing .body { animation: recoil 0.25s ease-out; }
  .flash { animation: flash 0.25s ease-out forwards; }
  @keyframes recoil { 30% { transform: translateX(-6px); } }
  @keyframes flash { from { opacity: 1; r: 16; } to { opacity: 0; r: 4; } }
</style>
