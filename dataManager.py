import pandas as pd
import TBA
import params
import os


def combineDataRange(minDate, maxDate):
    """Combines a data range given a max and min date"""
    files = []
    for filename in os.listdir(params.upload_folder):
        f = os.path.join(params.upload_folder, filename)
        if os.path.isfile(f):
            try:
                if int(filename.rsplit("_", 1)[1][:8:]) >= minDate and int(
                    filename.rsplit("_", 1)[1][:8:]) <= maxDate:
                    files.append( filename)
                    
            except:
                pass
        else: "Hold up, there's a directory in here?"

    return combineData(files, str(minDate) + str(maxDate) + "scouting_data.xlsx")


def combineData(files, filename):
    """Combines a given list of files and writes the result it to processed_data as a xlsx"""
    extension = files[0].rsplit(".", 1)[1]
    if extension == "xlsx":
        df = pd.read_excel(os.path.join(params.upload_folder, files[0]))
    elif extension == "csv":
        df = pd.read_csv(os.path.join(params.upload_folder, files[0]))
    else:
        raise TypeError("Wrong file type")

    for file in files[1::]:
        extension = file.rsplit(".", 1)[1]
        if extension == "xlsx":
            df = pd.concat(
                [df, pd.read_excel(os.path.join(params.upload_folder, file))],
                ignore_index=True,
            )
        elif extension == "csv":
            df = pd.concat(
                [df, pd.read_csv(os.path.join(params.upload_folder, file))],
                ignore_index=True,
            )
        else:
            raise TypeError("Wrong file type")

    df.to_excel(os.path.join(params.download_folder, filename))

def completeData(eventCode):
    """Completes scouting data using TBA data for the event"""
    df = pd.read_excel("{}\{}.xlsx".format(params.download_folder, eventCode))
    eventMatches = TBA.fetchEventMatches(eventCode)

    for k, entry in enumerate(df.values[::]):
        index = [
            i for i, j in enumerate(eventMatches) if j["match_number"] == entry[0]
        ][0]
        alliance = entry[3][-3::-1][::-1].lower()
        # Check if the team numbers are correct, or else we can't continue
        if (
            "frc" + str(entry[1])
            in eventMatches[index]["alliances"]["blue"]["team_keys"]
            or "frc" + str(entry[1])
            in eventMatches[index]["alliances"]["red"]["team_keys"]
        ):

            #Begin corrections
            if entry[27] != eventMatches[index]["alliances"][alliance]["score"]:
                print(
                    "Wrong score in match {}: It's {} but it should be {}.".format(
                        entry[0],
                        entry[27],
                        eventMatches[index]["alliances"][alliance]["score"],
                    )
                )
                df.loc[k, "Final Alliance Score"] = eventMatches[index]["alliances"][alliance]["score"]
            
            if entry[16] != len(eventMatches[index]["score_breakdown"][alliance]["links"]):
                print("Wrong link count in match {}: It's {} but it should be {}.".format(
                        entry[0],
                        entry[16],
                        len(eventMatches[index]["score_breakdown"][alliance]["links"]),
                    )
                )
                df.loc[k, "Teleop Links"] = len(eventMatches[index]["score_breakdown"][alliance]["links"])
        else:
            raise ValueError(
                "Bad team number. match {}; team {}.".format(entry[0], entry[1])
            )
    df.to_excel(os.path.join(params.download_folder, eventCode + ".xlsx"), index=False)

combineDataRange(20231010, 20231012)
