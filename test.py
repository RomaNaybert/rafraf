import hashlib

def hash_string(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    hash_hex = hash_object.hexdigest()

    return hash_hex

print(hash_string('dogedogedog'))

#a7ffa6121c67667045ccb87b57aac89f577d7235c1b8316bcc458decbef6ad5b