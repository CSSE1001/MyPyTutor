# since the hash function seems to be different on different
# machines here is a simple string hash that hashes up to the first 40
# chars
def simple_hash(text):
    hash_value = 5381
    num = 0
    for c in text:
        if num > 40:
            break
        num += 1
        hash_value = 0x00ffffff & ((hash_value << 5) + hash_value + ord(c))
    return hash_value
