import uuid


def generate_unique_code(prefix: str = "") -> str:
    code = uuid.uuid4().hex[:8].upper()
    return f"{prefix}{code}" if prefix else code


def normalize_phone(phone: str) -> str:
    cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
    return cleaned
