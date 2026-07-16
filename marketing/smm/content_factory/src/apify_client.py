import os
import requests
import time
from typing import List, Dict

# Список всех ключей Apify от Анны
APIFY_KEYS = [
    'apify_api_s7CtRGUlvVHXbK3Q3vPjWSy6ZfDNe80VKnU0',
    'apify_api_RCSzFDBq9g7xBybrp43kpTacfdxJBE16Vj7o',
    'apify_api_AWssTaFMkGmwBO9WTWYj8LFcV4kDp10qMqlm',
    'apify_api_YDMvgxM4N6QWLkEAcj70o5VbWrPHdr2SOPl5',
    'apify_api_VG6GhQS7MK1mzjHdmcTv9WNFCpXqhu2k9PCb',
    'apify_api_afvrpS0yBWmMbBwCYJDeK8a81TNPIZ17dfph',
    'apify_api_xmQdR5xnNeGdL48g6uP8zQNCTwkqsk1GwAZR',
    'apify_api_ye5COeWsK211Da9WhTybTyE3HX3KWl4lcnX8',
    'apify_api_weZbCAT9CAcxAIcZ6RbasUsu3UaAfS1vG7OV',
    'apify_api_PmB4lpUbEehONkeq7fBXQWzBOcERtr2WvWBR'
]

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