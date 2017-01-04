# SASPING

Stateless SAS program runner via web interface

### Install

`pip install -r requirements.txt`
`cd ./report && npm install`

### How to run
`cd ..` - only if you are in report directory after `npm install`.

`python main.py [settings json file path] [output csv|html file path]`

It will append new requests if file already exists.


### Test
`python -m unittest tests`
