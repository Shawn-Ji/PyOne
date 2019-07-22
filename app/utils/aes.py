#-*- coding=utf-8 -*-
from header import *
from Crypto import Random
from Crypto.Cipher import AES
import hashlib
import base64
import time
import urllib


class AesCls(object):
    def __init__(self,key):
        self.key=key

    def pad(self,data):
        length = 16 - (len(data) % 16)
        return data + (chr(length)*length).encode()

    def unpad(self,data):
        return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

    def bytes_to_key(self,data, salt, output=48):
        # extended from https://gist.github.com/gsakkis/4546068
        assert len(salt) == 8, len(salt)
        data=data.encode('utf-8')
        data += salt
        key = hashlib.md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = hashlib.md5(key + data).digest()
            final_key += key
        return final_key[:output]

    def encrypt(self,message):
        salt = Random.new().read(8)
        key_iv = self.bytes_to_key(self.key, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(self.pad(message)))

    def decrypt(self,encrypted):
        encrypted = base64.b64decode(encrypted)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = self.bytes_to_key(self.key, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return self.unpad(aes.decrypt(encrypted[16:]))


def replace_token(token):
    return token.replace('+','plus').replace('/','xiegang').replace('=','equal')

def reverse_token(token):
    return token.replace('plus','+').replace('xiegang','/').replace('equal','=')

def VerifyToken(token,filepath):
    token=reverse_token(token)
    path=filepath.split(':')[-1]
    ae=AesCls(GetConfig("password"))
    msg=ae.decrypt(token)
    r_filepath,timeout=msg.split('#$#')
    if r_filepath==path and int(timeout)>time.time():
        return True
    else:
        return False

def GenerateToken(filepath):
    path=filepath.split(':')[-1]
    ae=AesCls(GetConfig("password"))
    timeout=int(time.time())+int(GetConfig("downloadUrl_timeout"))
    key="{}#$#{}".format(path,timeout)
    return replace_token(ae.encrypt(key))
