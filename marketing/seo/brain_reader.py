"""
Модуль для чтения "второго мозга" клиники ARclinic.
Загружает знания из папки C:\\Arclinic\\мозг_клиники_ARclinic
"""

import os
from pathlib import Path

BRAIN_PATH = Path(r"C:\Arclinic\мозг_клиники_ARclinic")


def load_brain_file(relative_path: str) -> str:
    """Загружает содержимое файла из второго мозга."""
    full_path = BRAIN_PATH / relative_path
    if not full_path.exists():
        return f"[Файл не найден: {relative_path}]"
    return full_path.read_text(encoding="utf-8")


def get_clinic_info() -> dict:
    """Возвращает структурированную информацию о клинике."""
    return {
        "клиника": load_brain_file("бизнес/клиника.md"),
        "услуги": load_brain_file("бизнес/услуги.md"),
        "аудитория": load_brain_file("бизнес/аудитория.md"),
        "возражения": load_brain_file("бизнес/возражения.md"),
        "экономика": load_brain_file("бизнес/экономика.md"),
    }


def get_identity_info() -> dict:
    """Возвращает информацию об идентичности и принципах."""
    return {
        "me": load_brain_file("идентичность/me.md"),
        "бизнес_принципы": load_brain_file("идентичность/бизнес-принципы.md"),
        "контент_принципы": load_brain_file("идентичность/контент-принципы.md"),
    }


def get_tone_info() -> str:
    """Возвращает информацию о голосе и тоне."""
    return load_brain_file("голос/tone.md")


def get_all_knowledge() -> dict:
    """Загружает все знания из второго мозга."""
    knowledge = {}
    knowledge.update(get_clinic_info())
    knowledge.update(get_identity_info())
    knowledge["tone"] = get_tone_info()
    return knowledge


def list_brain_structure() -> list:
    """Возвращает список всех файлов во втором мозге."""
    files = []
    for root, dirs, filenames in os.walk(BRAIN_PATH):
        for f in filenames:
            rel_path = os.path.relpath(os.path.join(root, f), BRAIN_PATH)
            files.append(rel_path)
    return sorted(files)


if __name__ == "__main__":
    print("=" * 60)
    print("ВТОРОЙ МОЗГ ARclinic")
    print("=" * 60)
    print(f"\nПуть: {BRAIN_PATH}")
    print(f"\nФайлы:")
    for f in list_brain_structure():
        print(f"  - {f}")
    print(f"\nВсего файлов: {len(list_brain_structure())}")
