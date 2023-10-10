import os

data_save_dir = "scouting_data"

def combineData():
    for filename in os.listdir(data_save_dir):
        if filename: #Todo: Find file naming convention for time & date
            f = os.path.join(data_save_dir, filename)
            if os.path.isfile(f):
                pass
            