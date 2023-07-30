#Formula from 8248, Ember

#External imports
import matplotlib.pyplot as plt
import pandas as pd
import statbotics
import numpy as np
import concurrent.futures
import logging
import json
#Local imports
import TBA

logging.basicConfig(filename="main.log", format='%(asctime)s %(message)s', filemode='w')
 
# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)

sb = statbotics.Statbotics()

def normalizeData(data):
    data = {key: val for key, val in sorted(data.items(), key = lambda ele: ele[0])}
    mean_data = sum(data.values())/len(data)
    data_normalized = {team_number[3::]: data[team_number] - mean_data for team_number in data}
    max_data = max(data_normalized.values())
    min_data = abs(min(data_normalized.values()))
    max_or_min_data = max([max_data, min_data])

    for team in data_normalized:
        data_normalized[team] /= max_or_min_data
    return data_normalized

def fetchTeam_Threaded(name, team, event, tofetch, useOverall_EPA, useAuto_EPA, useTeleOp_EPA, useEndgame_EPA):
    logging.info("Thread %s: starting", name)
    team_query = {}
    team_query = sb.get_team_event(int(team[3::]), event, tofetch) # type: ignore
    logging.debug("Thread %s: finished API Fetch", name)
    team_names[team] = team_query["team_name"]
    if useOverall_EPA: epas_max[team] = float(team_query["epa_max"])
    if useAuto_EPA: auto_epas_max[team] = float(team_query["auto_epa_max"])
    if useTeleOp_EPA: teleop_epas_max[team] = float(team_query["teleop_epa_max"])
    if useEndgame_EPA: endgame_epas_max[team] = float(team_query["endgame_epa_max"])
    logging.info("Thread %s: finished", name)
    
def createRankings(event, useOPR, useCCWMS, useOverall_EPA, useAuto_EPA, useTeleOp_EPA, useEndgame_EPA):
    logger.info("Request came in for %s.", event)
    if TBA.checkAPIStatus() != True:
        if not useOPR and not useCCWMS and not useOverall_EPA and not useAuto_EPA and not useTeleOp_EPA and not useEndgame_EPA:
            return "Nothing was selected"
        API_Response = TBA.fetchEventOprs(event)

        team_count = len(API_Response["oprs"])

        if useOPR: 
            oprs = API_Response["oprs"]
            oprs_normalized = normalizeData(oprs)
        else: oprs_normalized = dict.fromkeys(np.arange(0,team_count+1), 0)
        if useCCWMS: 
            ccwms = API_Response["ccwms"]
            ccwms_normalized = normalizeData(ccwms)
        else: ccwms_normalized = dict.fromkeys(np.arange(0,team_count+1), 0)

        global team_names, epas_max, auto_epas_max, teleop_epas_max, endgame_epas_max
        team_names = {}

        if not useOverall_EPA: epas_max = dict.fromkeys(np.arange(0,team_count+1), 0)
        else: epas_max = {}
        if not useAuto_EPA: auto_epas_max = dict.fromkeys(np.arange(0,team_count+1), 0)
        else: auto_epas_max = {}
        if not useTeleOp_EPA: teleop_epas_max = dict.fromkeys(np.arange(0,team_count+1), 0)
        else: teleop_epas_max = {}
        if not useEndgame_EPA: endgame_epas_max = dict.fromkeys(np.arange(0,team_count+1), 0)
        else: endgame_epas_max = {}

        tofetch = ["team_name"]

        if useOverall_EPA: tofetch.append('epa_max')
        if useAuto_EPA: tofetch.append('auto_epa_max')
        if useTeleOp_EPA: tofetch.append('teleop_epa_max')
        if useEndgame_EPA: tofetch.append('endgame_epa_max')

        logging.info("Main: beginning Statbotics API fetch...") 


        with concurrent.futures.ThreadPoolExecutor(max_workers=team_count) as executer: 
            executer.map(fetchTeam_Threaded, range(team_count), oprs.keys(), [event] * team_count, [tofetch] * team_count, [useOverall_EPA] * team_count, [useAuto_EPA] * team_count, [useTeleOp_EPA] * team_count, [useEndgame_EPA] * team_count)

        logging.info("Main: finished Statbotics API fetch")

        team_names = {key: val for key, val in sorted(team_names.items(), key = lambda ele: ele[0])}

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
        # print("Ranked teams on OPR and EPA")
        # print(*score_and_names, sep="\n")
        

        team_names = [team for (score, team) in score_and_names]
        team_scores = [score for (score, team) in score_and_names]
        min_score = min(team_scores)
        for i in range(len(team_scores)):
            team_scores[i] += abs(min_score) + 0.02

        return json.dumps([team_names, team_scores])
    
    else:
        return "The Blue Alliance API is down."