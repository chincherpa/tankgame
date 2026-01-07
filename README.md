# 🎮 Tankgame

Ein Terminal-basiertes Panzer-Kampfspiel in Python.

## 🎯 Features

- **PvP-Modus**: 2+ Spieler gegeneinander
- **PvC-Modus**: Gegen den Computer spielen
- **Shop-System**: Rüstung, Munition und Reparaturen kaufen
- **Individuelle Panzer**: Vordefiniert oder selbst konfiguriert
- **Dodging**: Ausweichen von Angriffen
- **Speichern/Laden**: Spielstände sichern

## 📋 Voraussetzungen

- Python 3.8+
- pip

## 🚀 Installation

```bash
# Repository klonen
git clone https://github.com/username/tankgame.git
cd tankgame

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## 🎮 Spielstart

```bash
python -m src.main
```

### Schnellstart (Legacy)
```bash
python run.py
```

## 🕹️ Spielanleitung

### Panzer-Attribute

| Attribut | Beschreibung |
|----------|--------------|
| **Armor** | Panzerung, wird bei Treffern reduziert |
| **Ammo** | Anzahl Munition, -1 pro Schuss |
| **Power** | Schaden pro Schuss |
| **Dmg Mitigation** | Schadensreduktion in %, -1 pro Treffer |
| **Miss** | Fehlschuss-Wahrscheinlichkeit |
| **Malfunction** | Fehlfunktions-Wahrscheinlichkeit |
| **Credits** | Währung für den Shop |

### Vordefinierte Panzer

| Panzer | Armor | Ammo | Power | Dmg Mit. |
|--------|-------|------|-------|----------|
| Heavy Tank | 120 | 7 | 15 | 13 |
| Middle Tank | 110 | 9 | 14 | 11 |
| Light Tank | 95 | 11 | 12 | 9 |
| UltraLight Tank | 80 | 15 | 10 | 7 |

### Aktionen pro Runde

- **[S]hoot**: Auf Gegner schießen
- **[B]uy**: Shop öffnen
- **[N]othing**: Warten (+1 Credit)

### Shop-Items

| Item | Effekt | Preis |
|------|--------|-------|
| Armor+10 | +10 Panzerung | 3 Credits |
| Armor+20 | +20 Panzerung | 5 Credits |
| Ammo+2 | +2 Munition | 3 Credits |
| Repair | -1% Fehlfunktion | 2 Credits |

## 📁 Projektstruktur

```
tankgame/
├── src/
│   ├── __init__.py
│   ├── main.py          # Einstiegspunkt
│   ├── tank.py          # Tank-Klasse
│   ├── game.py          # Spiellogik
│   ├── shop.py          # Shop-System
│   ├── ui.py            # UI-Funktionen
│   ├── config.py        # Einstellungen
│   └── utils.py         # Hilfsfunktionen
├── tests/
│   ├── test_tank.py
│   ├── test_game.py
│   └── test_shop.py
├── saves/               # Spielstände
├── requirements.txt
├── README.md
└── LICENSE
```

## 🧪 Tests

```bash
pytest tests/ -v
```

## 📜 Lizenz

MIT License - siehe [LICENSE](LICENSE)

## 🤝 Beitragen

Pull Requests sind willkommen! Für größere Änderungen bitte zuerst ein Issue eröffnen.
