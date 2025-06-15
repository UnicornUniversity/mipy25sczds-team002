import requests


class ScoreAPI:
    def __init__(self, server_url):
        self.server_url = server_url

    def upload_score(self, player_name, score, date):
        """Odešle skóre na server"""
        try:
            data = {
                "name": player_name,
                "score": score,
                "date": date,
                "game": "deadlock"
            }
            # Upravená URL s /deadlock prefix
            response = requests.post(f"{self.server_url}/deadlock/api/scores",
                                     json=data,
                                     timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Chyba při odesílání skóre: {e}")
            return False

    def download_scores(self, limit=10):
        """Stáhne nejlepší skóre ze serveru"""
        try:
            # Upravená URL s /deadlock prefix
            response = requests.get(f"{self.server_url}/deadlock/api/scores?limit={limit}",
                                    timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Chyba při stahování skóre: {e}")
            return []