import os
import requests
from typing import Dict, List

class AIClient:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = 'deepseek/deepseek-v4-pro'):
        self.api_key = api_key or os.getenv('AI_API_KEY')
        self.base_url = base_url or os.getenv('AI_API_BASE_URL')
        
        if not self.api_key:
            raise ValueError("AI_API_KEY not set. Add it to .env file")
        if not self.base_url:
            raise ValueError("AI_API_BASE_URL not set. Add it to .env file")
        
        self.model = model
        self.model_name = model or os.getenv('AI_MODEL', 'deepseek/deepseek-v4-pro')
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Новый формат запроса для DeepSeek API
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4096,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Печатаем ошибку для отладки
            if response.status_code != 200:
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"Ответ: {response.text[:500]}")
            
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Ответ сервера: {e.response.text[:500]}")
            raise