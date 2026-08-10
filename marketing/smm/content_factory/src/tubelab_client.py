import os
import requests
from typing import List, Dict

class TubeLabClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('TUBELAB_API_KEY')
        if not self.api_key:
            raise ValueError("TUBELAB_API_KEY not set. Add it to .env file")
        self.base_url = 'https://api.tubelab.net/v1'
    
    def fetch_outliers(self, channel_id: str = None, days: int = 30, limit: int = 50) -> List[Dict]:
        params = {
            'days': days,
            'limit': limit
        }
        
        if channel_id:
            params['channelId'] = channel_id
        
        response = requests.get(
            f'{self.base_url}/outliers',
            params=params,
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_transcript(self, video_id: str) -> str:
        response = requests.get(
            f'{self.base_url}/transcripts/{video_id}',
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        response.raise_for_status()
        
        return response.json().get('transcript', '')
