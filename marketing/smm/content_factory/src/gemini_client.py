import os
import requests
import base64
from typing import Dict

class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set. Add it to .env file")
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta'
    
    def analyze_video(self, video_url: str) -> Dict:
        prompt = """Analyze this video and extract:
1. Hook (first 10 seconds) - what grabs attention
2. Content structure (beginning, middle, end)
3. Key patterns that make it engaging
4. Replicable elements for content creation
5. Target audience
6. Main topic/theme

Return as JSON with these keys: hook, structure, patterns, replicable_elements, audience, topic"""
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"fileData": {"fileUri": video_url}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048
            }
        }
        
        response = requests.post(
            f'{self.base_url}/models/gemini-pro:generateContent',
            params={'key': self.api_key},
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        
        import json
        try:
            return json.loads(text)
        except:
            return {'raw_analysis': text}
