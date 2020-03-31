import json
import hashlib


def hash_string_sha256(sstring):
    return hashlib.sha256(sstring).hexdigest()


def hash_block(block):
    """ Returns the hash of the block """
    hashable_block = block.__dict__.copy()  # Create a copy as it would
    # otherwise change the prev dict while hashing
    # Convert transaction objects within a block to dictionaries as well
    hashable_block['transactions'] = [
        tx.to_ordered_dict() for tx in hashable_block['transactions']
    ]
    print(f'hashable block : {hashable_block}')
    return hash_string_sha256(
        json.dumps(hashable_block, sort_keys=True).encode())
