from random import randint
import hashlib


def string_hash_code(s: str) -> int:
    n = len(s)
    hash_code = 0

    for i, c in enumerate(s, start=1):
        hash_code += c * (31 ** (n - i))

    return hash_code


def gen_seed() -> int:
    return randint(0, (2 ** 64) - 1)


def seed_hash(seed: int):
    m = hashlib.sha256()
    m.update(seed.to_bytes(8, 'big'))
    return m.digest()[:8]
