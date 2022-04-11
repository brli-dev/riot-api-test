# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 16:03:35 2021

@author: Brian
"""


import roleml

from datetime import timedelta

import time

import cassiopeia as cass

import json 

import collections

def getAPI_key():
    f = open("./api_key.txt", "r")
    return f.read()

def analyzeMatch(match, summoner):
    p = match.participants[summoner]
    
    roleml.change_role_formatting('full')
    match.timeline.load()
    
    roleml.predict(match.to_dict(), match.timeline.to_dict(), True)
    roleml.add_cass_predicted_roles(match)
    role = p.predicted_role
    
    
    champ = champList[str(p.champion.id)]
    
    return role, champ




def get_challenger_data():
    
    data = cass.get_challenger_league(cass.Queue.ranked_solo_fives)
    
    summonerNames = []
    role_dict = []
    champ_dict = []
    for item in data.entries:
        if data.entries.index(item) %10 == 0:
            print('\nCURRENT LADDER ENTRY= ', data.entries.index(item))
        elif data.entries.index(item)>10:
            pass
        else:
            summonerNames.append(item.summoner.name)
            summoner= item.summoner
            match_history = summoner.match_history(queues={cass.Queue.ranked_solo_fives}, begin_index=0, end_index=10)
            
            roles = []
            champs = []
            for match in match_history:
                if match.is_remake:
                    pass
                elif match.duration < timedelta(minutes=15, seconds= 30):
                    pass
                else:
                    role, champ = analyzeMatch(match, summoner)
                    roles.append(role)
                    champs.append(champ)
                    
                    
                    
                    
            main_role= collections.Counter(roles).most_common(1)[0]
            main_champ= collections.Counter(champs).most_common(1)[0]
    
            role_dict.append(main_role)
            champ_dict.append(main_champ)

                    
    return summonerNames, role_dict, champ_dict
    
    
def write_output(summonerNames, role_dict, champ_dict):
    
    print("\nSummoner name, (Role, games), (Champ, games)")
    for i in range(0, len(summonerNames)):
        print(summonerNames[i], "//", role_dict[i], "//", champ_dict[i])
    
    
    
#%% Main run
if __name__ == "__main__":
    start_time = time.time()
    
    cass.set_riot_api_key(getAPI_key())  # This overrides the value set in your configuration/settings.
    cass.set_default_region("KR")
    

    with open('championsNew.json', 'r') as champList_file:
        champList = json.load(champList_file)
        champList_file.close()
        champList = champList["keys"]

    
    summonerNames, role_dict, champ_dict= get_challenger_data()
    write_output(summonerNames, role_dict, champ_dict)
    
    print("\n--- %s seconds ---" % (time.time() - start_time))
    
    

