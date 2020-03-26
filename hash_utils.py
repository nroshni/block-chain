import json
import hashlib


def hash_string_sha256(sstring):
    return hashlib.sha256(sstring).hexdigest()


def hash_block(block):
    """ Returns the hash of the block """
    return hashlib.sha256(json.dumps(block,
                                     sort_keys=True).encode()).hexdigest()
