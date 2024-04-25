# GithubAnalysis
## Setup
All settings are in settings.json. You can change `statistics` to skip some statistics collection. `sufficiency_for_considering` is a field that determines the ratio of the number of commits a contributor must have  to the number of commits of the top-1 contributor to this file to be considered in the following statistics. It is used because committing to the file once and a thousand times is different. 
## Run
Just run main.py and provide a link to the remote GitHub repository as input.
