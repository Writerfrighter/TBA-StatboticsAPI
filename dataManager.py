import pandas as pd
import TBA
import params
import os


def combineEventRange(eventCode, correctData=True):
    event = TBA.fetchEventDate(eventCode).replace("-", "").split(" ")
    print(event)
    combineDataRange(int(event[0]), int(event[1]), fileName=eventCode)
    if correctData:
        completeData(eventCode)


def combineDataRange(minDate, maxDate, fileName=None):
    """Combines a data range given a max and min date"""
    files = []
    for filename in os.listdir(params.upload_folder):
        f = os.path.join(params.upload_folder, filename)
        if os.path.isfile(f):
            try:
                if (
                    int(filename.rsplit("_", 1)[1][:8:]) >= minDate
                    and int(filename.rsplit("_", 1)[1][:8:]) <= maxDate
                ):
                    files.append(filename)

            except:
                pass
        else:
            "Hold up, there's a directory in here?"
    if fileName == None:
        combineData(files, str(minDate) + str(maxDate) + "scouting_data.xlsx")
    else:
        combineData(files, fileName + ".xlsx")


def combineData(files, filename):
    """Combines a given list of files and writes the result it to processed_data as a xlsx"""
    extension = files[0].rsplit(".", 1)[1]
    if extension == "xlsx":
        df = pd.read_excel(
            os.path.join(params.upload_folder, files[0]), index_col=False
        )

    elif extension == "csv":
        df = pd.read_csv(os.path.join(params.upload_folder, files[0]), index_col=False)
    else:
        raise TypeError("Wrong file type")

    for file in files[1::]:
        extension = file.rsplit(".", 1)[1]
        if extension == "xlsx":
            df = pd.concat(
                [
                    df,
                    pd.read_excel(
                        os.path.join(params.upload_folder, file), index_col=False
                    ),
                ],
                ignore_index=True,
            )
        elif extension == "csv":
            df = pd.concat(
                [
                    df,
                    pd.read_csv(
                        os.path.join(params.upload_folder, file), index_col=False
                    ),
                ],
                ignore_index=True,
            )
        else:
            raise TypeError("Wrong file type")

    df.to_excel(os.path.join(params.download_folder, filename), index=False)


def completeData(eventCode):
    """Completes scouting data using TBA data for the event"""
    df = pd.read_excel("{}\{}.xlsx".format(params.download_folder, eventCode))
    eventMatches = TBA.fetchEventMatches(eventCode)

    stats = [0, 0, 0]  # List for storing accuracy statistics

    for k, entry in enumerate(df.values[::]):
        index = [
            i for i, j in enumerate(eventMatches) if j["match_number"] == entry[0]
        ][0]
        alliance = entry[3][-3::-1][::-1].lower()
        # Check if the team numbers are correct, or else we can't continue
        if (
            "frc" + str(entry[1])
            not in eventMatches[index]["alliances"][alliance]["team_keys"]
        ):
            team_replace = fixInvalidTeamNumber(
                eventMatches[index]["key"], str(entry[1]), alliance
            )
            if not params.auto_replace_team_names:
                print(
                    "Invalid team number was found in match {}, team number {}, our algorithm has found a possible replacement of {}. Do you accept this change? (y/n)".format(
                        eventMatches[index]["match_number"], entry[1], team_replace
                    )
                )
                answer = input().lower()
            else:
                print(
                    "Wrong team number was found in match {}: Team number {}, replacement of {} was found. Autoaccept has been enabled.".format(
                        eventMatches[index]["match_number"], entry[1], team_replace
                    )
                )
            if params.auto_replace_team_names:
                df.loc[k, "Team Number"] = int(team_replace)
            elif answer == "y":
                df.loc[k, "Team Number"] = int(team_replace)
            else:
                df.loc[k, "Team Number"] = int(input("What is your replacement? \n"))
            stats[0] += 1
        # Begin corrections
        if entry[27] != eventMatches[index]["alliances"][alliance]["score"]: #Final score
            print(
                "Wrong score in match {}: It's {} but it should be {}.".format(
                    entry[0],
                    entry[27],
                    eventMatches[index]["alliances"][alliance]["score"],
                )
            )
            stats[1] += abs(
                eventMatches[index]["alliances"][alliance]["score"] - entry[27]
            )
            df.loc[k, "Final Alliance Score"] = eventMatches[index]["alliances"][
                alliance
            ]["score"]

        if entry[16] != len(eventMatches[index]["score_breakdown"][alliance]["links"]): # Link count
            print(
                "Wrong link count in match {}: It's {} but it should be {}.".format(
                    entry[0],
                    entry[16],
                    len(eventMatches[index]["score_breakdown"][alliance]["links"]),
                )
            )
            stats[2] += abs(
                len(eventMatches[index]["score_breakdown"][alliance]["links"])
                - entry[16]
            )
            df.loc[k, "Teleop Links"] = len(
                eventMatches[index]["score_breakdown"][alliance]["links"]
            )
        #Bonus corrections
        for bonus in params.bonuses:
            if bool(entry[bonus[0]]) != eventMatches[index]["score_breakdown"][alliance][bonus[1]]: # Bonus
                print(
                    "Wrong {} in match {}: It's {} but it should be {}.".format(
                        bonus[2],
                        entry[0],
                        entry[bonus[0]],
                        eventMatches[index]["score_breakdown"][alliance][bonus[1]],
                    )
                )
                # stats[1] += 1
    
                df.loc[k, bonus[2]] = eventMatches[index]["score_breakdown"][alliance][bonus[1]]


    df.to_excel(os.path.join(params.download_folder, eventCode + ".xlsx"), index=False)
    print(
        f"Correction statistics:\nTeam numbers entered incorrectly: {stats[0]}\nMean score deviation: {stats[1]/len(df.values)}\nMean link count deviation: {stats[2]/len(df.values)}"
    )


def fixInvalidTeamNumber(matchKey, givenTeamNumber, alliance):
    givenTeamNumber = str(givenTeamNumber)
    data = TBA.fetchMatchData(matchKey)
    teams = data["alliances"][alliance]["team_keys"]

    matches = []
    for i in range(len(teams)):
        matches.append(0)
        teams[i] = teams[i][3::]
        for j in range(len(teams[i])):
            try:
                if teams[i][j] == givenTeamNumber[j]:
                    matches[i] += 1
            except:
                matches[i] -= 1
    if max(matches) >= params.team_number_threshold:
        return teams[matches.index(max(matches))]
    else:
        raise ValueError(
            "Bad team number in match {}, team number {} fixInvalid could not identity the correct one.".format(
                matchKey, givenTeamNumber
            )
        )

combineEventRange("2023pncmp")
