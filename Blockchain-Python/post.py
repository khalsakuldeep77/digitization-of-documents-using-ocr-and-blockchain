# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 23:02:20 2020

@author: USER
"""


import requests
import json
print("enter the hash you want to store in the blockchain")
hash=input()
dictToSend = {'sender':'3df81c65b360447f82d7d85921d978c8','recipient':'someone-other-address','amount':hash}
res = requests.post('http://localhost:8000/transactions/new',json=dictToSend)
print('response from server:',res.text)
res = requests.get('http://localhost:8000/mine')
print(res)
data=res.json()
i=data['transactions'][0]
print(i)
