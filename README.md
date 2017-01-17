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


### Create dummy test data
`python test_generator.py [from unix timestamp] [interval in seconds] [max runs] [tests per run] [output]`

e.g. `python test_generator.py 1389970377 3600 6000 10 report/build` - will create 60000 rows test file. First run will be on Fri, 17 Jan 2014, in one hour intervals.  
