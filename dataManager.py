import pandas as pd
import TBA
import params
import os


def combineDataRange(minDate, maxDate):
    files = []
    for filename in os.listdir(params.upload_folder):
        f = os.path.join(params.upload_folderr, filename)
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

    df.to_excel(os.path.join("combined_data", filename))

def completeData(eventCode):
    df = pd.read_excel("{}\{}.xlsx".format(params.download_folder, eventCode))
    eventMatches = TBA.fetchEventMatches(eventCode)
    # for df in eventMatches:
    #     if event['actual_time'] != None:
    #         match = df.loc[df['Match Number'] == event['match_number']]
    #         if not match.empty:
    #             t = match.loc[match['Team Number'] == 492]
    #             if not t.empty: print(match.loc[match['Team Number'] == 492])

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


def getDataAccuracy():
    df = pd.read_excel("{}\BordieData.xlsx".format(params.download_folder))
    print(df)

    eventMatches = TBA.fetchEventMatchs("2023brd")
    print(eventMatches)
    for event in eventMatches:
        if event["actual_time"] == None:
            pass
        else:
            match = df.loc[df["Match Number"] == event["match_number"]]
            if match["Endgame Sustainbility Bonus"] == event["Endgame"]:
                pass


completeData("2023brd")
