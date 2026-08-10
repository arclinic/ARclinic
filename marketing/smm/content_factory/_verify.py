import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

print('=== .env ===')
print(f'AI_MODEL={os.getenv("AI_MODEL")}')
print(f'BASE_URL={os.getenv("AI_API_BASE_URL")}')
key = os.getenv('AI_API_KEY', '')
print(f'AI_API_KEY={key[:12]}...({len(key)} chars)' if key else 'AI_API_KEY=NOT SET')
print()

print('=== AIClient test ===')
from src.ai_client import AIClient
ai = AIClient()
print(f'Model name: {ai.model_name}')
print(f'Base URL: {ai.base_url}')
r = ai.generate('Say OK in russian, one word')
print(f'Response: {r}')
