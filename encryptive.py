import os

from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from trng import generate_random


def generate_keys():
    # generate key pair
    key_pair = RSA.generate(2048, randfunc=generate_random)

    private_key = key_pair.exportKey('PEM')  # private key for hashing
    public_key = key_pair.publickey().exportKey('PEM')  # public key for exchange

    try:
        with open('private.pem', 'wb') as keyfile:
            keyfile.write(private_key)
            keyfile.close()
        print("[Successfully created your RSA PRIVATE key]")
    except Exception as e:
        print("[Error creating your key]", e)

    try:
        with open("public.pem", "wb") as keyfile:
            keyfile.write(public_key)
            keyfile.close()
        return True
    except Exception as e:
        return False


def sign_file(file, private_key):
    text_file = file.read()
    msg = bytes(str(text_file), 'utf-8')

    # print(msg_raw)
    print('[Message to sign:] ' + msg.decode())

    try:
        private_key: RsaKey = RSA.import_key(private_key.read())
    except Exception as e:
        print("[Error opening private key]", e)

    # signing
    hasher = SHA256.new(msg)
    signer = pkcs1_15.new(private_key)
    signature = signer.sign(hasher)

    try:
        signed_file = open(os.path.basename('/signatures/signed_file'), 'wb')
        signed_file.write(signature)
        signed_file.close()
        print("[Successfully signed your message!]")
    except Exception as e:
        print("[Error signing your message]", e)


def check_signature(file, public_key):
    text_file = file.read()
    msg = bytes(str(text_file), 'utf-8')
    key = RSA.import_key(public_key.read())
    hasher = SHA256.new(msg)
    private_key_file = open('private.pem', 'rb')
    private = RSA.import_key(private_key_file.read())
    signer = PKCS115_SigScheme(private)
    signature = signer.sign(hasher)
    verifier = PKCS115_SigScheme(key)

    try:
        verifier.verify(hasher, signature)
        return True
    except Exception as e:
        return False
