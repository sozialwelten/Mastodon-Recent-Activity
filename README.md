# Mastodon Recent Activity

CLI-Tool zur Anzeige von Aktivitätsstatistiken einer Mastodon-Instanz der letzten 24 Stunden.

## Features

- 📊 Übersicht lokaler Posts und aktiver Accounts
- 🔥 Trending Hashtags (instanzweit)
- 💬 Meistgenutzte Hashtags in lokalen Posts
- 🚀 Top gebooste und favorisierte Beiträge
- 📈 Wöchentliche Instanz-Statistiken

## Installation

```bash
pip install requests
```

## Konfiguration

Empfohlen: Umgebungsvariablen in `~/.bashrc` setzen:

```bash
export MASTODON_INSTANCE="https://deine-instanz.social"
export MASTODON_TOKEN="dein_access_token"
```

### Access Token erstellen

1. Mastodon → **Einstellungen** → **Entwicklung** → **Neue Anwendung**
2. Name vergeben, **Leserechte** aktivieren
3. Token kopieren und in `.bashrc` speichern

## Verwendung

```bash
# Mit Umgebungsvariablen
python MastodonRecentActivity.py

# Mit Argumenten
python MastodonRecentActivity.py https://mastodon.social
python MastodonRecentActivity.py https://mastodon.social --token YOUR_TOKEN

# Hilfe
python MastodonRecentActivity.py --help
```

## Beispielausgabe

```
======================================================================
  🐘 MASTODON AKTIVITÄTSBERICHT - Letzte 24 Stunden
  Instanz: https://ifwo.eu
  Zeitstempel: 2025-12-06 14:23:45
======================================================================

📈 ÜBERSICHT
----------------------------------------------------------------------
  Lokale Posts (letzte 24h): 42
  Aktive Accounts:            12

🔥 TRENDING HASHTAGS (Instanz-weit)
----------------------------------------------------------------------
  1. #Fediverse            (156 Nutzungen)
  2. #Privacy              (89 Nutzungen)
  ...
```

## Lizenz

GPL-3.0

## Autor

Michael Karbacher