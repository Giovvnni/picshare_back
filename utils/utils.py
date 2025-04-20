import secrets

def generate_wallet_key():
    return secrets.token_hex(32)  # 64 caracteres hexadecimales

def generate_read_only_key():
    return secrets.token_urlsafe(16)
