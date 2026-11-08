<script lang="ts">
  interface Props { value: number; max: number; color?: string; label?: string }
  let { value, max, color, label }: Props = $props();
  const pct = $derived(Math.max(0, Math.min(100, (value / max) * 100)));
  const auto = $derived(pct > 50 ? 'var(--ok)' : pct > 25 ? 'var(--accent)' : 'var(--danger)');
</script>

<div class="bar" aria-label={label} role="meter" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max}>
  <div class="fill" style:width="{pct}%" style:background={color ?? auto}></div>
</div>

<style>
  .bar { height: 10px; background: #0d1218; border-radius: 5px; overflow: hidden; border: 1px solid #2a3646; }
  .fill { height: 100%; transition: width 0.45s ease-out, background 0.45s; }
</style>
