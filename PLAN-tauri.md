# Plan: Tankgame als Tauri-2-App mit Mausbedienung

## 1. Ausgangslage

- Rundenbasiertes Terminal-Spiel (Python, `rich`), ca. 1.300 Zeilen in `src/`, 47 Tests.
- **Kernproblem für die Portierung:** Spiellogik und I/O sind verwoben:
  - `Tank.fire_at()` / `hit()` / `check_malfunction()` rufen direkt `ui.animate_*` und `sleep()` auf.
  - `Game`, `Shop` und `main` blockieren auf `input()` (Eingaben über Tastaturbuchstaben `[S]`, `[B]`, `[N]` …).
  - `save_system` schreibt nach `./saves/` relativ zum Quellcode.
- `run.py` und `tank.py` im Root sind Legacy-Duplikate; werden nicht portiert.

Eine GUI braucht dagegen eine **zustandsbasierte, nicht-blockierende Engine**: Aktion rein → neuer Zustand + Liste von Ereignissen raus. Die UI spielt die Ereignisse als Animation ab.

## 2. Architekturentscheidung

**Empfehlung: Spiellogik in TypeScript im Frontend, Rust nur als dünne Schicht (Fenster, Speicherstände).**

| Option | Bewertung |
|---|---|
| **A) TS-Engine im Frontend** (empfohlen) | Kleine, synchrone Logik ohne Performance-Anforderung; kein IPC pro Klick; Engine auch im Browser testbar (`pnpm dev` ohne Rust-Build); Syntax/Denkweise für Python-Entwickler am nächsten. |
| B) Engine in Rust (`#[tauri::command]`) | Saubere Trennung, `cargo test`, aber jeder Klick = IPC-Roundtrip und doppelte Typdefinitionen (Rust ↔ TS, z. B. via `specta`). Lohnt erst bei Online-Multiplayer/Anti-Cheat. |
| C) Python als Sidecar (PyInstaller) | Bestehender Code bleibt, aber blockierende `input()`-Logik müsste trotzdem komplett umgebaut werden; +30–60 MB Binary, Plattform-Builds mühsam. Nicht empfohlen. |

**Stack:**
- Tauri 2 (`create-tauri-app`, Template `vanilla-ts` oder `svelte-ts`)
- Frontend: **Svelte 5 + TypeScript + Vite** (wenig Boilerplate, reaktiver Store passt gut zum Spielzustand). Alternativ Vanilla-TS, falls keine Framework-Abhängigkeit gewünscht.
- Tests: **Vitest** (Engine), optional Playwright für UI-Smoke-Test.
- Persistenz: `@tauri-apps/plugin-fs` im `AppData`-Verzeichnis (oder `plugin-store`), Rust-seitig keine eigene Logik nötig.

## 3. Zielstruktur

```
tankgame/
├── python/                 # bisheriger Code (src/, tests/, run.py …) – Referenz, später löschbar
├── src/                    # Frontend (Vite)
│   ├── engine/             # reine Spiellogik, KEIN DOM, KEIN Tauri-Import
│   │   ├── config.ts       # ← src/config.py
│   │   ├── tank.ts         # ← src/tank.py (ohne ui/sleep)
│   │   ├── shop.ts         # ← src/shop.py (buy() ohne print)
│   │   ├── game.ts         # ← src/game.py als Reducer
│   │   ├── ai.ts           # Computer-Zug
│   │   ├── rng.ts          # injizierbarer, seedbarer Zufall
│   │   └── events.ts       # Ereignistypen
│   ├── persistence/save.ts # ← save_system.py via plugin-fs
│   ├── ui/                 # Svelte-Komponenten (Screens, Panzer-Karten, Shop …)
│   └── main.ts
├── tests/engine/*.test.ts  # ← tests/test_*.py portiert
├── src-tauri/              # Rust-Shell (tauri.conf.json, capabilities, icons)
└── package.json
```

## 4. Engine-Design (Kern der Arbeit)

```ts
type Action =
  | { type: 'shoot'; targetId?: string }
  | { type: 'buy'; itemId: string }
  | { type: 'wait' };

type GameEvent =
  | { type: 'shot'; from: string; to: string }
  | { type: 'miss' } | { type: 'dodge'; who: string }
  | { type: 'hit'; who: string; damage: number }
  | { type: 'malfunction'; who: string }
  | { type: 'explode'; who: string }
  | { type: 'bought'; who: string; itemId: string }
  | { type: 'waited'; who: string }
  | { type: 'gameOver'; winner: string | null };

function applyAction(state: GameState, action: Action, rng: Rng): { state: GameState; events: GameEvent[] };
function computerAction(state: GameState): Action;   // KI wählt nur eine Action
function validActions(state: GameState): {...};       // steuert enabled/disabled der Buttons
```

- **Immutabel** (`structuredClone` oder Immer) → einfaches Undo/Debug, triviales Speichern (State = JSON).
- `GameState` ist 1:1 serialisierbar; ersetzt `to_dict`/`from_dict`. Feld `version` für Save-Migration.
- Spieler bekommen ein Flag `isComputer` statt der Namensprüfung `name == 'Computer'` (aktueller Bug: ein Mensch namens „Computer“ wird von der KI gesteuert).
- `get_opponent_tank()` ist bei >2 Spielern unklar definiert → in der GUI immer explizites Ziel per Klick, bei genau einem lebenden Gegner automatisch.
- Shop-Kauf zählt wie bisher als Zug; „Shop öffnen und abbrechen“ kostet keinen Zug (wie heute).

## 5. Mausbedienung (UX)

Grundsatz: **Alles per Klick erreichbar, keine Texteingabe außer Spielernamen.** Tastaturkürzel (S/B/N, Esc) bleiben als optionale Zweitbedienung.

| Screen | Bedienung |
|---|---|
| **Hauptmenü** | Große Buttons: *Gegen Computer*, *Mehrspieler*, *Laden*, *Anleitung*, *Beenden*. |
| **Setup** | Spielerzahl per Stepper (2–8) bzw. Chips; Name-Feld mit Vorbelegung; Panzerwahl als **4 klickbare Karten** mit Stat-Balken + Karte *Eigener Panzer*. |
| **Eigener Panzer** | Pro Attribut `–`/`+`-Buttons (und Mausrad über der Zeile), Restpunkte-Anzeige, *Zufällig*, *Fertig* (erst aktiv bei 0 Restpunkten). Ersetzt die sequentielle Abfrage. |
| **Spielfeld** | Panzer-Karten mit Panzerungsbalken, Munition, Credits; aktiver Spieler hervorgehoben. Aktionsleiste: **Schießen**, **Shop**, **Warten (+1 Credit)**. |
| **Zielen** | Bei >1 Gegner: *Schießen* klicken → gegnerische Karten pulsieren → **Klick auf Ziel-Panzer** feuert; Rechtsklick/Esc bricht ab. Alternativ direkt auf Gegner klicken = Schießen auf ihn. |
| **Shop** | Modal mit Item-Karten; nicht leistbare Items ausgegraut mit Tooltip „fehlen X Credits“. Kein Munition-Popup mehr: *Schießen* ist bei 0 Munition deaktiviert, Tooltip verweist auf Shop. |
| **Hover-Infos** | Tooltip auf Panzer zeigt Detailwerte (Miss-, Fehlfunktions-, Ausweich-Chance, Schadensreduktion). |
| **Animationen** | Event-Queue abspielen: Geschoss-Flug, Treffer-Zahl, „Daneben“, „Ausgewichen“, Explosion; Klick überspringt die laufende Animation. Eingaben während Animation gesperrt. |
| **Computerzug** | Automatisch nach kurzer Verzögerung, sichtbar animiert. |
| **Spielende** | Siegerbanner + Statistiktabelle; Buttons *Revanche*, *Hauptmenü*. |
| **Speichern/Laden** | Menü-Button im Spiel → Dialog mit vorgeschlagenem Namen; Ladeliste mit Datum/Modus, Löschen per Papierkorb-Icon mit Bestätigung. |

Optik: Canvas ist nicht nötig, DOM + CSS-Animationen reichen für ein rundenbasiertes Spiel. Panzer als eigene SVG-Grafiken.

## 6. Tauri-spezifisches

- `tauri.conf.json`: Fenster ca. 1280×800, `minWidth`/`minHeight`, Titel, Icons (`tauri icon`).
- **Capabilities** (Tauri-2-Rechtesystem) minimal halten: nur `fs` auf `$APPDATA/saves/**` lesen/schreiben/löschen, `core:default`. Keine Shell-, keine Netzwerk-Rechte.
- Speicherpfad: `appDataDir()/saves/*.json` statt Projektordner.
- Kein eigener Rust-Code nötig außer `main.rs`/`lib.rs` aus dem Template plus Plugin-Registrierung.
- Kontextmenü/Textauswahl im Spiel per CSS (`user-select: none`) unterbinden.

## 7. Umsetzungsschritte

| # | Schritt | Ergebnis / Abnahme |
|---|---|---|
| 1 | Python-Code nach `python/` verschieben, Tauri-2-Projekt anlegen (`pnpm create tauri-app`, Svelte-TS), CI-fähiges `pnpm build` | Leeres Fenster startet via `pnpm tauri dev` |
| 2 | `engine/config.ts`, `rng.ts` (seedbar, z. B. mulberry32), Typen | Kompiliert, Typen vollständig |
| 3 | `tank.ts`, `shop.ts`, `game.ts` als reine Funktionen; KI in `ai.ts` | Keine DOM-/Tauri-Imports in `engine/` (per ESLint-Regel erzwungen) |
| 4 | Python-Tests nach Vitest portieren (47 Tests), mit festem Seed statt `random`-Mocks | `pnpm test` grün; Verhalten deckungsgleich mit Python |
| 5 | UI-Gerüst: Screen-Router (Menü → Setup → Spiel → Ende), Svelte-Store um `applyAction` | Komplette Partie ohne Animationen per Maus spielbar |
| 6 | Panzer-Auswahl + Punkteverteilung mit Steppern | Eigener Panzer per Maus erstellbar |
| 7 | Shop-Modal, Zielauswahl per Klick, deaktivierte Buttons + Tooltips | Keine ungültige Aktion auslösbar |
| 8 | Event-Animationen + Computerzug-Timing, Überspringen per Klick | Partie fühlt sich „lebendig“ an |
| 9 | Speichern/Laden/Löschen über `plugin-fs`, Capabilities eingeschränkt | Spielstand übersteht Neustart |
| 10 | Anleitung-Screen, Icons, Feinschliff, optional Sounds | — |
| 11 | Release-Build: `pnpm tauri build` lokal; optional GitHub Action mit `tauri-apps/tauri-action` für Windows/macOS/Linux | Installer (.msi/.dmg/.AppImage/.deb) |
| 12 | README aktualisieren; `python/` entfernen oder als `legacy`-Branch archivieren | — |

Grobe Aufwandsschätzung: Schritte 1–5 ca. 1–2 Tage, 6–9 ca. 2–3 Tage, Rest nach Anspruch an Optik.

## 8. Entscheidungen (getroffen)

1. **Frontend:** Svelte 5 + TypeScript.
2. **Python-Version:** eingefroren unter `python/`, wird nicht weiter gepflegt.
3. **Regeln:** nachgebessert (siehe unten).
4. **Mehrspieler:** nur am selben Rechner (Hotseat) – Engine bleibt in TypeScript.

### Regeländerungen gegenüber der Python-Version

| Bereich | Python | Neu | Grund |
|---|---|---|---|
| KI-Erkennung | Name == „Computer“ | Flag `isComputer` je Platz | Bug; außerdem beliebige Mischung Mensch/KI |
| Zielwahl | „nächster Spieler“, auch zerstörte | Klick auf lebenden Gegner | Bug bei >2 Spielern |
| Startspieler | immer Spieler 1 | ausgelost | Vorteil für den ersten Zug |
| Ausweichen | 5 % für alle | 5 % + 2 % je 3 Punkte Start-Panzerung unter 120 (Schwer 5 %, Mittel 11 %, Leicht 21 %, Ultraleicht 31 %) | Schwerer Panzer gewann 95 % gegen Ultraleicht |
| Munition +2 | 3 Credits | 4 Credits | Munition soll knapp sein, sonst zählt der Munitionsvorrat leichter Panzer nicht |
| Reparatur | −1 % Fehlfunktion | −3 % | −1 % war wertlos (jeder Treffer +1 %) |
| Abschuss | – | +3 Credits Bonus | Anreiz im Mehrspieler |
| Mindestschaden | 0 möglich | 1 | |
| KI | schießt immer, sonst warten | kauft Munition wenn leer, repariert ab 30 % Fehlfunktion, zielt auf den schnellsten Abschuss | |
| Schießen ohne Munition | Rückfrage „Im Shop kaufen?“ | Button deaktiviert + Tooltip | |

Balance-Messung (KI gegen KI, je 1 500 Partien, Siegquote Zeile gegen Spalte), nach den Änderungen:

|  | Schwer | Mittel | Leicht | Ultral. |
|---|---|---|---|---|
| **Schwer** | 48 % | 40 % | 64 % | 70 % |
| **Mittel** | 61 % | 52 % | 63 % | 67 % |
| **Leicht** | 36 % | 37 % | 50 % | 58 % |
| **Ultraleicht** | 32 % | 34 % | 43 % | 50 % |

Vorher lagen die Extreme bei 5 %/95 %.
Bekannte Schwäche (aus dem Original übernommen): Bei eigenen Panzern ist 1 Punkt Feuerkraft deutlich mehr wert als 5 Panzerung – „Glaskanonen“ sind stark. Kandidat für eine spätere Runde.

## Umsetzungsstand

| # | Schritt | Status |
|---|---|---|
| 1 | Python nach `python/`, Tauri-2-/Svelte-Projekt | ✅ |
| 2–3 | Engine (`src/engine/`) als reine Funktionen, KI | ✅ |
| 4 | Tests portiert + erweitert (Vitest, 46 Tests) | ✅ |
| 5–8 | UI: Menü, Aufstellung, Panzer-Baukasten, Kampf mit Klick-Zielen, Shop, Animationen, Spielende | ✅ |
| 9 | Speichern/Laden/Löschen über `plugin-fs`, Rechte auf `$APPDATA/saves` beschränkt | ✅ |
| 10 | Anleitung, Icons | ✅ (Sounds offen) |
| 11 | CI (`ci.yml`) und Release-Workflow (`release.yml`, Tag `v*`) | ✅ angelegt, noch nicht auf GitHub gelaufen |
| 12 | README | ✅ |

## 9. Voraussetzungen für die Entwicklung

- Node.js ≥ 20, pnpm ≥ 10, Rust (stable, via `rustup`)
- Linux: `libwebkit2gtk-4.1-dev`, `build-essential`, `libssl-dev`, `libayatana-appindicator3-dev`, `librsvg2-dev`
- Windows: WebView2 (bei Win10/11 vorinstalliert), MSVC Build Tools
- macOS: Xcode Command Line Tools
