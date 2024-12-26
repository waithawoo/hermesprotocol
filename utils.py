def xor_encrypt_decrypt(data: bytes, key: bytes) -> bytes:
    """Simple XOR encryption/decryption."""
    return bytes([b ^ key[0] for b in data])

def calculate_checksum(data: bytes) -> bytes:
    """Calculate XOR checksum of the data."""
    checksum = 0
    for byte in data:
        checksum ^= byte
    return bytes([checksum])
