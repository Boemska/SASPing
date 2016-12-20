# SASPING

Stateless SAS program runner via web interface

### Install

`pip install -r requirements.txt`

### How to run

`python main.py [settings json file path] [output csv file path]`

output CSV file headers:
`id, status, which test failed, failed pattern, message, had to login, time of execution, execution duration`


### Test
`python -m unittest tests`
