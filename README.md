# SASPING

Stateless SAS program runner via web interface

### Development

* `pip install -r requirements.txt`
* `cd ./report && npm install`
* `npm run dev` - build and run (it will watch file changes and build your js and sass)
* `cd ..`
* `test_generator.py 1477324439 3600 60000 10 5 report/build` - generate some dummy data
* `python aggregate.py report/build/sasping_data.csv 100` - run aggregator to shring the generated data
* open http://localhost:8000/build/

### Run collector
`python main.py [settings json file path] [output dir]`

This command will run the main program. It will read your settings file (check the `settings.json` file structure), run the tests described in settings file, and append data to your sasping_data.csv in your output dir (second command argument)

### Create dummy test data
`python test_generator.py [from unix timestamp] [interval in seconds] [max runs] [tests per run] [number of apps] [output]`

e.g. `python test_generator.py 1389970377 3600 6000 10 5 report/build` - will create 60000 rows test file. First run will be on Fri, 17 Jan 2014, in one hour intervals.  

### Run aggregator
`python aggregate.py [master csv file] [number of max data points]`

Aggregator will shrink your data if necessary and break to smaller files suitable for the web application. Second command argument is the number of maximum points on graph shown to user. Aggregator will combine multiple collector runs into one, and create files with as many as possible data points, but less than the second argument

### Deploy

Run `npm run release` from `report/` folder to build web application. It will create `report/dist` folder which should be copied to web accessible destination.

Add cron jobs to run collector and aggregator scripts. Both scripts should create/save files to the web app path.
