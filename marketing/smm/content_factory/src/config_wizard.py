import os
import sys
import io
import getpass
from pathlib import Path
from dotenv import load_dotenv, set_key, dotenv_values

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

REQUIRED_KEYS = {
    'APIFY_TOKEN': {
        'description': 'Apify API токен (скрапинг X/Twitter, Instagram, TikTok)',
        'url': 'https://console.apify.com/account/integrations',
        'optional': False,
        'prefix': None,
    },
    'TUBELAB_API_KEY': {
        'description': 'TubeLab API ключ (YouTube аналитика)',
        'url': 'https://tubelab.net/settings/api',
        'optional': False,
        'prefix': None,
    },
    'GEMINI_API_KEY': {
        'description': 'Google Gemini API ключ (анализ видео)',
        'url': 'https://aistudio.google.com/apikey',
        'optional': False,
        'prefix': 'AI',
    },
    'AI_API_KEY': {
        'description': 'Promptra API ключ (OpenAI-совместимый прокси)',
        'url': 'регистрация на promptra.ru',
        'optional': False,
        'prefix': 'sk',
    },
    'AI_API_BASE_URL': {
        'description': 'AI API URL (Promptra — OpenAI-совместимый прокси)',
        'url': 'Promptra: https://api.promptra.ru/v1',
        'optional': False,
        'prefix': 'http',
        'choices': {
            '1': 'https://api.promptra.ru/v1',
        },
    },
    'AI_MODEL': {
        'description': 'AI модель (deepseek-v4-pro, deepseek-v4-flash)',
        'url': '1) deepseek/deepseek-v4-pro  2) deepseek/deepseek-v4-flash',
        'optional': True,
        'prefix': None,
        'choices': {
            '1': 'deepseek/deepseek-v4-pro',
            '2': 'deepseek/deepseek-v4-flash',
        },
        'default': 'deepseek/deepseek-v4-pro',
    },
}

ENV_FILE = Path('.env')
EXAMPLE_FILE = Path('.env.example')


def _print_header():
    print()
    print('=' * 70)
    print('  Content Factory — Мастер настройки API-ключей')
    print('=' * 70)
    print()
    print('Для работы SMM-агента требуются API-ключи внешних сервисов.')
    print('Откройте ссылки ниже, получите ключи и введите их.')
    print('Ключи сохранятся в файл .env (этот файл не попадает в git).')
    print()
    print('Нажмите Enter чтобы пропустить отдельный ключ.', flush=True)
    print()


def _ask_key(name: str, info: dict) -> str | None:
    desc = info['description']
    url = info.get('url', '')
    optional = info.get('optional', False)
    prefix = info.get('prefix')
    choices = info.get('choices')
    default = info.get('default')

    print(f'  ● {name}')
    print(f'    {desc}')
    if url:
        print(f'    Получите здесь: {url}')

    if choices:
        prompt = '    Выбор'
    elif name.endswith('_KEY') or name.endswith('_TOKEN'):
        prompt = '    Ключ'
    else:
        prompt = '    Значение'

    while True:
        if choices:
            raw = input(f'    {prompt} [1-{len(choices)}] {"(по умолчанию: " + default + ")" if default else ""}: ').strip()
            if not raw and default:
                return default
            if raw in choices:
                print(f'    ✓ Выбрано: {choices[raw]}')
                print()
                return choices[raw]
            if raw in choices.values():
                print(f'    ✓ Выбрано: {raw}')
                print()
                return raw
            if raw:
                print(f'    ✗ Некорректный выбор. Попробуйте 1-{len(choices)}')
                continue
            if optional:
                print('    → Пропущено')
                print()
                return default
            print(f'    ✗ Значение обязательно. Введите 1-{len(choices)}')
            continue
        else:
            is_secret = name.endswith('_KEY') or name.endswith('_TOKEN') or name == 'APIFY_TOKEN'
            try:
                if is_secret:
                    raw = getpass.getpass(f'    {prompt} (ввод скрыт, Enter — пропустить): ')
                else:
                    raw = input(f'    {prompt} (Enter — пропустить): ')
            except (EOFError, KeyboardInterrupt):
                return None

            raw = raw.strip()

            if not raw:
                if optional:
                    print('    → Пропущено')
                    print()
                    return default if default else None
                print('    ✗ Это поле обязательно. Введите значение.')
                continue

            if prefix and not raw.startswith(prefix):
                print(f'    ⚠ Ожидается что ключ начинается с "{prefix}". Продолжить с этим значением? (y/n): ', end='')
                try:
                    confirm = input().strip().lower()
                except (EOFError, KeyboardInterrupt):
                    confirm = 'n'
                if confirm not in ('y', 'yes', 'д', 'да', ''):
                    print('    → Попробуйте ещё раз')
                    continue

            masked = raw[:4] + '...' + raw[-4:] if len(raw) > 10 else '***'
            print(f'    ✓ Принято: {masked}')
            print()
            return raw


def _save_env(values: dict):
    if not ENV_FILE.exists():
        if EXAMPLE_FILE.exists():
            ENV_FILE.write_text(EXAMPLE_FILE.read_text(), encoding='utf-8')
        else:
            ENV_FILE.write_text('', encoding='utf-8')

    existing = dotenv_values(ENV_FILE) if ENV_FILE.exists() else {}

    for key, value in values.items():
        if value is not None:
            set_key(str(ENV_FILE), key, value)

    load_dotenv(ENV_FILE, override=True)


def run_wizard():
    _print_header()

    existing = dotenv_values(ENV_FILE) if ENV_FILE.exists() else {}
    values = {}

    for name, info in REQUIRED_KEYS.items():
        current = existing.get(name)
        if current and current != f'your_{name.lower()}_here' and not current.startswith('your_'):
            masked = current[:4] + '...' + current[-4:] if len(current) > 10 else '***'
            print(f'  ✓ {name} уже настроен ({masked})')
            print(f'    Оставить как есть? (Y/n): ', end='')
            try:
                choice = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                choice = 'y'
            if choice in ('', 'y', 'yes', 'д', 'да'):
                print(f'    → Оставлено')
                print()
                continue
            else:
                print(f'    → Заменить')
                print()

        value = _ask_key(name, info)
        if value is not None:
            values[name] = value

    if values:
        _save_env(values)
        print()
        print('=' * 70)
        print(f'  ✓ Конфигурация сохранена в {ENV_FILE}')
        print('=' * 70)
        print()
    else:
        print()
        print('  Ничего не изменено.')
        print()

    return True


def check_missing_keys() -> list:
    load_dotenv(ENV_FILE)
    missing = []
    for name, info in REQUIRED_KEYS.items():
        value = os.getenv(name)
        if not value or value.startswith('your_') or value == f'your_{name.lower()}_here':
            if info.get('optional') and info.get('default'):
                os.environ[name] = info['default']
                continue
            if not info.get('optional'):
                missing.append((name, info))
    return missing


def ensure_config() -> bool:
    missing = check_missing_keys()
    if not missing:
        load_dotenv(ENV_FILE)
        return True

    print()
    print('⚠ Отсутствуют обязательные API-ключи:')
    for name, info in missing:
        print(f'  • {name} — {info["description"]}')
    print()

    try:
        choice = input('Запустить мастер настройки? (Y/n): ').strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = 'y'

    if choice in ('', 'y', 'yes', 'д', 'да'):
        return run_wizard()
    else:
        print()
        print('Настройка отменена. Запустите "python setup.py" или создайте .env вручную.')
        print()
        return False
