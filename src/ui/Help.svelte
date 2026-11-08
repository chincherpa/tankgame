<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { ITEMS, PRESET_TANKS, SETTINGS, dodgeChanceFor } from '../engine';
</script>

<main>
  <header>
    <button class="btn" onclick={() => app.go('menu')}>← Zurück</button>
    <h2>Anleitung</h2>
  </header>

  <div class="content panel">
    <section>
      <h3>Ziel</h3>
      <p>Zerstöre alle gegnerischen Panzer. Wer zuletzt noch fährt, gewinnt.</p>
    </section>

    <section>
      <h3>Dein Zug – alles per Maus</h3>
      <ul>
        <li><b>Schießen:</b> Klicke direkt auf einen gegnerischen Panzer – oder auf „Schießen“ und dann aufs Ziel. Rechtsklick bricht das Zielen ab.</li>
        <li><b>Shop:</b> Ausrüstung kaufen. Ein Kauf beendet deinen Zug, Schließen ohne Kauf nicht.</li>
        <li><b>Warten:</b> +{SETTINGS.waitReward} Credit.</li>
        <li>Ein Klick während einer Animation spult sie vor.</li>
        <li>Tastatur optional: <kbd>S</kbd> Schießen, <kbd>B</kbd> Shop, <kbd>N</kbd> Warten, <kbd>Esc</kbd> Abbrechen.</li>
      </ul>
    </section>

    <section>
      <h3>Ablauf eines Schusses</h3>
      <ol>
        <li>Fehlfunktion? (Start {SETTINGS.probabilityOfMalfunction} %) → Zug verfällt, keine Munition verbraucht.</li>
        <li>Fehlschuss? ({SETTINGS.probabilityToMiss} %) → Munition weg.</li>
        <li>Ausweichen des Ziels? (abhängig vom Gewicht, siehe unten)</li>
        <li>Treffer: Schaden = Feuerkraft × (100 − Schadensreduktion) %, mindestens {SETTINGS.minDamage}.
          Das Ziel verliert 1 % Schadensreduktion und bekommt +1 % Fehlfunktion.</li>
      </ol>
      <p>Treffer bringen +{SETTINGS.hitReward} Credit, eine Zerstörung zusätzlich +{SETTINGS.killReward} Credits.</p>
    </section>

    <section>
      <h3>Panzer</h3>
      <table>
        <thead><tr><th>Typ</th><th>Panzerung</th><th>Munition</th><th>Feuerkraft</th><th>Schadensred.</th><th>Ausweichen</th></tr></thead>
        <tbody>
          {#each PRESET_TANKS as t}
            <tr>
              <td>{t.name}</td><td>{t.stats.armor}</td><td>{t.stats.ammo}</td><td>{t.stats.power}</td>
              <td>{t.stats.dmgMitigation} %</td><td>{dodgeChanceFor(t.stats.armor)} %</td>
            </tr>
          {/each}
        </tbody>
      </table>
      <p class="muted">Leichtere Panzer weichen häufiger aus: +2 % je 3 Punkte Start-Panzerung unter {SETTINGS.heavyArmor}.</p>
    </section>

    <section>
      <h3>Shop</h3>
      <table>
        <thead><tr><th>Artikel</th><th>Wirkung</th><th>Preis</th></tr></thead>
        <tbody>
          {#each ITEMS as i}
            <tr><td>{i.name}</td><td>{i.description}</td><td>{i.price} 💰</td></tr>
          {/each}
        </tbody>
      </table>
    </section>
  </div>
</main>

<style>
  main { height: 100%; display: flex; flex-direction: column; padding: 1.5rem 2rem; gap: 1rem; }
  header { display: flex; align-items: center; gap: 1rem; }
  h2 { margin: 0; }
  .content { overflow-y: auto; padding: 1rem 2rem 2rem; max-width: 900px; width: 100%; align-self: center; }
  h3 { color: var(--accent); margin-bottom: 0.4rem; }
  li { margin: 0.3rem 0; }
  table { border-collapse: collapse; width: 100%; margin: 0.5rem 0; }
  th, td { text-align: left; padding: 0.35rem 0.6rem; border-bottom: 1px solid var(--line); }
  th { color: var(--muted); font-weight: 600; }
  kbd { border: 1px solid var(--line); border-radius: 4px; padding: 0 0.35rem; font-family: inherit; }
</style>
