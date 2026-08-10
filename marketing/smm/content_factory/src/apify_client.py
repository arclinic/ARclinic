import os
import requests
import time
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

APIFY_KEYS = [k.strip() for k in os.getenv("APIFY_KEYS", "").split(",") if k.strip()]

ACTORS = {
    'x': 'curious_coder/twitter-scraper',
    'instagram': 'apify/instagram-profile-scraper',
    'tiktok': 'clockworks/tiktok-scraper'
}

class ApifyClient:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('APIFY_TOKEN')
        self.keys = APIFY_KEYS
        self.current_key_index = 0
        self.base_url = 'https://api.apify.com/v2'
    
    def _get_next_key(self):
        """Переключиться на следующий ключ"""
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        self.token = self.keys[self.current_key_index]
        print(f"🔄 Переключение на следующий Apify ключ (индекс {self.current_key_index})")
    
    def _make_request(self, method, url, **kwargs):
        """Сделать запрос с ротацией ключей при ошибке 401"""
        max_attempts = len(self.keys)
        
        for attempt in range(max_attempts):
            if 'params' not in kwargs:
                kwargs['params'] = {}
            kwargs['params']['token'] = self.token
            
            response = requests.request(method, url, **kwargs)
            
            if response.status_code == 401:
                print(f"⚠️ Ключ {self.token[:20]}... истёк или недействителен")
                self._get_next_key()
                continue
            
            return response
        
        raise Exception("Все Apify ключи исчерпаны или недействительны")
    
    def fetch_posts(self, platform: str, accounts: List[str], max_posts: int = 50) -> List[Dict]:
        if platform not in ACTORS:
            raise ValueError(f"Platform {platform} not supported")
        
        actor_id = ACTORS[platform]
        
        if platform == 'x':
            input_data = {
                "searchTerms": accounts,
                "maxTweets": max_posts,
                "proxyConfig": {"useApifyProxy": True}
            }
        elif platform == 'instagram':
            input_data = {
                "directUrls": [f"https://www.instagram.com/{acc}/" for acc in accounts],
                "resultsType": "posts",
                "resultsLimit": max_posts,
                "proxy": {"useApifyProxy": True}
            }
        elif platform == 'tiktok':
            input_data = {
                "searchQueries": accounts,
                "maxItems": max_posts,
                "proxyConfig": {"useApifyProxy": True}
            }
        else:
            raise ValueError(f"Platform {platform} not supported")
        
        # Запуск актора
        response = self._make_request(
            'POST',
            f'{self.base_url}/acts/{actor_id}/runs',
            json=input_data
        )
        
        if response.status_code == 404:
            raise Exception(f"Apify actor '{actor_id}' not found. Check if actor name is correct.")
        
        response.raise_for_status()
        
        run_data = response.json()
        dataset_id = run_data['data']['defaultDatasetId']
        
        # Ожидание завершения
        status = 'RUNNING'
        while status in ['RUNNING', 'READY']:
            time.sleep(5)
            status_response = self._make_request(
                'GET',
                f'{self.base_url}/acts/{actor_id}/runs/{run_data["data"]["id"]}'
            )
            status = status_response.json()['data']['status']
        
        if status != 'SUCCEEDED':
            raise Exception(f"Apify run failed with status: {status}")
        
        # Получение результатов
        items_response = self._make_request(
            'GET',
            f'{self.base_url}/datasets/{dataset_id}/items'
        )
        
        return items_response.json()