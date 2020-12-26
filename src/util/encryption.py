import hashlib

__all__ = ('generate_verify_hash',)


def generate_verify_hash(shared_secret: bytes, public_key: bytes):
    verify_hash = hashlib.sha1()

    verify_hash.update((' '*20).encode('utf-8'))
    verify_hash.update(shared_secret)
    verify_hash.update(public_key)

    return format(int.from_bytes(verify_hash.digest(), byteorder='big', signed=True), 'x')
