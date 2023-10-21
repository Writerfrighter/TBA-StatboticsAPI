import pandas as pd
import TBA
import os

data_save_dir = "scouting_data"


def combineDataRange(minDate, maxDate):
    files = []
    for filename in os.listdir(data_save_dir):
        f = os.path.join(data_save_dir, filename)
        if os.path.isfile(f):
            try:
                if int(filename.rsplit("_", 1)[0][:8:]) >= minDate and int(
                    filename.rsplit("_", 1) <= maxDate
                ):
                    files.append(filename)
            except:
                pass

    return combineData(files, str(minDate) + str(maxDate) + "scouting_data.xlsx")


def combineData(files, filename):
    extension = files[0].rsplit(".", 1)[1]
    if extension == "xlsx":
        df = pd.read_excel(files[0])
    elif extension == "csv":
        df = pd.read_csv(files[0])
    else:
        raise TypeError("Wrong file type")

    for file in files[1::]:
        extension = file.rsplit(".", 1)[1]
        if extension == "xlsx":
            df = pd.concat(
                [df, pd.read_excel(os.path.join(data_save_dir, file))],
                ignore_index=True,
            )
        elif extension == "csv":
            df = pd.concat(
                [df, pd.read_csv(os.path.join(data_save_dir, file))], ignore_index=True
            )
        else:
            raise TypeError("Wrong file type")

    df.to_excel(os.path.join("combined_data", filename))

def getDataAccuracy():
    df = pd.read_excel("combined_data\BordieData.xlsx")
    print(df)
    
    eventMatches = TBA.fetchEventMatchs("2023brd")
    print(eventMatches)
    for event in eventMatches:
        if event['actual_time'] == None:
            pass
        else:
            match = df.loc[df['Match Number'] == event['match_number']]
            if match["Endgame Sustainbility Bonus"] == event["Endgame"]: pass
            

getDataAccuracy()