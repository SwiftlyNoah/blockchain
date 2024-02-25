import os
import ecdsa
import hashlib

class Wallet:
    def __init__(self):
        self.private_key = Wallet.generate_private_key()
        self.public_key = Wallet.private_to_public(self.private_key)
        self.crypto_address = Wallet.public_to_address(self.public_key)

    @staticmethod
    def sha256(data):
        return hashlib.sha256(data).digest()

    @staticmethod
    def ripemd160(data):
        h = hashlib.new('ripemd160')
        h.update(data)
        return h.digest()

    @staticmethod
    def generate_private_key():
        return os.urandom(32).hex()

    @staticmethod
    def private_to_public(private_key):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        # Use the compressed format of the public key, which starts with either 02 or 03
        compressed_vk = vk.to_string("compressed")  # Get the compressed public key as bytes
        vk_without_prefix = compressed_vk[1:].hex()  # Skip the prefix and convert to hex
        return vk_without_prefix

    @staticmethod
    def public_to_address(public_key):
        pubkey_sha256 = Wallet.sha256(public_key.encode('utf8'))
        pubkey_ripemd160 = Wallet.ripemd160(pubkey_sha256)
        return Wallet.base58_encode(pubkey_ripemd160)

    @staticmethod
    def base58_encode(data):
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        num = int.from_bytes(data, 'big')
        encode = ''
        while num > 0:
            num, remainder = divmod(num, 58)
            encode = alphabet[remainder] + encode
        return encode