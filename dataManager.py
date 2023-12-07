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

    stats = [0, 0]  # List for storing accuracy statistics

    for i in range(
        len(params.location_dependent_comparisions)
        + len(params.length_of_list_comparisons)
        + len(params.value_comparisons)
        + len(params.bonuses)
    ):
        stats.append(0)

    for k, entry in enumerate(df.values[::]):
        index = [
            i for i, j in enumerate(eventMatches) if j["match_number"] == entry[0]
        ][
            0
        ]  # Grab the index of event in TBA
        alliance = entry[3][-3::-1][::-1].lower()
        # Check if the team numbers are correct
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

        score = eventMatches[index]["alliances"][alliance]["score"]
        if entry[27] != score:  # Final score correction
            print(
                "Wrong score in match {}: It's {} but it should be {}.".format(
                    entry[0],
                    entry[27],
                    score,
                )
            )
            stats[1] += abs(score - entry[27])
            df.loc[k, "Final Alliance Score"] = eventMatches[index]["alliances"][
                alliance
            ]["score"]

        robot_position = (
            eventMatches[index]["alliances"][alliance]["team_keys"].index(
                "frc" + str(df.loc[k, "Team Number"])
            )
            + 1
        )

        # Location Dependent Comparisons
        for i, correction in enumerate(params.location_dependent_comparisions):
            value = eventMatches[index]["score_breakdown"][alliance][
                correction["tba_format_name"].replace("%", str(robot_position))
            ]
            if correction["xlsx_tba_pairs"][entry[correction["index"]]] != value:
                print(
                    "Wrong {} value in match {}: It's {} but it should be {}.".format(
                        correction["xlsx_name"],
                        entry[0],
                        correction["xlsx_tba_pairs"][entry[correction["index"]]],
                        value,
                    )
                )
                correct = list(correction["xlsx_tba_pairs"].keys())[
                    list(correction["xlsx_tba_pairs"].values()).index(value)
                ]  # Dict value to key
                stats[2 + i] += 1
                df.loc[k, correction["xlsx_name"]] = correct

        # Length of List corrections
        for i, correction in enumerate(params.length_of_list_comparisons):
            length = len(
                eventMatches[index]["score_breakdown"][alliance][correction["tba_name"]]
            )
            if entry[correction["index"]] != length:
                print(
                    "Wrong {} count in match {}: It's {} but it should be {}.".format(
                        correction["xlsx_name"],
                        entry[0],
                        entry[correction["index"]],
                        length,
                    )
                )
                stats[2 + len(params.location_dependent_comparisions) + i] += abs(
                    length - entry[correction["index"]]
                )
                df.loc[k, correction["xlsx_name"]] = length

        # Value comparisons
        for correction in params.value_comparisons:
            value = eventMatches[index]["score_breakdown"][alliance][
                correction["tba_name"]
            ]
            csv_total = 0
            for key in correction["xlsx_data"]:
                csv_total += df.loc[k, key["xlsx_name"]]
            if csv_total != length:
                print(
                    "Wrong {} in match {}: It's {} but it should be {}.".format(
                        correction["tba_name"],
                        entry[0],
                        csv_total,
                        value,
                    )
                )

                if len(correction["xlsx_data"]) == 1:
                    df.loc[k, correction["xlsx_data"][0]["xlsx_name"]] = length

        # Bonus corrections
        for bonus in params.bonuses:
            if (
                bool(entry[bonus["index"]])
                != eventMatches[index]["score_breakdown"][alliance][bonus["tba_name"]]
            ):  # Bonus
                print(
                    "Wrong {} in match {}: It's {} but it should be {}.".format(
                        bonus["xlsx_name"],
                        entry[0],
                        entry[bonus["index"]],
                        eventMatches[index]["score_breakdown"][alliance][
                            bonus["tba_name"]
                        ],
                    )
                )
                # stats[1] += 1

                df.loc[k, bonus["xlsx_name"]] = eventMatches[index]["score_breakdown"][
                    alliance
                ][bonus["tba_name"]]

    df.to_excel(os.path.join(params.download_folder, eventCode + ".xlsx"), index=False)
    print(
        f"\nCorrection statistics:\nTeam numbers entered incorrectly: {stats[0]}\nMean score deviation: {stats[1]/len(df.values)}\nMean link count deviation: {stats[2]/len(df.values)}"
    )
    # TODO: Get metric system worked out


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
        answer = input(
            "Bad team number in match {}, team number {}, a suggested chance of {} was found that does not meet the minimum threshold do you accept the change? (y/n)".format(
                matchKey, givenTeamNumber, teams[matches.index(max(matches))]
            )
        ).lower()
        if answer == "y":
            return teams[matches.index(max(matches))]
        else:
            raise ValueError(
                "Bad team number in match {}, team number {} fixInvalid could not identity the correct team number.".format(
                    matchKey, givenTeamNumber
                )
            )


combineEventRange("2023pncmp")
