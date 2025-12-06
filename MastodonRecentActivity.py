#!/usr/bin/env python3
"""
Mastodon Recent Activity
Zeigt Aktivitätsstatistiken der letzten 24 Stunden einer Mastodon-Instanz an.

Author: Michael Karbacher
License: GPL-3.0
"""

import requests
from datetime import datetime, timedelta
from collections import Counter
import argparse
import sys
import os
from typing import List, Dict, Any


class MastodonActivityMonitor:
    def __init__(self, instance_url: str, access_token: str = None):
        """
        Initialize the monitor.

        Args:
            instance_url: URL der Mastodon-Instanz (z.B. https://mastodon.social)
            access_token: Optional - Access Token für authentifizierte Anfragen
        """
        self.instance_url = instance_url.rstrip('/')
        self.headers = {}
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'

    def get_public_timeline(self, limit: int = 40, local: bool = True) -> List[Dict[Any, Any]]:
        """Holt die öffentliche Timeline."""
        url = f"{self.instance_url}/api/v1/timelines/public"
        params = {'limit': limit, 'local': local}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Fehler beim Abrufen der Timeline: {e}")
            return []

    def get_trending_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Holt die aktuell trendenden Hashtags."""
        url = f"{self.instance_url}/api/v1/trends/tags"
        params = {'limit': limit}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Fehler beim Abrufen der Trending Tags: {e}")
            return []

    def get_instance_activity(self) -> Dict[str, Any]:
        """Holt allgemeine Instanz-Aktivitätsdaten."""
        url = f"{self.instance_url}/api/v1/instance/activity"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Fehler beim Abrufen der Instanz-Aktivität: {e}")
            return []

    def filter_last_24h(self, posts: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        """Filtert Posts der letzten 24 Stunden."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        filtered = []

        for post in posts:
            created_at = datetime.strptime(
                post['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'
            )
            if created_at >= cutoff_time:
                filtered.append(post)

        return filtered

    def analyze_activity(self) -> Dict[str, Any]:
        """Analysiert die Aktivität der letzten 24 Stunden."""
        print("📊 Sammle Daten...\n")

        # Timeline abrufen (mehrere Aufrufe für mehr Daten)
        all_posts = []
        for _ in range(3):  # 3 Seiten à 40 Posts = 120 Posts
            posts = self.get_public_timeline(limit=40, local=True)
            if not posts:
                break
            all_posts.extend(posts)

        # Nur Posts der letzten 24h
        recent_posts = self.filter_last_24h(all_posts)

        # Trending Tags
        trending = self.get_trending_tags(limit=10)

        # Instance Activity
        instance_activity = self.get_instance_activity()

        # Analyse
        unique_accounts = set(post['account']['id'] for post in recent_posts)

        # Top gebooste Posts
        top_boosted = sorted(
            recent_posts,
            key=lambda x: x['reblogs_count'],
            reverse=True
        )[:5]

        # Top favorisierte Posts
        top_faved = sorted(
            recent_posts,
            key=lambda x: x['favourites_count'],
            reverse=True
        )[:5]

        # Hashtag-Analyse aus Posts
        hashtags = []
        for post in recent_posts:
            hashtags.extend([tag['name'] for tag in post['tags']])

        hashtag_counts = Counter(hashtags).most_common(10)

        return {
            'total_posts': len(recent_posts),
            'unique_accounts': len(unique_accounts),
            'trending_tags': trending,
            'top_boosted': top_boosted,
            'top_faved': top_faved,
            'hashtag_counts': hashtag_counts,
            'instance_activity': instance_activity
        }

    @staticmethod
    def strip_html(text: str) -> str:
        """Entfernt HTML-Tags und konvertiert zu Plain Text."""
        import re

        # Hashtags mit # anzeigen
        text = re.sub(r'<a[^>]*class="mention hashtag"[^>]*>#<span>([^<]+)</span></a>', r'#\1', text)

        # Mentions beibehalten
        text = re.sub(r'<span class="h-card">(<a[^>]*>)?@<span>([^<]+)</span>(</a>)?</span>', r'@\2', text)

        # Links vereinfachen (Text oder URL anzeigen)
        text = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', r'\2', text)

        # Zeilenumbrüche
        text = text.replace('<br />', '\n').replace('<br/>', '\n').replace('<br>', '\n')

        # Paragraphen
        text = text.replace('</p><p>', '\n\n').replace('<p>', '').replace('</p>', '')

        # Alle verbleibenden Tags entfernen
        text = re.sub(r'<[^>]+>', '', text)

        # HTML-Entities dekodieren
        import html
        text = html.unescape(text)

        # Mehrfache Leerzeichen/Zeilenumbrüche reduzieren
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)

        return text.strip()

    def display_report(self, data: Dict[str, Any]):
        """Zeigt den Activity Report an."""
        print("=" * 70)
        print(f"  🐘 MASTODON AKTIVITÄTSBERICHT - Letzte 24 Stunden")
        print(f"  Instanz: {self.instance_url}")
        print(f"  Zeitstempel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()

        # Übersicht
        print("📈 ÜBERSICHT")
        print("-" * 70)
        print(f"  Lokale Posts (letzte 24h): {data['total_posts']}")
        print(f"  Aktive Accounts:            {data['unique_accounts']}")
        print()

        # Trending Hashtags (von API)
        if data['trending_tags']:
            print("🔥 TRENDING HASHTAGS (Instanz-weit)")
            print("-" * 70)
            for i, tag in enumerate(data['trending_tags'][:10], 1):
                name = tag['name']
                # Versuche history-Daten zu nutzen
                uses = 'N/A'
                if 'history' in tag and tag['history']:
                    uses = sum(int(h.get('uses', 0)) for h in tag['history'])
                print(f"  {i:2d}. #{name:20s} ({uses} Nutzungen)")
            print()

        # Hashtags aus Timeline
        if data['hashtag_counts']:
            print("💬 HASHTAGS IN LOKALEN POSTS (24h)")
            print("-" * 70)
            for i, (tag, count) in enumerate(data['hashtag_counts'][:10], 1):
                print(f"  {i:2d}. #{tag:20s} ({count}x)")
            print()

        # Top gebooste Posts
        if data['top_boosted']:
            print("🚀 MEIST GEBOOSTE POSTS")
            print("-" * 70)
            for i, post in enumerate(data['top_boosted'], 1):
                username = post['account']['username']
                boosts = post['reblogs_count']
                favs = post['favourites_count']
                content = self.strip_html(post['content'])

                print(f"  {i}. @{username} | 🔁 {boosts} | ⭐ {favs}")

                # Mehrzeiligen Content mit Einrückung anzeigen
                lines = content.split('\n')
                for line in lines:
                    if line.strip():
                        print(f"     {line}")

                print(f"     → {self.instance_url}/@{username}/{post['id']}")
                print()

        # Instanz-Statistik (falls verfügbar)
        if data['instance_activity']:
            print("📊 INSTANZ-AKTIVITÄT (Wöchentlich)")
            print("-" * 70)
            for week in data['instance_activity'][:4]:
                week_date = datetime.fromtimestamp(int(week['week'])).strftime('%Y-%m-%d')
                logins = week['logins']
                statuses = week['statuses']
                registrations = week['registrations']
                print(f"  Woche {week_date}: {statuses} Posts | {logins} Logins | {registrations} neue User")
            print()

        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Mastodon Instance Activity Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s https://mastodon.social
  %(prog)s  # Nutzt $MASTODON_INSTANCE

Umgebungsvariablen (empfohlen):
  export MASTODON_INSTANCE="https://deine-instanz.social"
  export MASTODON_TOKEN="your_token_here"

  In ~/.bashrc/.zshrc speichern, dann einfach:
  %(prog)s

Access Token generieren:
  1. Gehe zu Einstellungen → Entwicklung → Neue Anwendung
  2. Erteile Leserechte (read)
  3. Kopiere den Access Token
  4. Speichere ihn in ~/.bashrc: export MASTODON_TOKEN="..."
        """
    )

    parser.add_argument(
        'instance_url',
        nargs='?',
        help='URL der Mastodon-Instanz (z.B. https://mastodon.social, Standard: $MASTODON_INSTANCE)',
        default=None
    )

    parser.add_argument(
        '--token', '-t',
        help='Access Token für authentifizierte Anfragen (optional, Standard: $MASTODON_TOKEN)',
        default=None
    )

    args = parser.parse_args()

    # Instanz-URL: CLI-Argument > Umgebungsvariable
    instance_url = args.instance_url or os.environ.get('MASTODON_INSTANCE')

    if not instance_url:
        parser.error("Instanz-URL erforderlich: entweder als Argument oder via $MASTODON_INSTANCE")

    # Token-Priorität: CLI-Argument > Umgebungsvariable
    token = args.token or os.environ.get('MASTODON_TOKEN')

    try:
        monitor = MastodonActivityMonitor(instance_url, token)
        data = monitor.analyze_activity()
        monitor.display_report(data)
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()