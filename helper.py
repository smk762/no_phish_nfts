#!/usr/bin/env python3
import time
import hmac
import hashlib

def now():
    return int(time.time())


def hex_to_string(hexstring):
    return bytearray.fromhex(hexstring).decode()


def get_hmac(secret, url_hex):
    url = hex_to_string(url_hex)
    hmac_one = hmac.new(key=secret.encode(), msg=url.encode(), digestmod=hashlib.sha1)
    return hmac_one.hexdigest()
