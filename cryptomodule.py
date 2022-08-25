#!/usr/bin/python3
import base64
import pickle
import bz2
from Crypto.Hash import SHA512
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.IO import PEM
from Crypto.Util.Padding import pad, unpad


class RSA_key():
    def __init__(self):
        self.hasprivate = None
        self.size = None

    def gen_key(self, size):
        import time
        self.size = size
        t = time.time()
        print('Generating', size, 'bit key')
        rand = Random.new().read
        self.private_key = RSA.generate(size, rand)
        self.public_key = self.private_key.publickey()
        self.hasprivate = True
        t2=time.time()
        print('Generation Time', t2-t)

    def export_private_key(self, passphrase=None):
        if not passphrase:
            print('Warning: exporting private key unencrypted')
            data = self.private_key.exportKey().decode("utf-8")
        else:
            data = self.private_key.exportKey(passphrase=passphrase).decode("utf-8")
        return str(data)

    def export_public_key(self):
        data = self.public_key.exportKey().decode("utf-8")
        return str(data)

    def _import(self,key):
        if key.has_private:
            self.private_key = key
            self.public_key = key.publickey()
            self.hasprivate = True
        else:
            self.public_key = key
            self.private_key = None
            self.hasprivate = False
        self.size = key.size

    def import_key_file(self,filename,passphrase=None):
        with open(filename, "r",encoding='utf-8') as file:
            content = file.read()
        key = RSA.importKey(content, passphrase=passphrase)
        self._import(key)

    def import_key(self,data):
        key = RSA.importKey(data)
        self._import(key)

    def sign_hash(self,data):
        if self.private_key.can_sign():
            signer = PKCS1_v1_5.new(self.private_key)
            signature = signer.sign(data)
        else:
            raise Exception
        return signature

    def verify_hash(self, data, signature):
        verifier = PKCS1_v1_5.new(self.public_key)
        verify = verifier.verify(data, signature)
        return verify

    def encrypt(self, data):
        if self.public_key.can_encrypt():
            cipher = PKCS1_OAEP.new(self.public_key, hashAlgo= SHA512)
            encdata = cipher.encrypt(data)
            del cipher
        else:
            raise Exception
        return encdata

    def decrypt(self, data):
        cipher = PKCS1_OAEP.new(self.private_key, hashAlgo= SHA512)
        decdata = cipher.decrypt(data)
        del cipher
        return decdata


def AESencrypt(data, key, iv, binary=False):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if binary:
        bytedata = data
    else:
        try:
            bytedata = bytes(data.decode(),'utf-8')
        except:
            bytedata = bytes(data,'utf-8')
        
    padded = pad(bytedata,16)
    encrypted = cipher.encrypt(padded)
    del cipher
    return encrypted


def AESdecrypt(data, key, iv, binary=False):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dec = cipher.decrypt(data)
    unpadded = unpad(dec,16)
    decrypted = unpadded
    del cipher
    if binary:
        return decrypted
    else:
        return str(decrypted,'utf-8')

        
def rsaaes_encrypt(my_key, destination_key, message, isfile=False):
    aeskey = Random.new().read(32)
    iv = Random.new().read(AES.block_size)
    hash = SHA512.new()
    if isfile:
        hash.update(message)
        msg = message
    else:
        hash.update(bytes(message,'utf-8'))
        msg = bytes(message,'utf-8')
    
    signer = PKCS1_v1_5.new(my_key.private_key)
    signature = signer.sign(hash)
    data = {"iv": iv,
            'hash': hash.hexdigest(),
            'sign': signature,
            'key': destination_key.encrypt(aeskey),
            'msg': AESencrypt(msg, aeskey, iv, isfile)
            }
    del aeskey
    del iv
    del signer
    if isfile:
        return pickle.dumps(data)
    else:
        return base64.b64encode(pickle.dumps(data))


def rsaaes_decrypt(my_key, sender_key, encdata, isfile=False):
    if isfile:
        data = pickle.loads(encdata)
    else:
        data = pickle.loads(base64.b64decode(encdata))
    iv = data['iv']
    aeskey = my_key.decrypt(data['key'])
    decmsg = AESdecrypt(data['msg'], aeskey, iv, isfile)
    hash = SHA512.new()
    if isfile:
        hash.update(decmsg)
    else:
        hash.update(bytes(decmsg,'utf-8'))
    verify = sender_key.verify_hash(hash, data['sign'])
    returnme = {
        'msg':decmsg,
        'verify':verify,
        'hash':hash.hexdigest()
        }
    return returnme
    



