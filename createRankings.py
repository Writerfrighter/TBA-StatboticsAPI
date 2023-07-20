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

def normalizeData(data):
    mean_data = sum(data.values())/len(data)
    data_normalized = {team_number[3::]: data[team_number] - mean_data for team_number in data}
    max_data = max(data_normalized.values())
    min_data = abs(min(data_normalized.values()))
    max_or_min_data = max([max_data, min_data])

    for team in data_normalized:
        data_normalized[team] /= max_or_min_data
    
    return data_normalized

def createRankings(event, useOPR, useCCWMS, useOverall_EPA, useAuto_EPA, useTeleOp_EPA, useEndgame_EPA):

    if TBA.checkAPIStatus() != True:
        if not useOPR and not useCCWMS and not useOverall_EPA and not useAuto_EPA and not useTeleOp_EPA and not useEndgame_EPA:
            return "Nothing was selected"
        API_Response = TBA.fetchEventOprs(event)
        
        if useOPR: 
            oprs = API_Response["oprs"]
            oprs_normalized = normalizeData(oprs)
        else: oprs_normalized = dict.fromkeys(np.arange(0,len(API_Response["oprs"])+1), 0)
        if useCCWMS: 
            ccwms = API_Response["ccwms"]
            ccwms_normalized = normalizeData(ccwms)
        else: ccwms_normalized = dict.fromkeys(np.arange(0,len(API_Response["ccwms"])+1), 0)

        team_names = {}
        if not useOverall_EPA: epas_max = dict.fromkeys(np.arange(0,len(oprs)+1), 0)
        else: epas_max = {}
        if not useAuto_EPA: auto_epas_max = dict.fromkeys(np.arange(0,len(oprs)+1), 0)
        else: auto_epas_max = {}
        if not useTeleOp_EPA: teleop_epas_max = dict.fromkeys(np.arange(0,len(oprs)+1), 0)
        else: teleop_epas_max = {}
        if not useEndgame_EPA: endgame_epas_max = dict.fromkeys(np.arange(0,len(oprs)+1), 0)
        else: endgame_epas_max = {}
        
        i = 0

        tofetch = ["team_name"]

        if useOverall_EPA: tofetch.append('epa_max')
        if useAuto_EPA: tofetch.append('auto_epa_max')
        if useTeleOp_EPA: tofetch.append('teleop_epa_max')
        if useEndgame_EPA: tofetch.append('endgame_epa_max')

        for team in oprs:
            i+=1
            
            print("Fetching EPA data for team {} of {}...".format(i, len(oprs)), end = "\r")
            team_query = {}
            #print(team)
            team_query = sb.get_team_event(int(team[3::]), event, tofetch) # type: ignore
            
            team_names[team] = team_query["team_name"]
            if useOverall_EPA: epas_max[team] = float(team_query["epa_max"])
            if useAuto_EPA: auto_epas_max[team] = float(team_query["auto_epa_max"])
            if useTeleOp_EPA: teleop_epas_max[team] = float(team_query["teleop_epa_max"])
            if useEndgame_EPA: endgame_epas_max[team] = float(team_query["endgame_epa_max"])

        print("Fetching EPA data for team {} of {}".format(len(oprs), len(oprs)))
        if useOverall_EPA: epa_max_normalized = normalizeData(epas_max)
        else: epa_max_normalized = epas_max
        if useAuto_EPA: auto_epa_max_normalized = normalizeData(auto_epas_max)
        else: auto_epa_max_normalized = auto_epas_max
        if useTeleOp_EPA: teleop_epa_max_normalized = normalizeData(teleop_epas_max)
        else: teleop_epa_max_normalized = teleop_epas_max
        if useEndgame_EPA: endgame_epa_max_normalized = normalizeData(endgame_epas_max)
        else: endgame_epa_max_normalized = endgame_epas_max

        names = ["{} ({})".format(team_names[team_number], team_number[3::]) for team_number in team_names.keys()]

        
        scores = [(opr * 2) + (ccwm * 2) + epa_max + auto_epa_max + teleop_epa_max + endgame_epa_max for (opr, ccwm, epa_max, auto_epa_max, teleop_epa_max, endgame_epa_max) in zip(oprs_normalized.values(), ccwms_normalized.values(), epa_max_normalized.values(), auto_epa_max_normalized.values(), teleop_epa_max_normalized.values(), endgame_epa_max_normalized.values())]
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

        names_joined = "~".join(map(str, team_names))
        team_scores = "~".join(map(str, team_scores))
        return names_joined + "=" + team_scores
    
    else:
        return "The Blue Alliance API is down."


