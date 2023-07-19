#Formula from 8248, Ember

#External imports
import matplotlib.pyplot as plt
import pandas as pd
import statbotics
import numpy as np
import random
#Local imports
import TBA

sb = statbotics.Statbotics()

season = 2023
team = 492
lable = None
competition = 0

def getTeamAndSeasonData():
    global season, team
    try: 
        season = int(input("Enter the current season your scouting for: \n"))
        team = int(input("Enter your team number: \n"))
    except:
        print("That's not a valid integer")
        getTeamAndSeasonData()
        return
    
def UseEndgameEPA():
    global useEndgame_EPA
    response = input("Would you like to use the Endgame EPA for this query (y/n): \n")
    
    if response.lower() == 'y':
        useEndgame_EPA = True
    elif response.lower() == 'n':
        useEndgame_EPA = False
    else:
        print("That wasnt either \'y\' or \'n\'.")
        UseEndgameEPA()

def GetCompetition():
    global competition,lable

    competitions = TBA.fetchEventsForTeam(team, season)

    print("Select the competition your scouting for:")
        
    for i in range(len(competitions)):
        print(str(i+1) + ".", competitions[i][0])

    competition = input()

    try: 
        competition = competitions[int(competition) - 1][1]
        lable = competitions[int(competition) - 1][0]

    except:
        for i in range(len(competitions)):
            if competition == competitions[i][0] or competition == competitions[i][1]:
                competition = competitions[i][1]
                lable = competitions[i][0]
                return
            
        print("That's not a valid selection")
        GetCompetition()
    
def normalizeData(data):
    mean_data = sum(data.values())/len(data)

    data_normalized = {team_number[3::]: data[team_number] - mean_data for team_number in data}
    max_data = max(data_normalized.values())
    min_data = abs(min(data_normalized.values()))
    max_or_min_data = max([max_data, min_data])

    for team in data_normalized:
        data_normalized[team] /= max_or_min_data
    
    return data_normalized

def createRankings():
    global useEndgame_EPA

    if TBA.checkAPIStatus() != True:
        
        getTeamAndSeasonData()
        GetCompetition()
        UseEndgameEPA()
        print("Fetching TBA OPR Data...")
        API_Response = TBA.fetchEventOprs(competition)
        oprs = API_Response["oprs"]
        ccwms = API_Response["ccwms"]

        oprs_normalized = normalizeData(oprs)
        
        ccwms_normalized = normalizeData(ccwms)
        
        team_names = {}
        epas_max = {}
        auto_epas_max = {}
        teleop_epas_max = {}
        endgame_epas_max = {}
        
        i = 0
        for team in oprs:
            i+=1
            
            print("Fetching EPA data for team {} of {}...".format(i, len(oprs)), end = "\r")
            team_query = {}
            #print(team)
            if useEndgame_EPA: team_query = sb.get_team_event(int(team[3::]), competition, ["team_name", "epa_max", "auto_epa_max", "teleop_epa_max", "endgame_epa_max"]) # type: ignore
            else: team_query = sb.get_team_event(int(team[3::]), competition, ["team_name", "epa_max", "auto_epa_max", "teleop_epa_max"]) # type: ignore
            team_names[team] = team_query["team_name"]
            epas_max[team] = float(team_query["epa_max"])
            auto_epas_max[team] = float(team_query["auto_epa_max"])
            teleop_epas_max[team] = float(team_query["teleop_epa_max"])
            if useEndgame_EPA: endgame_epas_max[team] = float(team_query["endgame_epa_max"])

        print("Fetching EPA data for team {} of {}".format(len(oprs), len(oprs)))
        epa_max_normalized = normalizeData(epas_max)
        auto_epa_max_normalized = normalizeData(auto_epas_max)
        teleop_epa_max_normalized = normalizeData(teleop_epas_max)
        if useEndgame_EPA: endgame_epa_max_normalized = normalizeData(endgame_epas_max)

        names = ["{} ({})".format(team_names[team_number], team_number[3::]) for team_number in team_names.keys()]
        if useEndgame_EPA: scores = [(opr * 2) + (ccwm * 2) + epa_max + auto_epa_max + teleop_epa_max + endgame_epa_max for (opr, ccwm, epa_max, auto_epa_max, teleop_epa_max, endgame_epa_max) in zip(oprs_normalized.values(), ccwms_normalized.values(), epa_max_normalized.values(), auto_epa_max_normalized.values(), teleop_epa_max_normalized.values(), endgame_epa_max_normalized.values())]
        else: scores = [(opr * 2) + (ccwm * 2) + epa_max + auto_epa_max + teleop_epa_max for (opr, ccwm, epa_max, auto_epa_max, teleop_epa_max) in zip(oprs_normalized.values(), ccwms_normalized.values(), epa_max_normalized.values(), auto_epa_max_normalized.values(), teleop_epa_max_normalized.values())]
        score_and_names = [(score, name) for (score, name) in zip(scores, names) ]
        
        #Shhhhh
        #for i in range(len(score_and_names)):
        #    if score_and_names[i][1].__contains__("Titan Robotics Club"):
        #        score_and_names[i][0] = max(scores)+abs(min(scores))+ random.random() * 2

        score_and_names.sort(reverse=True)
        print("Ranked teams on OPR and EPA")
        print(*score_and_names, sep="\n")
        

        team_names = [team for (score, team) in score_and_names]
        team_scores = [score for (score, team) in score_and_names]
        min_score = min(team_scores)
        for i in range(len(team_scores)):
            team_scores[i] += abs(min_score)

        fig, ax = plt.subplots()
        red = ["tab:red" for i in range(15)]
        blue = ["tab:blue" for i in range(len(team_scores)-15)]
        bar_colors = red + blue
        y_pos = np.arange(len(team_names))
        hbars = ax.barh(y_pos, team_scores, color = bar_colors, align='center')
        ax.set_yticks(y_pos, labels=team_names)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Normalized Score')
        ax.set_title("{} Scouting Ranks".format(lable))
        # Label with specially formatted floats
        ax.bar_label(hbars, fmt='%.2f')
        ax.set_xlim(0, int(max(team_scores)) + 2)
        plt.subplots_adjust(.3)
        plt.show()
    else:
        print("The Blue Alliance API is down.")


