# 🎮 Tankgame

Rundenbasiertes Panzer-Kampfspiel als Desktop-App (Tauri 2 + Svelte 5), komplett mit der Maus bedienbar.

## Features

- **Gegen Computer** oder **Mehrspieler am selben Rechner** (2–8 Panzer, jeder Platz Mensch oder KI)
- Vordefinierte Panzer oder **eigener Panzer** per +/−-Punkteverteilung
- **Zielen per Klick** auf den gegnerischen Panzer, animierte Schüsse, Treffer und Explosionen
- **Shop** für Panzerung, Munition und Reparatur
- **Speichern/Laden/Löschen** von Spielständen
- Tastatur optional: `S` Schießen, `B` Shop, `N` Warten, `Esc` Abbrechen

## Entwicklung

Voraussetzungen: Node.js ≥ 20, [pnpm](https://pnpm.io) ≥ 10 (z. B. via `corepack enable`), Rust (stable) und die
[Tauri-Systemabhängigkeiten](https://v2.tauri.app/start/prerequisites/)
(Linux: `libwebkit2gtk-4.1-dev build-essential libssl-dev libayatana-appindicator3-dev librsvg2-dev`).

```bash
pnpm install
pnpm tauri dev     # App mit Hot-Reload starten
pnpm dev           # nur Frontend im Browser (Spielstände dann im localStorage)
pnpm test          # Engine-Tests (Vitest)
pnpm check         # Typprüfung (svelte-check)
pnpm tauri build   # Installer bauen (.msi/.dmg/.AppImage/.deb …)
```

## Spielregeln

| Aktion | Wirkung |
|---|---|
| **Schießen** | Fehlfunktion? → Zug verfällt (keine Munition verbraucht). Sonst −1 Munition, dann Fehlschuss-Wurf, dann Ausweich-Wurf des Ziels. Treffer: Schaden = Feuerkraft × (100 − Schadensreduktion) %, mind. 1; das Ziel verliert 1 % Schadensreduktion und erhält +1 % Fehlfunktion. |
| **Shop** | Kauf beendet den Zug; Schließen ohne Kauf nicht. |
| **Warten** | +1 Credit |

Credits: +1 pro Treffer, +3 Abschussbonus. Der Startspieler wird ausgelost.

| Panzer | Panzerung | Munition | Feuerkraft | Schadensred. | Ausweichen |
|---|---|---|---|---|---|
| Schwer | 120 | 7 | 15 | 13 % | 5 % |
| Mittel | 110 | 9 | 14 | 11 % | 11 % |
| Leicht | 95 | 11 | 12 | 9 % | 21 % |
| Ultraleicht | 80 | 15 | 10 | 7 % | 31 % |

Ausweichchance: 5 % + 2 % je 3 Punkte Start-Panzerung unter 120.

| Shop-Artikel | Effekt | Preis |
|---|---|---|
| Panzerung +10 | +10 Panzerung | 3 |
| Panzerung +20 | +20 Panzerung | 5 |
| Munition +2 | +2 Munition | 4 |
| Reparatur | −3 % Fehlfunktion | 2 |

Alle Werte stehen in `src/engine/config.ts`.

## Spielstände

Gespeichert wird über den Button „💾 Speichern“ im Spiel. Die Spielstände liegen als JSON-Dateien im App-Datenordner (`$APPDATA/saves/`), in der Browser-Vorschau (`pnpm dev`) im localStorage des Browsers.

## Ältere Terminal-Version (Python)

Die ursprüngliche Terminal-Version liegt unverändert unter `python/` und wird nicht mehr gepflegt. Sie hat ein eigenes Regelwerk, das von der App abweicht (z. B. Erkennung des Computers über den Namen, Munitionspreis 3).

```bash
cd python
pip install -r requirements.txt
python -m src.main
```

## Projektstruktur

```
src/
├── engine/        # reine Spiellogik (kein DOM, kein Tauri) – vollständig getestet
│   ├── config.ts  # Werte, Panzer, Shop
│   ├── game.ts    # createGame / applyAction / validateAction
│   ├── tank.ts    # Schussauflösung, Punkteverteilung
│   ├── ai.ts      # Computergegner
│   └── save.ts    # (De-)Serialisierung
├── lib/           # App-Zustand, Animationssteuerung, Dateizugriff
└── ui/            # Svelte-Komponenten
src-tauri/         # Rust-Shell, Fenster, Berechtigungen (nur $APPDATA/saves)
tests/engine/      # Vitest
python/            # ursprüngliche Terminal-Version (eingefroren, nicht mehr gepflegt)
PLAN-tauri.md      # Portierungsplan und getroffene Entscheidungen
```

## Lizenz

MIT – siehe [LICENSE](LICENSE).
