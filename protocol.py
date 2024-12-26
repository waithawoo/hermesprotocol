import struct
import asyncio
from utils import xor_encrypt_decrypt, calculate_checksum
from cryptography.fernet import Fernet
import secrets

KEY = b'BYCi-KsviDyiyxZkX7bS6fs2n9GSIHONzqV6CdEE-I8='

class HermesProtocol:
    def __init__(self, encryption_key: bytes = b'\x01'):
        self.encryption_key = encryption_key
        self.key = KEY
        self.cipher = Fernet(self.key)
    
    def encrypt_payload(self, payload: bytes) -> bytes:
        return self.cipher.encrypt(payload)

    def decrypt_payload(self, encrypted_payload: bytes) -> bytes:
        return self.cipher.decrypt(encrypted_payload)
    
    def encrypt_message(self, message: bytes) -> bytes:
        """Encrypt message using XOR encryption."""
        return xor_encrypt_decrypt(message, self.encryption_key)
    
    def decrypt_message(self, message: bytes) -> bytes:
        """Decrypt message using XOR encryption."""
        return xor_encrypt_decrypt(message, self.encryption_key)
    
    def create_message(self, message_type: int, payload: bytes) -> bytes:
        """Create a message with a header and checksum."""
        encrypted_payload = self.encrypt_payload(payload)

        encrypted_payload_size = len(encrypted_payload)
        
        # Construct the message
        header = struct.pack('!I', encrypted_payload_size + 6) # 4 for header, 1 for message_type and 1 for checksum
        message = struct.pack('!B', message_type) + encrypted_payload
        checksum = calculate_checksum(header + message)
        
        return self.encrypt_message(header + message + checksum)
    
    def parse_message(self, data: bytes) -> tuple:
        """Parse a raw message."""
        data = self.decrypt_message(data)
        print('data ', data)
        if len(data) < 4:
            raise ValueError("Insufficient data for header. Received bytes: {}".format(len(data)))

        header = data[:4]        
        message_size = struct.unpack('!I', header)[0]

        if len(data) < message_size:
            raise ValueError(f"Insufficient data: expected {message_size} bytes but got {len(data)}.")
        
        # Extract the message body and checksum
        message = data[4:-1]
        received_checksum = data[-1:]
        
        # Verify checksum
        if received_checksum != calculate_checksum(header + message):
            raise ValueError("Checksum mismatch!")
        
        # Extract message type and decrypted payload
        message_type = message[0]
        payload = self.decrypt_payload(message[1:])
                
        return message_type, payload


class HermesKeyExchange:
    def __init__(self, prime: int, generator: int):
        self.prime = prime
        self.generator = generator
        self.private_key = secrets.randbelow(prime)
        self.shared_key = None

    def generate_public_key(self):
        return pow(self.generator, self.private_key, self.prime)

    def compute_shared_key(self, public_key):
        self.shared_key = pow(public_key, self.private_key, self.prime)

    def encrypt(self, message: bytes):
        return xor_encrypt_decrypt(message, self.shared_key.to_bytes(16, 'big'))

    def decrypt(self, message: bytes):
        return xor_encrypt_decrypt(message, self.shared_key.to_bytes(16, 'big'))


if __name__ == '__main__':
    prime = 23
    generator = 5
    client = HermesKeyExchange(prime, generator)
    server = HermesKeyExchange(prime, generator)

    # Key exchange
    client_public_key = client.generate_public_key()
    server_public_key = server.generate_public_key()

    print('client_public_key ', client_public_key)
    print('server_public_key ', server_public_key)

    client.compute_shared_key(server_public_key)
    server.compute_shared_key(client_public_key)

    print('client.shared_key ', client.shared_key)
    print('server.shared_key ', server.shared_key)

    # Shared key is now established
    assert client.shared_key == server.shared_key
