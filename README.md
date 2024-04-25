# GithubAnalysis
## Setup
All settings are in settings.json. You can change `statistics` to skip some statistics collection. `sufficiency_for_considering_contributors` is a field that determines the ratio of the number of commits a contributor must have  to the number of commits of the top-1 contributor to this file to be considered in the following statistics. It is used because committing to the file once and a thousand times is different. The same logic applies to the `sufficiency_for_considering_files.` Only groups with `sufficiency_for_considering_files * max` joint commits (where `max` is the maximum number of commits such that some group was in all of them) will be presented in the statistics
## Run
Just run main.py and provide a link to the remote GitHub repository as input.
