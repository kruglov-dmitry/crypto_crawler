import requests
import hmac
import hashlib
import time
import json

from urllib import urlencode as _urlencode
str = unicode

key = ""
secret = ""
command = 'returnBalances'

req = { 
 'command' : command,
 'nonce': int(time.time()*1000) 
}

print _urlencode(req)

sign = hmac.new(secret, _urlencode(req), hashlib.sha512).hexdigest()
headers = {
            'Sign': sign,
            'Key': key
}


res = requests.post('https://poloniex.com/tradingApi', data=req, headers=headers, timeout=5).json()
print res
