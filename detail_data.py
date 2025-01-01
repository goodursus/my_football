from plotly.subplots import make_subplots
import plotly.graph_objs as go
import my_lib as mb
import pandas as pd
import re
from decimal import Decimal, getcontext
#from dash import dash_table
from dash.dash_table.Format import Group
#from dash.exceptions import PreventUpdate
import jmespath
#import random
#import test_total_progress as mp
#import plotly.offline as pyo
#import plotly.io as pio
import os
#import sys
#import random
import time
import datetime
#import pytz
#import json
#import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
#import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
#from collections import defaultdict
import numpy as np
#import math
import itertools
import re
import logging
import copy

country       = ''
league        = 0
season        = 0
total_rounds  = 0
current_round = 1
errors        = False
fig           = go.Figure()
fig_height    = 300

sorted_team_list = []

graph    = ''

scored_majority = [[],[],[]]
scored_minority = [[],[],[]]
#missed_majority = []
#missed_minority = []

arr_type_events = ["Goal", "Card", "subst", "Var"]

delta_annotation_goals = -5
delta_annotation_score = 5
delta_annotation_team  = 45

arr_dimension  = []
team_dimension = []
team_arr       = []
y_value_all    = []

all_marker_opacity                       = []
all_marker_opacity_goal                  = []
all_marker_opacity_card                  = []
all_marker_opacity_subst                 = []
all_marker_opacity_var                   = []
    
all_marker_opacity_normal_scored         = []
all_marker_opacity_penalty_scored        = []
all_marker_opacity_missed_penalty_scored = []
all_marker_opacity_own_goal_scored       = []
all_marker_opacity_extra_goal            = []
all_marker_opacity_majority_scored       = []
all_marker_opacity_minority_scored       = []

nochange_opacity = []
opacity      = []
extra_events = []

target_annotation_goals   = 'goals'
target_annotation_normal  = 'normal'
target_annotation_penalty = 'penalty'
target_annotation_mis_pen = 'mis_pen'
target_annotation_own     = 'own'
target_annotation_extra   = 'extra'
target_annotation_maj     = 'majority'
target_annotation_min     = 'minoriyt'
target_annotation_card    = 'card'
target_annotation_subst   = 'subst'
target_annotation_var     = 'var'
target_annotation_score   = 'score'
target_annotation_team    = 'team'
target_annotation_team_score = 'team_score'

range_season = {}

count_games_load = 0

global_time_request = time.time()

def get_list_games(country, league, season, team):

    global current_round

    round  = 1

    current_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    data_json = mb.get_fixture_league(country, league, season)        

    if type(data_json[0]) == str: 
#        print(data_json[0])
        errors = True
        return data_json[0]

    list_fields_home = '''{Round: league.round, 
                    Team_id_home: teams.home.id, 
                    Name_home:    teams.home.name, 
                    Team_id_away: teams.away.id,
                    Name_away: teams.away.name, 
                    Game_id:      fixture.id, 
                    Date:         fixture.date,
                    Score_home:   score.fulltime.home,
                    Score_away:   score.fulltime.away}
                    '''
    list_fields_away = '''{Round: league.round, 
                    Team_id_home: teams.home.id, 
                    Name_home:    teams.home.name, 
                    Team_id_away: teams.away.id,
                    Name_away: teams.away.name, 
                    Game_id: fixture.id, 
                    Date: fixture.date,
                    Score_home:   score.fulltime.home,
                    Score_away:   score.fulltime.away}
                        '''

    home_query = 'response[?teams.away.id==`' + str(team) + '` && contains(league.round, `Regular Season`) && fixture.status.short ==`FT` && fixture.date < `' + format(current_date) + '`].' + list_fields_home
    away_query = 'response[?teams.home.id==`' + str(team) + '` && contains(league.round, `Regular Season`) && fixture.status.short ==`FT` && fixture.date < `' + format(current_date) + '`].' + list_fields_away
    home_results = jmespath.search(home_query, data_json[0])
    away_results = jmespath.search(away_query, data_json[0])
    merged_results = home_results + away_results


    if len(merged_results) == 0:
#        print("Season is empty.")
        results_round = ''
    else:    
        for round in merged_results:
            round['Round'] = int(re.findall(r'\d+', round['Round'])[0])

        results_round = sorted(merged_results, key=lambda x: x["Round"])

    return results_round

def get_games_goals(list_games, league, season, team, arr_type_events):

    global total_rounds
    global current_round
    global errors

    global count_games_load 
    
    detail_scored      = []
    detail_missed      = []
    detail_scored_all  = []
    detail_missed_all  = []

    data_detail        = []
    data_card          = []

    detail_for_type_scored    = []
    detail_for_type_missed    = []
#    my_dict = {}

    for type_event in arr_type_events:
        dictionary_scored = {type_event: ''}
        detail_for_type_scored.append(dictionary_scored)
    for type_event in arr_type_events:
        dictionary_missed = {type_event: ''}
        detail_for_type_missed.append(dictionary_missed)

#    access = mb.get_access(len(list_games))
    count_games_load = get_count_games_online(count_games_load, list_games, league, season, 'Statistic')
    access = mb.get_access(count_games_load)
#    access = True
        
    if not access:
        return(access)
#        sys.exit()

    max_time        = 60
#    max_iteration   = 10
    max_iteration   = 4
    start_time      = time.time()
    iteration_count = 0
    time_limit      = max_time/max_iteration

    for i in range(0,len(list_games)):

#        logging.debug('Round: ' + str(i + 1))

        game_id = list_games[i]['Game_id']    
        
        count         = 0
        cash          = True
        check_zero    = True

        while True:
            data_json_goal = mb.download_and_save(access, 
                                                'Statistic/' + str(country) + '/' + str(league) + '/' + str(season) + '/' + str(i+1) + '/' + str(game_id) + '.json', 
                                                'fixtures/events?fixture=' + str(game_id), cash, check_zero, range_season)
#            print('fixtures/events?fixture=' + str(game_id) + ': ' + data_json_goal[1])

            if type(data_json_goal[0]) == str: 
                print('errors = True: ', data_json_goal[0])
                errors = True
                return data_json_goal[0]
            
            result = jmespath.search('results', data_json_goal[0])
            # Выводим результат
            #print(result)

            if not result:
                print('Error download: ' + str(data_json_goal[1]))
                break
            
            if result > 0:
#                print('Загрузка данных Ок. Повтор загрузки игры ' + str(game_id) + ' не нужен')
#                print('massage:', data_json_goal[1])
                break

            count += 1
#            print('Повторная загрузка данных игры ' + str(game_id))

            cash = False

            if count == 2:
                break

    # выполнение цикла
        iteration_count += 1
        current_time = time.time() - start_time
        
#        print('current_time: ' + str(current_time))
        print('round: ' + str(i + 1))
        mb.info_request['round'] = i + 1
        mb.info_request['team'] = team

        #get detail data
        detail_text = '''Time:     time.elapsed, 
                        Extra:     time.extra, 
                        Team_id:   team.id,
                        Team:      team.name,
                        Detail:    detail, 
                        Player_id: player.id,
                        Player:    player.name,
                        Assist_id: assist.id,
                        Assist:    assist.name,
                        Type:      type,
                        Comment:   comments
                        ''' 
    
#            detail_query = 'response[?type == `'+ type_events + '` && team.id == `'+ str(team) + '`].{' + detail_text + '}'
        detail_query = 'response[?team.id == `'+ str(team) + '`].{' + detail_text + '}'

        detail_results = jmespath.search(detail_query, data_json_goal[0])

        if len(detail_results) == 0:
            detail_scored_all.append([0])
        else:
            detail_scored_all.append(detail_results)

#            detail_query = 'response[?type == `'+ type_events + '` && team.id != `'+ str(team) + '`].{' + detail_text + '}'
        detail_query = 'response[?team.id != `'+ str(team) + '`].{' + detail_text + '}'
        
        detail_results = jmespath.search(detail_query, data_json_goal[0])

        if len(detail_results) == 0:
            detail_missed_all.append([0])
        else:
            detail_missed_all.append(detail_results)

#    current_dimension = []

    empty_detail       = {'Time':     -100, 
                        'Extra':     0, 
                        'Team_id':   0,
                        'Team':      None,
                        'Detail':    None, 
                        'Player_id': 0,
                        'Player':    None,
                        'Assist_id': 0,
                        'Assist':    None,
                        'Type':      None,
                        'Comment':   None}
    
    detail_missed = [[d for d in arr if d.get('Type') == 'Goal'] for arr in detail_missed_all]
    
    for i in range(len(detail_scored_all)):
        detail_scored_all[i].extend(detail_missed[i])

    max_length = 0

    for sublist in detail_scored_all:
        sublist_length = len(sublist)
        max_length = max(max_length, sublist_length)

    for step in range(0, max_length + 1): # +1 для добавления еще одной пустой строки для красных карточек в majority.
    
        my_detail = []
        for round in range(0, current_round):
            if round < len(detail_scored_all):
                if 0 <= step < len(detail_scored_all[round]):  
                    my_detail.append(detail_scored_all[round][step])
                else:    
                    my_detail.append(empty_detail)
            else:    
                my_detail.append(empty_detail)

        data_detail.append(my_detail)

    detail_card = [[d for d in arr if d.get('Detail') == 'Red Card'] for arr in detail_missed_all]
    
    max_length_card = 0

    for sublist in detail_card:
        sublist_length = len(sublist)
        max_length_card = max(max_length_card, sublist_length)

    for step in range(0, max_length_card):
    
        my_detail = []
        for round in range(0, current_round):
            if round < len(detail_card):
                if 0 <= step < len(detail_card[round]):  
                    my_detail.append(detail_card[round][step])
                else:    
                    my_detail.append(empty_detail)
            else:    
                my_detail.append(empty_detail)

        data_card.append(my_detail)

#    print('Info_request: ', mb.info_request)

    return data_detail, data_card
#    return detail_for_type_scored, detail_for_type_missed, current_dimension

def arr_to_df(my_array, arr_dim, detail_dim):

    df = pd.DataFrame(columns=['val' + str(k) for k in range(detail_dim)])
    for i in range(arr_dim):
        row = pd.DataFrame({'val1': [[[my_array[i][j][0]] for j in range(arr_dim)] for i in range(arr_dim)],
                            'val2': [[[my_array[i][j][1]] for j in range(arr_dim)] for i in range(arr_dim)],
                            'val3': [[[my_array[i][j][2]] for j in range(arr_dim)] for i in range(arr_dim)]})
    df = df.append(row, ignore_index=True)    

    return df

def dict_to_df(my_dict):

    arr_keys = list(my_dict[0][0].keys())

    df = pd.DataFrame([[[item[arr_keys[keys]] for item in row] for keys in range(len(arr_keys))] for row in my_dict])

    df.columns = arr_keys

    #df = df.assign(x = list(range(1, total_rounds + 1)))
    df = df.assign(x = list(range(1, len(df) + 1)))

    return df

def not_equal_compositions(team, majority, df_detail):
    
    if majority:
        rival = 1 #красная у соперника
        own   = 0 #собственная красная 
    else:
        rival = 0
        own   = 1
                
    # In the majority
#    print('In the ' + str(majority))
    
#    all_cards = df_detail[rival][1]['Card'] 
    red_card_own     = []
    red_card_rival   = []
    arr_player       = []
    all_goals_scored = []
    all_goals_missed = []

#    current_round = 0
    for i, row in enumerate(df_detail):
        for j, round in enumerate(row):
            if round['Detail'] == 'Red Card':
                card_time = round['Time']
                if round['Team_id'] == team:
                    red_card_own.append([card_time,j])
                else:    
                    red_card_rival.append([card_time,j])
                
                player = round['Player']
                arr_player.append(player)

            elif round['Type'] == 'Goal':
                if round['Team_id'] == team:
                    all_goals_scored.append([round['Time'], j]) 
                else:
                    all_goals_missed.append([round['Time'], j])       

#    all_goals_scored = df_detail[0][0]['Goal'] #голы забитые
#    all_goals_missed = df_detail[1][0]['Goal'] #голы пропущенные 

    after_red_card_scored = []
    after_red_card_missed = []

    for k in range(len(red_card_own)):
        for i in range(len(all_goals_scored)):
            q = red_card_own[k][1]    
#            if all_goals_scored[i][q]['Time'] >= red_card[k][0]:
            if all_goals_scored[i][0] >= red_card_own[k][0]:
                after_red_card_scored.append([i,q])
#                print(after_red_card)

    for k in range(len(red_card_own)):
        for i in range(len(all_goals_missed)):
            q = red_card_own[k][1]    
#            if all_goals_missed[i][q]['Time'] >= red_card[k][0]:
            if all_goals_missed[i][0] >= red_card_own[k][0]:
                after_red_card_missed.append([i,q])
#                print(after_red_card)

    return red_card_own, after_red_card_scored, after_red_card_missed, arr_player   

def find_duplicate_indices(type, fig, sorted_team_list, dimension):
    
    global total_rounds
    global arr_type_events

    for t in range(len(sorted_team_list)):

        if t == 0:
            delta_team = 0
        else:    
            delta_team = sum(dimension[:t])

        arr_type = []
        count = 1
        for i, trace in enumerate(fig.data[delta_team:dimension[t] + delta_team]):
            sub_arr = []
            for j, symbol in enumerate(trace.marker.symbol):
#                if type == 'goal' and (symbol == 0 or symbol == 2 or symbol == 5 or symbol == 6 or symbol == 1 or symbol == 201):
                if symbol == 0 or symbol == 2 or symbol == 5 or symbol == 6:
                    sub_arr.append(trace.y[j])
                elif symbol == 1 or symbol == 201:
                    sub_arr.append(trace.y[j])
                else:
                    sub_arr.append(-100)

            arr_type.append(sub_arr)
            if count >= dimension[t]:
                break
            else:
                count += 1

        y = np.array(arr_type)
         
        result = []
        for column_index, column in enumerate(zip(*y)):
            my_column = list(column)
            column_result = index_column(my_column)
            result.append(column_result)

        delta = 0.1
        # Вывести результат
        for j, element in enumerate(result):
            if element:
                for duble in element:
                    count = len(duble) - 1
                    array = [round(i * delta * current_round/total_rounds, 2) for i in range(-count, count+1, 2)]
                    for k, row in enumerate(duble):
                        x_values  = fig.data[row + delta_team].x
#                        x_values  = [x for x in range(1, current_round + 1)]
                        new_x_values  = tuple( x + array[k] if i == j else x for i, x in enumerate(x_values))
                        fig.data[row + delta_team].x = new_x_values 

    return fig

def find_duplicate_indices_xaxis(map, marker_symbol, y_values, dim):
    
    global current_round

    count = 1
    
    delta = 0.1
    x_axis = [[i+1 for i in range(current_round)] for _ in range(len(y_values))]

    x_values  = [x for x in range(1, current_round + 1)]

    for t in range(len(dim)):
        if t == 0:
            offset = 0
            event = 0
        else:
            offset = sum(dim[:t])
            event = offset 

        result = []
        arr_events = []

        for i, trace in enumerate(itertools.islice(marker_symbol, offset, offset + dim[t]), start = offset):
            sub_arr = []
            for j, symbol in enumerate(trace):
                if symbol in map:
                    sub_arr.append(y_values[i][j])
                else:
                    sub_arr.append(-100)

            arr_events.append(sub_arr)

        y = np.array(arr_events)
            
        for column_index, column in enumerate(zip(*y)):
            my_column = list(column)
            column_result = index_column(my_column)
            result.append(column_result)

        # Вывести результат
        for i, element in enumerate(result):
            if element:
                for duble in element:
                    count = len(duble) - 1
                    array = [round(i * delta * current_round/total_rounds, 2) for i in range(-count, count+1, 2)]
                    for k, row in enumerate(duble):
                        x_axis[row + event][i] = x_values[i] + array[k]

    return x_axis

def upload_dump(fig, sorted_team_list, my_dict):

    for teams in sorted_team_list:
        
        team = teams['name']
        # Получение данных из fig.data
        data_x           = []
        data_y           = []
        data_marker      = []
        data_color       = []
        data_hover       = []

        for trace in fig.data:
            data_x.append(trace.x)
            data_y.append(trace.y)
            data_marker.append(trace.marker.symbol)
            data_color.append(trace.marker.color)
            data_hover.append(trace.hovertemplate)

        df_x      = pd.DataFrame(data_x)
        df_y      = pd.DataFrame(data_y)
        df_marker = pd.DataFrame(data_marker)
        df_color  = pd.DataFrame(data_color)
        df_hover  = pd.DataFrame(data_hover)

        with pd.ExcelWriter('Dumps/data_' + team + '.xlsx') as writer:        
            df_x.to_excel(writer, sheet_name='x', index=False)
            df_y.to_excel(writer, sheet_name='y', index=False)
            df_marker.to_excel(writer, sheet_name='marker_symbol', index=False)
            df_color.to_excel(writer, sheet_name='marker_color', index=False)
            df_hover.to_excel(writer, sheet_name='marker_hover', index=False)
            for key, value in my_dict.items():
                my_df = pd.DataFrame(value)
                my_df.to_excel(writer, sheet_name = key, index=False)

def index_column(data):
    tolerance = 5

    result = []
    my_result = []
    
    '''
    for i in range(len(data)):
        if data[i] > 0:
            group = []
            curr_val = data[i] 
            for j in range(len(data)):
                if data[j] > 0: 
                    value = data[j]
                    if i != j:
                        if abs(value - curr_val) <= tolerance:
                            group.append(value)
                    else:
                        if abs(value - curr_val) <= tolerance:
                            group.append(curr_val)
            result.append(group)   

    
    unique_lst = list(set(map(tuple, result)))

    my_result = [list(item) for item in unique_lst] 

    indexes = [[data.index(val) for val in group] for group in my_result]

    indexes = []
    for group in my_result:
        my_group = []
        ind   = -1
        for val in group:
            if ind != data.index(val):
                my_group.append(data.index(val))
                ind = data.index(val)
            else: 
                my_group.append(data.index(val, ind + 1))
                ind = data.index(val)
        if len(my_group) > 1:
            indexes.append(my_group)
    '''
    for i in range(len(data)):
        if data[i] > 0:
            group = []
            curr_val = data[i] 
            for j in range(len(data)):
                if data[j] > 0: 
                    value = data[j]
                    if i != j:
                        if abs(value - curr_val) <= tolerance:
                            group.append(value)
    #                        group.append(curr_val)
                    else:
                        if abs(value - curr_val) <= tolerance:
                            group.append(curr_val)
            my_result.append(group)   

    #print('my_result:  ', my_result)

    for sublist in my_result:
        if sorted(sublist) not in [sorted(x) for x in result]:
            result.append(sublist)

    #print('result:     ', result)

    #unique_lst = list(set(map(tuple, result)))
    #print('unique_lst: ', unique_lst)

    grouped_list = [sublist for i, sublist in enumerate(result) if not any(set(sublist).issubset(set(x)) for j, x in enumerate(result) if i != j) and len(sublist) > 1]
    #print('groupe_list:', grouped_list)

    indexes = [[data.index(val) for val in group] for group in grouped_list if len(group) > 1]
    #indexes = [[data.index(val) for val in group] for group in grouped_list]
    #print('indexes:    ', indexes)

    return indexes

def add_shapes(fig, my_row):
    
    global sorted_team_list
 
    step = 9
    minuts = 45
    second_time = 46

    if len(fig['layout']['shapes']) == len(sorted_team_list) * 18:    
        return fig
    elif len(fig['layout']['shapes']) == len(sorted_team_list): 
        fig['layout']['shapes'] = []

    for i in range(step):
        opac = (i/45)
        fig.add_shape(
            type = 'rect',
#            xref = 'x' if my_row == 1 else 'x' + str(my_row),
#            yref = 'y' if my_row == 1 else 'y' + str(my_row),
            xref = 'x' + str(2*my_row),
            yref = 'y' + str(2*my_row),
            x0   = 1,
            x1   = total_rounds + 1,
            y0   = i*(minuts/step),
            y1   = i*(minuts/step) + minuts/step,
            fillcolor = "green",
            opacity   = opac,
            line      = dict(width = 0),
            layer="below"
        )

    for i in range(step):
        opac = (i/45)
        fig.add_shape(
            type = 'rect',
#            xref = 'x' if my_row == 1 else 'x' + str(my_row),
#            yref = 'y' if my_row == 1 else 'y' + str(my_row),
            xref = 'x' + str(2*my_row),
            yref = 'y' + str(2*my_row),
            x0   = 1,
            x1   = total_rounds + 1,
            y0   = second_time + i*(minuts/step),
            y1   = second_time + i*(minuts/step) + minuts/step,
            fillcolor = "red",
            opacity   = opac,
            line      = dict(width = 0),
            layer="below"    
        )

    return fig

def get_count_games_online(count_games, list_games, league, season, root):

    for i in range(0, len(list_games)):
        #for i in range(2):
        game_id = list_games[i]['Game_id']   

        path      = root + '/' + str(country) + '/' + str(league) + '/' + str(season) + '/' + str(i + 1) + '/' + str(game_id) + '.json'
        if not os.path.isfile(path):
            count_games += 1    

    return count_games

def get_detail_games(country, league, season, sorted_team_list):

    global total_rounds
    global current_round
    global fig
    global scored_majority
    global scored_minority
    global arr_type_events
    global team_dimension
    global team_arr
    global symbol_marker_goals

    global all_marker_opacity                       
    global all_marker_opacity_goal                  
    global all_marker_opacity_card                  
    global all_marker_opacity_subst                 
    global all_marker_opacity_var                   
     
    global all_marker_opacity_normal_scored         
    global all_marker_opacity_penalty_scored        
    global all_marker_opacity_missed_penalty_scored 
    global all_marker_opacity_own_goal_scored       
    global all_marker_opacity_extra_goal      
    global all_marker_opacity_majority_scored       
    global all_marker_opacity_minority_scored  

    global opacity 
    global nochange_opacity
    global extra_events 
    global y_value_all

    global count_games_load 

    # Initializaion
    extra_events   = []
    team_arr       = []
    team_dimension = []
    y_value_all    = []

    y_goals = []
    y_cards = []
    y_subst = []
    y_var   = []
    y_majority = []
    y_minority = []

    color_marker_goals  = []
    symbol_marker_goals = []

    stat_goal_scored           = []
    stat_goal_missed           = []
    stat_normal_goal_scored    = []
    stat_penalty_scored        = []
    stat_missid_penalty_scored = []
    stat_own_goal_scored       = [] 
    stat_own_goal_missed       = [] 
    stat_normal_goal_missed    = []
    stat_penalty_missed        = []
    stat_missid_penalty_missed = []
    stat_extra_scored          = []
    stat_extra_missed          = []
    stat_yellow                = []
    stat_red                   = []
    stat_subst                 = []
    stat_var                   = []


    goal_annotation           = []
    normal_goal_annotation    = []
    penalty_annotation        = []
    missid_penalty_annotation = []
    own_goal_annotation       = []
    extra_goal_annotation     = []
    cards_annotation          = []
    subst_annotation          = []
    var_annotation            = []
    majority_annotation       = []
    minority_annotation       = []

    all_scored                = []
    all_missed                = []

    my_row = 1 

    fig = make_subplots(rows = len(sorted_team_list), cols = 2, column_widths=[0.1, 0.9], vertical_spacing=0.03)

    delta = 1/len(sorted_team_list)

    str_delta = str(delta)
    subplot_height = [Decimal(str_delta) for _ in range(len(sorted_team_list))] 
    
    annotations_stat  = []
    annotations_all   = []

    count_games_load = 0 

    for t, teams in enumerate(sorted_team_list):

        team      = teams['name_id']

        start_time = time.time()
        data_detail = get_list_games(country, league, season, team)
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения get_list_games:", execution_time, "секунд")

        start_time = time.time()
        all_detail   = get_games_goals(data_detail, league, season, team, arr_type_events)
        if isinstance(all_detail, bool):
            if not all_detail:
                return all_detail
            
        df_detail    = all_detail[0]
        df_red_cards = all_detail[1]
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения get_games_goals:", execution_time, "секунд")
        
        label_colors = []
        positions    = []

        for item in data_detail:
            if item['Team_id_home'] == team:
                if item['Score_home'] > item['Score_away']:
                    label_colors.append('green')
                    positions.append(-0.05)
                elif item['Score_home'] < item['Score_away']:
                    label_colors.append('red')
                    positions.append(-0.15)
                else:
                    label_colors.append('blue')  
                    positions.append(-0.1)
            else:
                if item['Score_home'] > item['Score_away']:
                    label_colors.append('red')
                    positions.append(-0.15)
                elif item['Score_home'] < item['Score_away']:
                    label_colors.append('green')
                    positions.append(-0.05)
                else:
                    label_colors.append('blue')
                    positions.append(-0.1)

    #    all_marker = []
        annotations_round = []    
        annotations_team  = []
        annotations_score = []
        annotations_goals = []
        annotations_teams = []

        start_time = time.time()

        df_scored = dict_to_df(df_detail)
        team_dimension.append(len(df_scored))

        x_values_def    = list(range(1, current_round + 1))
        y_values        = df_scored['Time']
        extra_time      = df_scored['Extra'], 
        detail          = df_scored['Detail'], 
        player_scored   = df_scored['Player'], 
        assist_scored   = df_scored['Assist'], 
        type_scored     = df_scored['Type'], 
        comment_scored  = df_scored['Comment'], 
        team_id         = df_scored['Team_id'],

        team_arr.extend(team_id)

        color_marker     = []
        symbol_marker    = []
        color_extra_time = []

        symbol_goals     = []
        symbol_cards     = []
        symbol_subst     = []
        symbol_var       = []
        symbol_majority  = []
        symbol_monority  = []    
        hovertemplate_events = []

        y_extra_time = []
        
        for sublist in detail:
            for i, round in enumerate(sublist):
#            for j, data in enumerate(type_scored[0][i]):
                sub_events = []
                for j, item in enumerate(round):
                    type =  type_scored[0][i][j]
                    if type == 'Goal':
                        template       =  f'<br>Type: {item}<br>Player: {player_scored[0][i][j]}<br>Assist: {assist_scored[0][i][j]}'
                        template_extra =  f' + {extra_time[0][i][j]}<br>Type: {detail[0][i][j]}<br>Player: {player_scored[0][i][j]}<br>Assist: {assist_scored[0][i][j]}'
                    elif type == 'Card':    
                        template       =  f'<br>Type: {item}<br>Player: {player_scored[0][i][j]}<br>Comment: {comment_scored[0][i][j]}'
                        template_extra =  f' + {extra_time[0][i][j]}<br>Type: {detail[0][i][j]}<br>Player: {player_scored[0][i][j]}<br>Comment: {comment_scored[0][i][j]}'
                    elif type == 'subst':
                        template       =  f'<br>Type: {item}<br>Input: {player_scored[0][i][j]}<br>Output: {assist_scored[0][i][j]}'
                        template_extra =  f' + {extra_time[0][i][j]}<br>Type: {detail[0][i][j]}<br>Input: {player_scored[0][i][j]}<br>Output: {assist_scored[0][i][j]}'
                    elif type == 'Var':
                        template       =  f'<br>Type: {item}<br>Player: {player_scored[0][i][j]}'
                        template_extra =  f' + {extra_time[0][i][j]}<br>Type: {detail[0][i][j]}<br>Player: {player_scored[0][i][j]}'
                    
                    if extra_time[0][i][j] == None or extra_time[0][i][j] == 0:
                        sub_events.append('Home:Away: <br>%{text}<br>Elapsed: %{y}' + template + '<br><extra></extra>')

                    else:
                        sub_events.append('Home:Away: <br>%{text}<br>Elapsed: %{y}' + template_extra + '<br><extra></extra>')

                hovertemplate_events.append(sub_events)

        mapping_goals = {
                    'Penalty'           : 1,
                    'Missed Penalty'    : 1, 
                    'Own Goal'          : 1,
                    'Normal Goal'       : 1,
                    }
        
        for sublist in detail:
            for i, round in enumerate(sublist):
                sub_symbol_goals = []
                for j, item in enumerate(round):
                    if item in mapping_goals:
                        sub_symbol_goals.append(y_values[i][j])
                    else:
                        sub_symbol_goals.append(-100)
        
                symbol_goals.append(sub_symbol_goals)

        mapping_cards = {
                   'Yellow Card'       : 1,
                   'Red Card'          : 1,
                  }

        for sublist in detail:
            for i, round in enumerate(sublist):
                sub_symbol_cards = []
                for j, item in enumerate(round):
                    if item in mapping_cards:
                        sub_symbol_cards.append(y_values[i][j])
                    else:
                        sub_symbol_cards.append(-100)
        
                symbol_cards.append(sub_symbol_cards)

        mapping_cards = {
                   'Substitution 1'    : 1,
                   'Substitution 2'    : 1,
                   'Substitution 3'    : 1,
                   'Substitution 4'    : 1,
                   'Substitution 5'    : 1,
                  }

        for sublist in detail:
            for i, round in enumerate(sublist):
                sub_symbol_subst = []
                for j, item in enumerate(round):
                    if item in mapping_cards:
                        sub_symbol_subst.append(y_values[i][j])
                    else:
                        sub_symbol_subst.append(-100)
        
                symbol_subst.append(sub_symbol_subst)

        mapping_cards = {
                   'Penalty cancelled' : 1,
                   'Card reviewed'     : 1,
                   'Goal cancelled'    : 1,
                  }

        for sublist in detail:
            for i, round in enumerate(sublist):
                sub_symbol_var = []
                for j, item in enumerate(round):
                    if item in mapping_cards:
                        sub_symbol_var.append(y_values[i][j])
                    else:
                        sub_symbol_var.append(-100)
        
                symbol_var.append(sub_symbol_var)

        mapping = {'Penalty'           : 5,
                   'Missed Penalty'    : 6, 
                   'Own Goal'          : 2,
                   'Normal Goal'       : 0,
                   'Yellow Card'       : 1,
                   'Red Card'          : 201,
                   'Penalty cancelled' : 17,
                   'Card reviewed'     : 17,
                   'Goal cancelled'    : 17,
                   'Substitution 1'    : 26,
                   'Substitution 2'    : 26,
                   'Substitution 3'    : 26,
                   'Substitution 4'    : 26,
                   'Substitution 5'    : 26,
                  }
 
        symbol_marker = []

        for sublist in detail:
            for i, round in enumerate(sublist):
                sub_symbol_marker = []
                for j, item in enumerate(round):
                    if item in mapping:
                        sub_symbol_marker.append(mapping.get(item))
                    else:
                        sub_symbol_marker.append(100)
        
                symbol_marker.append(sub_symbol_marker)

        my_normal_goal_scored    = 0
        my_penalty_scored        = 0
        my_missid_penalty_scored = 0
        my_own_goal_scored       = 0 
        my_normal_goal_missed    = 0
        my_penalty_missed        = 0
        my_missid_penalty_missed = 0
        my_own_goal_missed       = 0 
        my_extra_scored          = 0
        my_extra_missed          = 0
        my_yellow                = 0
        my_red                   = 0
        my_subst                 = 0
        my_var                   = 0

        map_item = {0 :1, 
                    2 :1,
                    5 :1, 
                    6 :1
            
        }

        for i, sublist in enumerate(symbol_marker):
            my_extra_time = []
            for j, item in enumerate(sublist):
                if team_id[0][i][j] == team:
                    if item == 0:
                        my_normal_goal_scored += 1
                    elif item == 5:
                        my_penalty_scored += 1
                    elif item == 6:
                        my_missid_penalty_scored += 1
                    elif item == 2:
                        my_own_goal_scored += 1
                    if extra_time[0][i][j] != None:   
                        if extra_time[0][i][j] > 0 and item in map_item: 
                            my_extra_scored += 1
                            my_extra_time.append(extra_time[0][i][j])      
                        else:
                            my_extra_time.append(0) 
                    else:
                        my_extra_time.append(0) 
                else:
                    if item == 0:
                        my_normal_goal_missed += 1
                    if item == 5:
                        my_penalty_missed += 1
                    if item == 6:
                        my_missid_penalty_missed += 1
                    if item == 2:
                        my_own_goal_missed += 1
                    if extra_time[0][i][j] != None:   
                        if extra_time[0][i][j] > 0 and item in map_item: 
                            my_extra_missed += 1      
                            my_extra_time.append(extra_time[0][i][j]) 
                        else:
                            my_extra_time.append(0) 
                    else:
                        my_extra_time.append(0) 
            
            y_extra_time.append(my_extra_time)
 
            my_yellow  += sublist.count(1)
            my_red     += sublist.count(201)
            my_subst   += sublist.count(26)
            my_var     += sublist.count(17)

        normal_goal_annotation.append('Scored: ' + str(my_normal_goal_scored) + ' | Missed: ' + str(my_normal_goal_missed) + ' the all time')
        penalty_annotation.append('Scored: ' + str(my_penalty_scored) + ' | Missed: ' + str(my_penalty_missed) + ' the all time')
        missid_penalty_annotation.append('Scored: ' + str(my_missid_penalty_scored) + ' | Missed: ' + str(my_missid_penalty_missed) + ' the all time')
        own_goal_annotation.append('Scored: ' + str(my_own_goal_scored) + ' | Missed: ' + str(my_own_goal_missed) + ' the all time')
        extra_goal_annotation.append('Scored: ' + str(my_extra_scored) + ' | Missed: ' + str(my_extra_missed) + ' the all time')
        cards_annotation.append('Yellow: ' + str(my_yellow) + ' | Red: ' + str(my_red) + ' the all time')
        subst_annotation.append('Subst: ' + str(my_subst) + ' the all time')
        var_annotation.append('Var: ' + str(my_var) + ' the all time')

        stat_goal_scored.append(my_yellow)
        stat_goal_missed.append(my_yellow)
        stat_normal_goal_scored.append(my_normal_goal_scored)
        stat_penalty_scored.append(my_penalty_scored)
        stat_missid_penalty_scored.append(my_missid_penalty_scored)
        stat_own_goal_scored.append(my_own_goal_scored) 
        stat_own_goal_missed.append(my_own_goal_missed) 
        stat_normal_goal_missed.append(my_normal_goal_missed)
        stat_penalty_missed.append(my_penalty_missed)
        stat_missid_penalty_missed.append(my_missid_penalty_missed)
        stat_extra_scored.append(my_extra_scored)
        stat_extra_missed.append(my_extra_missed)
        stat_yellow.append(my_yellow)
        stat_red.append(my_red)
        stat_subst.append(my_subst)
        stat_var.append(my_var)

        map_team = {team: 'green'}

        color_marker = []
        for sublist in team_id:
            for round in sublist:
                sub_color_marker = []
                for item in round:
                    if item in map_team:
                        sub_color_marker.append(map_team.get(item))
                    else:
                        sub_color_marker.append('red')
        
                color_marker.append(sub_color_marker)

        map_card = {'Yellow Card': 'yellow',
                    'Red Card':    'red'}

        for sublist in detail:
            for i, round in enumerate(sublist):
                for j, item in enumerate(round):
                    if item in map_card:
                        color_marker[i][j] =  map_card.get(item)

        color_extra_time = []

        for sublist in extra_time:
            for i, round in enumerate(sublist):
                sub_extra_time = []
                for j, item in enumerate(round):
                    if item != None and item != 0 and (y_values[i][j] >= 45 or y_values[i][j] >= 90) :
                        sub_extra_time.append('orange')
                    else:
                        if color_marker[i][j] == 'green':
                            sub_extra_time.append('green')
                        elif color_marker[i][j] == 'yellow':
                            sub_extra_time.append('green')
                        else:
                           sub_extra_time.append('red')
        
                color_extra_time.append(sub_extra_time)

        
        mapping_red_card = {
                    'Red Card' : 1,
                    }
        
        red_card_own   = []
        red_card_rival = []

        for i, row in enumerate(df_detail):
            for j, round in enumerate(row):
                if round['Detail'] == 'Red Card':
                    card_time = round['Time']
                    if round['Team_id'] == team:
                        red_card_own.append([card_time,j])

        for i, row in enumerate(df_red_cards):
            for j, round in enumerate(row):
                if round['Detail'] == 'Red Card':
                    if round['Team_id'] != team:
                        card_time = round['Time']
                        red_card_rival.append([card_time, j, round])

        mapping_goals_not_equal = {
                    'Penalty'           : 1,
                    'Missed Penalty'    : 1, 
                    'Own Goal'          : 1,
                    'Normal Goal'       : 1,
                    }
        
        goals_majority      = []
        goals_minority      = []

        count_majority_scored = 0
        count_majority_missed = 0
        count_minority_scored = 0
        count_minority_missed = 0

        for i, column in enumerate(zip(*list(detail[0]))):
            time_own = 0
            time_rival = 0
            for index, sublist in enumerate(red_card_own):
                if i == sublist[1]:
                    time_own = sublist[0]
                    break
            for index, sublist in enumerate(red_card_rival):
                if i == sublist[1]:
                    time_rival = sublist[0]
                    break
            sub_goals_majority= []
            sub_goals_minority= []
            for j, item in enumerate(column):
                if item in mapping_goals_not_equal:
                    if  time_rival > 0 and y_values[j][i] >= time_rival:
                        sub_goals_majority.append(y_values[j][i])
                        sub_goals_minority.append(-100)
                        if team_id[0][j][i] == team:
                            count_majority_scored += 1
                        else:
                            count_majority_missed += 1    
                    elif time_own > 0  and y_values[j][i] >= time_own:
                        sub_goals_minority.append(y_values[j][i])
                        sub_goals_majority.append(-100)
                        if team_id[0][j][i] == team:
                            count_minority_scored += 1
                        else:
                            count_minority_missed += 1    
                    else:
                        sub_goals_majority.append(-100)
                        sub_goals_minority.append(-100)
                else:
                    sub_goals_majority.append(-100)
                    sub_goals_minority.append(-100)

      
            goals_majority.append(sub_goals_majority)
            goals_minority.append(sub_goals_minority)

        majority_annotation.append('Scored: ' + str(count_majority_scored) + ' | Missed: ' + str(count_majority_missed) + ' the all time')
        minority_annotation.append('Scored: ' + str(count_minority_scored) + ' | Missed: ' + str(count_minority_missed) + ' the all time')
        
        scored_majority[0].append(count_majority_scored)
        scored_majority[1].append(count_majority_missed)
        scored_majority[2].append(count_majority_scored - count_majority_missed)
        scored_minority[0].append(count_minority_scored)
        scored_minority[1].append(count_minority_missed)
        scored_minority[2].append(count_minority_scored - count_minority_missed)

        for card in red_card_own:
            j = card[1]
            for i in range(len(df_detail)):
                if symbol_marker[i][j] == 100:
                    goals_minority[j][i]       = card[0]
                    symbol_marker[i][j]        = 201
                    color_marker[i][j]         = 'red'
                    color_extra_time[i][j]     = 'green'
                    template_extra = f' + {extra_time[0][i][j]}<br>Type: Red Card <br>Player: {player_scored[0][i][j]}<br>Comment: {comment_scored[0][i][j]}'
                    template       = f'<br>Type: Red Card <br>Player: {player_scored[0][i][j]}<br>Comment: {comment_scored[0][i][j]}'
                    if extra_time[0][i][j] == None or extra_time[0][i][j] == 0:
                        sub_events = 'Home:Away: <br>%{text}<br>Elapsed: %{y}' + template + '<br><extra></extra>'

                    else:
                        sub_events = 'Home:Away: <br>%{text}<br>Elapsed: %{y}' + template_extra + '<br><extra></extra>'
                    
                    hovertemplate_events[i][j] = sub_events 
                    
                    break
                else:
                    next    

        for card in red_card_rival:
            j            = card[1]
            detail_cover = card[2]
            for i in range(len(df_detail)):
                if symbol_marker[i][j] == 100:
                    goals_majority[j][i] = card[0]
                    symbol_marker[i][j] = 201
                    color_marker[i][j] = 'green'
                    color_extra_time[i][j] = 'red'
                    extra = detail_cover['Extra']
                    player = detail_cover['Player']
                    comment = detail_cover['Comment']
                    template_extra = f' + {extra}<br>Type:  Red Card <br>Player: {player}<br>Comment: {comment}'
                    template       = f'<br>Type: Red Card <br>Player: {player}<br>Comment: {comment}'
                    if extra_time[0][i][j] == None or extra_time[0][i][j] == 0:
                        sub_events = 'Home:Away: <br>%{text}<br>Elapsed: %{y}' + template + '<br><extra></extra>'

                    else:
                        sub_events = 'Home:Away: <br>%{text}<br>Elapsed: %{y}' + template_extra + '<br><extra></extra>'
                    
                    hovertemplate_events[i][j] = sub_events 
                    
                    break
                else:
                    next    

        majority = []
        for i, column in enumerate(zip(*goals_majority)):
            sub_majority= []
            for j, item in enumerate(column):
                    sub_majority.append(item)

            majority.append(sub_majority)

        minority = []
        for i, column in enumerate(zip(*goals_minority)):
            sub_minority= []
            for j, item in enumerate(column):
                    sub_minority.append(item)

            minority.append(sub_minority)

        team_dim = len(df_scored)
        # Tracing
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения MARKERS:", execution_time, "секунд")
        start_time = time.time()
        # Tracing
        
        marker_opacity                       = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_goal                  = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_card                  = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_subst                 = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_var                   = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_majority_scored       = [[1.0] * current_round for _ in range(team_dim)]
        marker_opacity_minority_scored       = [[1.0] * current_round for _ in range(team_dim)]
        
        marker_opacity_normal_scored         = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_penalty_scored        = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_missed_penalty_scored = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_own_goal_scored       = [[0.0] * current_round for _ in range(team_dim)]
        marker_opacity_extra_goal            = [[0.0] * current_round for _ in range(team_dim)]
        
        for sublist in type_scored:
            for i, round in enumerate(sublist):
                for j, item in enumerate(round):
                    if item == 'Goal':
                        marker_opacity_goal[i][j]  =  1.0
                        if extra_time[0][i][j] != None:   
                            if extra_time[0][i][j] > 0:
                                marker_opacity_extra_goal[i][j]  =  1.0
                    if item == 'Card':
                        marker_opacity_card[i][j]  =  1.0
                    if item == 'subst':
                        marker_opacity_subst[i][j] =  1.0
                    if item == 'Var':
                        marker_opacity_var[i][j]   =  1.0
  
        map_detail = {
            'Yellow Card'       : 0.0,
            'Red Card'          : 0.0,
            'Penalty cancelled' : 0.0,
            'Card reviewed'     : 0.0,
            'Goal cancelled'    : 0.0,
            'Substitution 1'    : 0.0,
            'Substitution 2'    : 0.0,
            'Substitution 3'    : 0.0,
            'Substitution 4'    : 0.0,
            'Substitution 5'    : 0.0
            }

        for sublist in detail:
            for i, round in enumerate(sublist):
                for j, item in enumerate(round):
                    
                    if item == 'Normal Goal':
                        marker_opacity_normal_scored[i][j] =  1.0
                    else:
                        marker_opacity_normal_scored[i][j] =  0.2    
                    if item == 'Penalty':
                        marker_opacity_penalty_scored[i][j] =  1.0
                    else:
                        marker_opacity_penalty_scored[i][j] =  0.2    
                    if item == 'Missed Penalty':
                        marker_opacity_missed_penalty_scored[i][j] =  1.0
                    else:
                        marker_opacity_missed_penalty_scored[i][j] =  0.2    
                    if item == 'Own Goal':
                        marker_opacity_own_goal_scored[i][j] =  1.0
                    else:
                        marker_opacity_own_goal_scored[i][j] =  0.2 

                    if item in map_detail:
                        marker_opacity_normal_scored[i][j]         = map_detail.get(item)
                        marker_opacity_penalty_scored[i][j]        = map_detail.get(item)
                        marker_opacity_missed_penalty_scored[i][j] = map_detail.get(item)
                        marker_opacity_own_goal_scored[i][j]       = map_detail.get(item)
         
        score_home_away = []
        round_team      = []
        score_team      = []
        color_team      = []
        scored_goals    = 0
        missed_goals    = 0

        # Tracing
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения OPACITYES:", execution_time, "секунд")
        start_time = time.time()
        # Tracing

        for i, item in enumerate(data_detail):
            val = item['Name_home'] + ':' + item['Name_away'] + '<br>' + str(item['Score_home']) + ':' + str(item['Score_away'])
            score_home_away.append(val)
            if team == item['Team_id_home']: # Home
                round_team.append(item['Name_away'])
                score_team.append(str(item['Score_home']) + ':' + str(item['Score_away']))
                color_team.append('lightgreen')
                scored_goals = scored_goals + item['Score_home']
                missed_goals = missed_goals + item['Score_away']
            else:                            # Away
                round_team.append(item['Name_home'])
                score_team.append(str(item['Score_away']) + ':' + str(item['Score_home']))    
                color_team.append('lightpink')
                scored_goals = scored_goals + item['Score_away']
                missed_goals = missed_goals + item['Score_home']

            # ANNOTATION                    
            my_dict = dict(
                    x         = x_values_def[i],
                    y         = positions[x_values_def[i]-2],  # Координата Y для размещения аннотации ниже оси X
                    text      = str(x_values_def[i]),
                    showarrow = False,
                    xref      = 'x',
                    yref      = 'paper',  # Использование 'paper' для размещения аннотации ниже оси X
                    font      = dict(
                                    color = label_colors[x_values_def[i]-1],
                                    size  = 14
                                )
                )                
            annotations_round.append(my_dict)    
        
            if i < len(round_team):

                annotations_team.append(dict(
                    name      = target_annotation_team,
                    x         = x_values_def[i] + 0.3 * current_round/total_rounds,
                    y         = 45,
                    xref      = "x" + str(2*t+2),
                    yref      = "y" + str(2*t+2),
                    text      = round_team[i],
                    showarrow = False,
                    font      = dict(
                        family = "Courier New, monospace, bolt",
                        size   = 16,
                        color  = 'black',
                    ),
                    bgcolor   = color_team[i],
                    opacity   = 0.5,
                    textangle = 270
                ))

                annotations_score.append(dict(
                    name      = target_annotation_score,
                    x         = x_values_def[i],
                    y         = 95,
                    xref      = "x" + str(2*t+2),
                    yref      = "y" + str(2*t+2),
                    text      = score_team[i],
                    showarrow = False,
                    font      = dict(
                        family = "Courier New, monospace, bolt",
                        size   = 16,
                        color  = 'black',
                    ),
                    bgcolor   = color_team[i],
                    opacity   = 0.5
                ))

        annotations_teams = annotations_team + annotations_score
        annotations_all.extend(annotations_teams)
        # END ANNOTATION

        # Tracing
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения ANNOTATIONS:", execution_time, "секунд")
        start_time = time.time()
        # Tracing

        # ************ scored *********************
        for i in range(len(df_detail)):
            new_scatter_scored = go.Scatter(
                    x      = x_values_def,
                    y      = symbol_goals[i],
                    mode   = 'markers',
                    marker = dict(size = 15, color = color_marker[i], 
                                symbol = symbol_marker[i],
                                line = dict(color = color_extra_time[i], width = 3),
                    ),   
#                    name   = f'round-{x_values_def[i]}',
                    hovertemplate = hovertemplate_events[i], 
                    text = score_home_away,
                    hoverlabel   = dict(
                        align       = 'auto',
                        bgcolor     = ['lightgreen' if round == 'green' else 'lightpink' for round in color_marker[i]],
                        font_size   = 16,
                        font_family = "Rockwell"
                       ),
                    hovertext=[''] * total_rounds    
                    )

            
            fig.add_trace(new_scatter_scored, row = my_row, col = 2)
        
        # Tracing
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения HOVER and SCATTER:", execution_time, "секунд")
        start_time = time.time()
        # Tracing

        # SHAPES
        update = False
        fig = add_shapes(fig, my_row)
        # Tracing
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения add_shapes:", execution_time, "секунд")
        start_time = time.time()
        # Tracing

        my_stat = dict(
                    name      = target_annotation_goals,
                    x          = 1,
                    y          = delta_annotation_goals,
                    xanchor   = 'left',
                    xref       = "x" + str(2*t+2),
                    yref       = "y" + str(2*t+2),
                    text       = 'Scored: ' + str(scored_goals) + ' | Missed: ' + str(missed_goals) + ' the all time',
                    showarrow  = False,
                    font       = dict(
                        family = "Arial, monospace",
                        size   = 16,
                       color  = "black",
                    ),
                    bgcolor="lightgreen",
                )

        annotations_stat.append(my_stat)
        
        goal_annotation.append('Scored: ' + str(scored_goals) + ' | Missed: ' + str(missed_goals) + ' the all time')
        all_scored.append(scored_goals)
        all_missed.append(missed_goals)
        
        # Tracing
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения add_annotation Scored:", execution_time, "секунд")
        start_time = time.time()
        # Tracing
 
        if my_row == 1:
            all_marker_opacity_goal  = marker_opacity_goal
            all_marker_opacity_card  = marker_opacity_card
            all_marker_opacity_subst = marker_opacity_subst
            all_marker_opacity_var   = marker_opacity_var
            all_marker_opacity_normal_scored         = marker_opacity_normal_scored
            all_marker_opacity_penalty_scored        = marker_opacity_penalty_scored
            all_marker_opacity_missed_penalty_scored = marker_opacity_missed_penalty_scored 
            all_marker_opacity_own_goal_scored       = marker_opacity_own_goal_scored
            all_marker_opacity_extra_goal            = marker_opacity_extra_goal
            all_marker_opacity_majority_scored       = marker_opacity_majority_scored
            all_marker_opacity_minority_scored       = marker_opacity_minority_scored
        else:
            for i in range(len(marker_opacity)):
                all_marker_opacity_goal.append(marker_opacity_goal[i])
                all_marker_opacity_card.append(marker_opacity_card[i])
                all_marker_opacity_subst.append(marker_opacity_subst[i])
                all_marker_opacity_var.append(marker_opacity_var[i])
                all_marker_opacity_normal_scored.append(marker_opacity_normal_scored[i])
                all_marker_opacity_penalty_scored.append(marker_opacity_penalty_scored[i])
                all_marker_opacity_missed_penalty_scored.append(marker_opacity_missed_penalty_scored[i]) 
                all_marker_opacity_own_goal_scored.append(marker_opacity_own_goal_scored[i])
                all_marker_opacity_extra_goal.append(marker_opacity_extra_goal[i])
    
            all_marker_opacity_majority_scored = all_marker_opacity_majority_scored + marker_opacity_majority_scored
            all_marker_opacity_minority_scored = all_marker_opacity_minority_scored + marker_opacity_minority_scored

        y_goals.extend(symbol_goals)
        y_cards.extend(symbol_cards)
        y_subst.extend(symbol_subst)
        y_var.extend(symbol_var)
        y_majority.extend(majority)
        y_minority.extend(minority)

        y_value_all.extend(y_values)

        color_marker_goals.extend(color_marker)
        symbol_marker_goals.extend(symbol_marker)
        extra_events.extend(y_extra_time)      

        my_row += 1

        # Tracing
        end_time = time.time()
        execution_time = end_time - start_time
#        print("Время выполнения all_marker_opacity:", execution_time, "секунд")
        start_time = time.time()
        # Tracing
    ##################### Next team ############################
    
    opacity_goal = []
    opacity_goal.append(all_marker_opacity_goal)                 
    opacity_goal.append(all_marker_opacity_normal_scored)         
    opacity_goal.append(all_marker_opacity_penalty_scored)        
    opacity_goal.append(all_marker_opacity_missed_penalty_scored) 
    opacity_goal.append(all_marker_opacity_own_goal_scored)       
    opacity_goal.append(all_marker_opacity_extra_goal)

    opacity_other = []
    opacity_other.append(all_marker_opacity_card)                 
    opacity_other.append(all_marker_opacity_subst)                 
    opacity_other.append(all_marker_opacity_var)
    
    opacity = []
    opacity.append(opacity_goal)
    opacity.append(opacity_other)
    nochange_opacity = copy.deepcopy(opacity)

    annotations_all.extend(annotations_stat)
#    fig.update_layout(annotations = annotations_all)
    
    # Tracing
    end_time = time.time()
    execution_time = end_time - start_time
#    print("Время выполнения add_annotation_all:", execution_time, "секунд")
    start_time = time.time()
    # Tracing

    if len(sorted_team_list) == 1:
        ticks = False
    else:
        ticks = True

    ticks = True
    
    for i in range(0, len(sorted_team_list)):
        fig.update_layout(
            **{f'xaxis{2*i+2}': {'showgrid' : True, 
                                'gridcolor' : 'blue', 
                                'showticklabels': True if i == len(sorted_team_list) - 1 else False, 
                                'tickmode' : 'array', 
                                'tickvals' : list(range(1, total_rounds + 1)), 
                                'automargin' :True, 
                                'range' : [0.8, current_round + 0.3]}},    
            **{f'yaxis{2*i+2}': dict(title_text = sorted_team_list[i]['name'], 
                                    rangemode = "normal", 
                                    position  = 0, 
                                    side      = 'left',
                                    showline  = False,  # Скрыть линию оси X
                                    zeroline  = False)}
        )
        
    for i in range(0, len(sorted_team_list)):
        fig.update_layout(
            {'yaxis' + str(2*i+2): {
                                'range' : [-10, 100],
                                'tick0' : 1, 
                                'dtick': 1, 
                                'tickcolor' : 'blue', 
                                'gridcolor' : 'blue', 
                                'automargin' :True,
                                'showgrid' : True,  
                                'tickvals' : [1, 45, 90],
                                'title_standoff' : 5,
                                'showline'  : False, 
                                'zeroline'  : False
                                }   
            }   
        )
        
    fig.update_layout(
                    showlegend   = False, 
                    margin_autoexpand = True,
                    margin=dict(l=0, r=0, t=50, b=0)
#                    margin_b     = 50,
#                    margin_l     = 0,
#                    margin_r     = 10,
#                    margin_t     = 20,
#                    margin_pad   = 0,
                )
    
#    for i, height in enumerate(subplot_height):
#        fig.update_layout(
#            {'yaxis' + str(2*i+2): {'domain': [sum(subplot_height[:i]), 
#                                             sum(subplot_height[:i+1])]}}
#        )

    fig.update_layout(height = sum(subplot_height) * fig_height * len(sorted_team_list),
                        plot_bgcolor  = 'white',
                        paper_bgcolor = 'white',
                        font = dict(color="black")
                       )

    fig.update_layout(
        xaxis=dict(
            showline=False,  # Скрыть линию оси X
            zeroline=False,  # Отобразить нулевую линию оси X
        ),
        yaxis=dict(
            showline=False,  # Скрыть линию оси Y
            zeroline=False,  # Отобразить нулевую линию оси Y
        )
    )

    conf={
            'displayModeBar': False,
            'responsive': True,  # Разрешение отзывчивости графика
            'autosizable': True,  # Разрешение автоматической настройки размера графика
            'margin': {'l': 40, 'r': 0, 't': 40, 'b': 30},  # Настройка отступов графика
            }
    # Tracing
    end_time = time.time()
    execution_time = end_time - start_time
#    print("Время выполнения UPDATE LAYOUT:", execution_time, "секунд")
    start_time = time.time()
    # Tracing
    
    #    fig = find_duplicate_indices('goal', fig, sorted_team_list)
    fig = find_duplicate_indices('goal', fig, sorted_team_list, team_dimension)
    # Tracing
    end_time = time.time()
    execution_time = end_time - start_time
#    print("Время выполнения find_duplicate_indices:", execution_time, "секунд")
    start_time = time.time()
    # Tracing
    
    total_dim = sum(team_dimension)

    for t, teams in enumerate(sorted_team_list):

        if t == 0:
            delta_team = 0
        else:
            delta_team = team_dimension[t-1]    
    
    map_goal  = [0, 2, 5, 6]
    map       = [0, 2, 5, 6, 201]
    map_cards = [1, 201]
    map_subst = [26]
    map_var   = [17]

    x_cards    = find_duplicate_indices_xaxis(map_cards, symbol_marker_goals, y_cards, team_dimension)
    x_subst    = find_duplicate_indices_xaxis(map_subst, symbol_marker_goals, y_subst, team_dimension)
    x_var      = find_duplicate_indices_xaxis(map_var, symbol_marker_goals, y_var, team_dimension)
    x_goals    = find_duplicate_indices_xaxis(map_goal, symbol_marker_goals, y_goals, team_dimension)
    x_majority = find_duplicate_indices_xaxis(map, symbol_marker_goals, y_majority, team_dimension)
    x_minority = find_duplicate_indices_xaxis(map, symbol_marker_goals, y_minority, team_dimension)

    # Tracing
    end_time = time.time()
    execution_time = end_time - start_time
#    print("Время выполнения find_duplicate_indices_xaxis:", execution_time, "секунд")
    start_time = time.time()
    # Tracing

    count_team = len(sorted_team_list)

    x_name = [team['name'] for team in sorted_team_list]    
    x_name.reverse()
    
    my_all_missed = all_missed.copy()
    my_all_scored = all_scored.copy()

    green_annotations = []
        
    my_all_missed.reverse()
    my_all_scored.reverse()
#        y_list_green = [num + 0.25 for num in range(len(sorted_team_list))]
    y_list_green = [num + 0.5 for num in range(len(sorted_team_list))]
    difference = [x - y for x, y in zip(my_all_scored, my_all_missed)]
    min_value = min(min(difference), min(my_all_missed), min(my_all_scored))
    max_value = max(max(difference), max(my_all_missed), max(my_all_scored))

    # Вывод статистики в отдельном графике, если больше одной команды
    if len(sorted_team_list) > 1:
        fig.add_trace(go.Bar(y = x_name, 
                            x = difference, 
                            orientation = 'h', 
#                            marker_color='yellow'), 
                            marker = dict(
                                color='yellow',
                                line=dict(
                                    color = ['blue' if value >= 0 else 'red' for value in difference],
                                    width=2
                                ))
                            ),    
                            len(sorted_team_list), 
                            col = 1)    
        fig.add_trace(go.Bar(y = x_name, 
                            x = my_all_missed, 
                            orientation = 'h', 
#                            marker_color='lightpink'), 
                            marker = dict(
                                color='lightpink',
                                line=dict(
                                    color='red',
                                    width=2
                                ))
                            ),    
                            len(sorted_team_list), 
                            col = 1)    
        fig.add_trace(go.Bar(y = x_name, 
                            x = my_all_scored, 
                            orientation = 'h', 
#                            marker_color='lightgreen'), 
                            marker = dict(
                                color='lightgreen',
                                line=dict(
                                    color='green',
                                    width=2
                                ))
                            ),    
                            len(sorted_team_list), 
                            col = 1)    
        # Создаем список аннотаций для зеленой диаграммы
        for i in range(len(sorted_team_list)):
            green_annotations.append(dict(
                        name      = target_annotation_goals,
#                        x         = min_value if min_value < 0 else 2 if min_value == 0 else 0,
#                        x         = 2 if min_value <= 0 else min_value + 2,
                        x         = min_value/2 if min_value < 0 else min_value/10,
                        y         = y_list_green[i],
#                        y = 1,
                        xref      = "x" + str(2*len(sorted_team_list) - 1),
                        yref      = "y" + str(2*len(sorted_team_list) - 1),
                        text      = f'{x_name[i]}:{my_all_scored[i]}/{my_all_missed[i]}/{difference[i]}',
                        showarrow = False,
                        xanchor   = 'right',
                        font      = dict(
                            family = "Courier New, monospace, bolt",
                            size   = 14,
                            color  = 'black',
                        ),
#                        bgcolor="white",
                   ))

    fig.update_layout({
            'xaxis' + str(2*len(sorted_team_list) - 1): {'domain': [0.02, 0.15], 
#                                                        'autorange': 'min reversed', 
                                                        'autorange': 'reversed', 
                                                        'range' : [max_value, (min_value if min_value < 0 else 0)],
                                                        'visible' : True
                                                        },
            'yaxis' + str(2*len(sorted_team_list) - 1): {'domain': [0.4, 1 - (1 - 0.4)/(count_team)], 
                                                        'title_text' : 'Scored/Missed',
                                                        'side' : 'left',   
                                                        'tickvals' : [], 
                                                        'ticktext' : [],
                                                        'visible' : True
                                                        },
            'annotations' : annotations_all + green_annotations
            })
#Настройка Global Goals
    color_goals = ['yellow', 'lightpink', 'lightgreen']
    opacity_goals = [1, 1, 1]
    
    #Настройка Goals
    stat_1 = all_missed
    stat_2 = all_scored
    stat_0 = [x - y for x, y in zip(stat_2, stat_1)] 

    my_text = dict(
        type = 'Goals Scored/Missed/Dif',
        name = target_annotation_goals  
    ) 

    new_args_goal = get_update(
        fig, 
        x_goals.copy(), 
        y_goals.copy(), 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_goal.copy(), 
        goal_annotation, 
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        color_goals,
        opacity_goals
    )

    #Настройка Normal Goals
    stat_1 = stat_normal_goal_missed
    stat_2 = stat_normal_goal_scored
    stat_0 = [x - y for x, y in zip(stat_2, stat_1)] 

    my_text = dict(
        type = 'Goals Scored/Missed/Dif',
        name = target_annotation_normal  
    ) 

    new_args_normal_goal = get_update(
        fig, 
        x_goals.copy(), 
        y_goals.copy(), 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_normal_scored.copy(), 
        normal_goal_annotation, 
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        color_goals,
        opacity_goals
    )

    #Настройка Penalty Goals
    stat_1 = stat_penalty_missed                  #change
    stat_2 = stat_penalty_scored                  #change
    stat_0 = [x - y for x, y in zip(stat_2, stat_1)] 

    my_text = dict(
        type = 'Goals Scored/Missed/Dif',
        name = target_annotation_penalty          #change
    ) 

    new_args_penalty_goal = get_update(
        fig, 
        x_goals.copy(), 
        y_goals.copy(), 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_penalty_scored.copy(),  #change
        penalty_annotation,                        #change
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        color_goals,
        opacity_goals
    )

    #Настройка Missed Penalty Goals
    stat_1 = stat_missid_penalty_missed                  #change
    stat_2 = stat_missid_penalty_scored                  #change
    stat_0 = [x - y for x, y in zip(stat_2, stat_1)] 

    my_text = dict(
        type = 'Goals Scored/Missed/Dif',
        name = target_annotation_mis_pen          #change
    ) 

    new_args_missed_penalty_goal = get_update(
        fig, 
        x_goals.copy(), 
        y_goals.copy(), 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_missed_penalty_scored.copy(),  #change
        missid_penalty_annotation,                        #change
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        color_goals,
        opacity_goals                            #change
    )

    #Настройка Own Goals
    stat_1 = stat_own_goal_missed                  #change
    stat_2 = stat_own_goal_scored                  #change
    stat_0 = [x - y for x, y in zip(stat_2, stat_1)] 

    my_text = dict(
        type = 'Goals Scored/Missed/Dif',
        name = target_annotation_own          #change
    ) 

    new_args_own_goal = get_update(
        fig, 
        x_goals.copy(), 
        y_goals.copy(), 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_own_goal_scored.copy(),  #change
        own_goal_annotation,                        #change
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        color_goals,
        opacity_goals                           #change
    )

    #Настройка Extra Goals
    stat_1 = stat_extra_missed                  #change
    stat_2 = stat_extra_scored                  #change
    stat_0 = [x - y for x, y in zip(stat_2, stat_1)] 

    my_text = dict(
        type = 'Goals Scored/Missed/Dif',
        name = target_annotation_extra          #change
    ) 

    new_args_extra_goal = get_update(
        fig, 
        x_goals.copy(), 
        y_goals.copy(), 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_extra_goal.copy(),  #change
        extra_goal_annotation,                        #change
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        color_goals,
        opacity_goals                             #change
    )

    #Настройка Majority Golas
    stat_1 = scored_majority[1]                  #change
    stat_2 = scored_majority[0]                  #change
    stat_0 = scored_majority[2] 

    my_text = dict(
        type = 'Goals Scored/Missed/Dif',
        name = 'target_annotation_maj'          #change
    ) 

    new_args_majority_goal = get_update(
        fig, 
        x_majority.copy(), 
        y_majority.copy(), 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_majority_scored.copy(),  #change
        majority_annotation,                        #change
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        color_goals,
        opacity_goals,
#        False                                     #change
    )

    #Настройка Minority Golas
    stat_1 = scored_minority[1]                  #change
    stat_2 = scored_minority[0]                  #change
    stat_0 = scored_minority[2] 

    my_text = dict(
        type = 'Goals Scored/Missed/Dif',
        name = 'target_annotation_min'          #change
    ) 

    new_args_minority_goal = get_update(
        fig, 
        x_minority.copy(), 
        y_minority.copy(), 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_minority_scored.copy(),  #change
        minority_annotation,                        #change
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        color_goals,
        opacity_goals,
#        False                                     #change
    )

    buttons_goals = [
        dict(label = 'Goals',
            method = 'update',
#            args=[{
#                   'x': x_goals, 
#                   'y': y_goals, 
#                   'marker.opacity': all_marker_opacity_goal,
#                },
#                {
#                f'annotations[{i}].text': goal_annotation[i] for i in range(count_team)
#                },
#                ]
            args   = new_args_goal
            ),
        dict(label = 'Normal goals',
            method = 'update',
            args   = new_args_normal_goal
            ), 
        dict(label = 'Penalty',
            method = 'update',
            args   = new_args_penalty_goal
            ), 
        dict(label = 'Missed Penalty',
            method = 'update',
            args   = new_args_missed_penalty_goal
            ), 
        dict(label = 'Own goals',
            method = 'update',
            args   = new_args_own_goal
            ), 
        dict(label='Extra time',
            method='update',
            args   = new_args_extra_goal
            ), 
        dict(label='In the majority',
            method='update',
            args   = new_args_majority_goal
            ), 
        dict(label='In the minority',
            method='update',
            args   = new_args_minority_goal
            ), 
    ]

    #Настройка карточек
    color_cards = ['white', 'red', 'yellow']
    opacity_cards = [0, 1, 1]
    
    stat_0 = [0, 0, 0]
    my_text = dict(
        type = 'Cards Yellow/Red',
        name = target_annotation_card  
    ) 

    new_args_card = get_update(
        fig, 
        x_cards, 
        y_cards, 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_card.copy(), 
        cards_annotation, 
        x_name,
        my_text,
        stat_0,
        stat_red,
        stat_yellow,
        color_cards,
        opacity_cards
    )

    #Настройка замен
    color_subst   = ['white', 'white', 'lightgreen']
    opacity_subst = [0, 0, 1]
    
    stat_0 = [0, 0, 0]
    stat_1 = [0, 0, 0]
    my_text = dict(
        type = 'Substitutions',
        name = target_annotation_subst  
    ) 

    new_args_subst = get_update(
        fig, 
        x_subst, 
        y_subst, 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_subst.copy(), 
        subst_annotation, 
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_subst,
        color_subst,
        opacity_subst
    )

    #Настройка VAR
    color_var   = ['white', 'white', 'lightgreen']
    opacity_var = [0, 0, 1]
    
    stat_0 = [0, 0, 0]
    stat_1 = [0, 0, 0]
    my_text = dict(
        type = 'VAR',
        name = target_annotation_var  
    ) 

    new_args_var = get_update(
        fig, 
        x_var, 
        y_var, 
        color_marker_goals.copy(), 
        symbol_marker_goals, 
        all_marker_opacity_var.copy(), 
        var_annotation, 
        x_name,
        my_text,
        stat_0,
        stat_1,
        stat_var,
        color_var,
        opacity_var
    )

    buttons = [
        dict(label ='Cards',
            method ='update',
            args   = new_args_card
        ),

        dict(label='Subst',
            method='update',
            args   = new_args_subst
        ),

        dict(label='Var',
            method='update',
            args   = new_args_var
        ),
        ]

    # Обновление layout updatemenus с использованием кнопок
    
    fig.update_layout(
        updatemenus = [
            dict(
                type       = 'dropdown',
                direction  ='down',
                buttons    = buttons_goals,
                showactive = True,
                active     = 0,
                bgcolor    = 'lightgrey',  # Цвет фона кнопок
                font       = dict(color = 'black'),  # Цвет шрифта кнопок
                x          = 0.02,
                xanchor    = 'left',
                y          = 1.0,
                yanchor    = 'top'
            ),
            dict(
                type       ='buttons',
                direction  ='down',
                buttons    = buttons,
                showactive = False,
#                active     = 0,
                bgcolor    = 'lightgrey',  # Цвет фона кнопок
                font       = dict(color = 'black'),  # Цвет шрифта кнопок
                x          = 0.02,
                xanchor    = 'left',
                y          = 1 - ((1 - 0.85)/len(sorted_team_list)) if len(sorted_team_list) > 1 else 0.8,
                yanchor    = 'top'
            )
        ],
    )
    #print("y: ", str(1 - ((1 - 0.85)/len(sorted_team_list)) if len(sorted_team_list) > 1 else 0.8))
    # Tracing
    end_time = time.time()
    execution_time = end_time - start_time
#    print("Время выполнения UPDATEMENUES:", execution_time, "секунд")
    start_time = time.time()
    # Tracing

    # НЕ УДАЛЯТЬ Uploads dumps НЕ УДАЛЯТЬ **************************
    # НЕ УДАЛЯТЬ Uploads dumps НЕ УДАЛЯТЬ **************************
    # НЕ УДАЛЯТЬ Uploads dumps НЕ УДАЛЯТЬ **************************
    ''' 
    my_dict = {'y_goals'    : y_goals, 
               'y_cards'    : y_cards, 
               'y_subst'    : y_subst, 
               'y_var'      : y_var, 
               'x_majority' : x_majority, 
               'x_minority' : x_minority,
               'y_majority' : y_majority, 
               'y_minority' : y_minority,
               'all_marker_opacity_goal' : all_marker_opacity_goal,
               'all_marker_opacity_penalty_scored' : all_marker_opacity_penalty_scored,
               'all_marker_opacity_card' : all_marker_opacity_card,
               }

    upload_dump(fig, sorted_team_list, my_dict)
    '''
    # НЕ УДАЛЯТЬ Uploads dumps НЕ УДАЛЯТЬ **************************

    # Tracing
    end_time = time.time()
    execution_time = end_time - start_time
#    print("Время выполнения upload_dump:", execution_time, "секунд")
    start_time = time.time()
    # Tracing
 
    return fig

def get_update(
        fig, 
        x_value, 
        y_value, 
        color, 
        symbol, 
        gl_opacity, 
        annotation, 
        y_name,
        my_text,
        stat_0,
        stat_1,
        stat_2,
        my_color, 
        my_opacity,
        stat_visible = True
        ):
    
    count_data   = len(fig.data)
    count_teams  = len(y_name)

    stat_2.reverse()
    stat_1.reverse()
    stat_0.reverse()

    x_value.append(stat_0) 
    x_value.append(stat_1)
    x_value.append(stat_2)
    y_value.append(y_name)
    y_value.append(y_name)
    y_value.append(y_name)
    
    my_visible = []
    
    for i in range(len(fig.data)):
        if stat_visible:
            if i < len(fig.data):
                my_visible.append(True)
        else:        
            if i < len(fig.data) - 3:
                my_visible.append(True)
            else:       
                my_visible.append(False)

    for i in range(3):
        color.append(my_color[i])
        gl_opacity.append(my_opacity[i])

    len_ann = len(fig.layout.annotations)
    
    new_annotation = []
    
    for i in range(len_ann):
        new_annotation.append(fig.layout.annotations[i].text)
    
#    # Для обновления annotations.text
    for i in range(len_ann - 2*len(y_name), len_ann - len(y_name)):
        new_annotation[i] = annotation[i - (len_ann - 2*len(y_name))] 

    if stat_visible:
        for i in range(len_ann - len(y_name), len_ann):
            j = i - (len_ann - len(y_name))
            if all(item == 0 for item in stat_0) and all(item == 0 for item in stat_1):
                new_annotation[i] = y_name[j] + ': ' + str(stat_2[j])
            elif all(item == 0 for item in stat_0):
                new_annotation[i] = y_name[j] + ': ' + str(stat_2[j]) + '/' + str(stat_1[j])
            else:
                new_annotation[i] = y_name[j] + ': ' + str(stat_2[j]) + '/' + str(stat_1[j]) + '/' + str(stat_0[j])
    else:
        for i in range(len_ann - len(y_name), len_ann):
            new_annotation[i] = ''

     
    my_range_max = max(max(stat_0), max(stat_1), max(stat_2))
    my_range_min = min(min(stat_0), min(stat_1), min(stat_2))

    y_list_green = [num + 0.5 for num in range(len(y_name))]

    new_args = {
        'yaxis' + str(2*len(y_name) - 1) + '.title.text' : my_text['type'],
        'xaxis' + str(2*len(y_name) - 1) + '.range' : [my_range_max, (my_range_min if my_range_min < 0 else 0)],
        'yaxis' + str(2*len(y_name) - 1) + '.visible' : stat_visible,
        'xaxis' + str(2*len(y_name) - 1) + '.visible' : stat_visible,
    }

    args_2 = {**new_args, **{f'annotations[{i}].text': value for i, value in enumerate(new_annotation, start=0)}}
    args_3 = {**args_2,   **{f'annotations[{i}].name': my_text['name'] for i in range(len_ann - 2*len(y_name), len_ann - len(y_name))}}
    args_4 = {**args_3,   **{f'annotations[{i}].name': my_text['name'] for i in range(len_ann - len(y_name), len_ann)}}
    args_5 = {**args_4,   **{f'annotations[{i}].xref': "x" + str(2*len(y_name) - 1) for i in range(len_ann - len(y_name), len_ann)}}
    args_6 = {**args_5,   **{f'annotations[{i}].yref': "y" + str(2*len(y_name) - 1) for i in range(len_ann - len(y_name), len_ann)}}
    args_7 = {**args_6,   **{f'annotations[{i}].x': my_range_min/2 if my_range_min < 0 else my_range_max/10  for i in range(len_ann - len(y_name), len_ann)}}
    args_8 = {**args_7,   **{f'annotations[{i}].y': y_list_green[i - (len_ann - len(y_name))] for i in range(len_ann - len(y_name), len_ann)}}

    args_1 = {
            'x': x_value, 
            'y': y_value, 
#            'visible' : my_visible,
            'marker.color': color, 
            'marker.symbol': symbol, 
            'marker.opacity': gl_opacity,
    }
    
    my_args = [args_1, args_8]

    return my_args

def flatten_list(lst):
    flattened = []
    for item in lst:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened

def get_indexes(lst, values):
    indexes = []
    for i, row in enumerate(lst):
        row_indexes = []
        for j, item in enumerate(row):
            if item in values:
                row_indexes.append(j)
        indexes.append(row_indexes)
    return indexes

def update_annotations(fig, slider_range, dim, sorted_team_list, team_id, event, marker_symbol):
    
    global extra_events

    stat_x = {}
    for i in range(2):
        if i == 0:
            for j in range(6):
                for k in range(3):
                    stat_x[f'x_{str(i)}_{str(j)}_{str(k)}'] = []
        else:
            for j in range(3):
                for k in range(3):
                    stat_x[f'x_{str(i)}_{str(j)}_{str(k)}'] = []

    len_ann = len(fig.layout.annotations)    

    for t in range(len(dim)):
        if t == 0:
            offset = 0
        else:
            offset = sum(dim[:t])
 
        my_annotation            = []
        goal_annotation          = []
        other_annotation         = []
        
        sh_my_annotation         = []
        sh_goal_annotation       = []
        sh_other_annotation      = []

        my_goal_scored           = 0
        my_normal_goal_scored    = 0
        my_penalty_scored        = 0
        my_missid_penalty_scored = 0
        my_own_goal_scored       = 0 
        my_extra_goal_scored     = 0 
        my_goal_missed           = 0
        my_normal_goal_missed    = 0
        my_penalty_missed        = 0
        my_missid_penalty_missed = 0
        my_own_goal_missed       = 0 
        my_extra_goal_missed     = 0 
        my_yellow                = 0
        my_red                   = 0
        my_subst                 = 0
        my_var                   = 0

        team = sorted_team_list[t]['name_id']
        time_range = ' in time from: ' + str(slider_range[0]) + ' to: ' + str(slider_range[1]) + '| Team: ' + sorted_team_list[t]['name']
        sh_time_range = ' time: ' + str(slider_range[0]) + '<->' + str(slider_range[1])
        str_time = str(slider_range[0]) + '<->' + str(slider_range[1])
   
        for i, trace in enumerate(itertools.islice(marker_symbol, offset, offset + dim[t]), start = offset):
            for j, item in enumerate(trace):
                value = event[i][j]
                if slider_range[0] <= value <= slider_range[1]:
                    if team_id[t][i - offset][j] == team:
                        if item == 0:
                            my_normal_goal_scored += 1
                        if item == 5:
                            my_penalty_scored += 1
                        if item == 6:
                            my_missid_penalty_scored += 1
                        if item == 2:
                            my_own_goal_scored += 1
                        if  item == 0 or item == 5 or item == 6 or item == 2:
                            my_goal_scored += 1
                            if extra_events[i][j] > 0:
                                my_extra_goal_scored += 1
                        if item == 1:
                            my_yellow  += 1
                        if item == 201:    
                            my_red     += 1
                        if item == 26:   
                            my_subst   += 1
                        if item == 17:    
                            my_var     += 1

                    else:
                        if item == 0:
                            my_normal_goal_missed += 1
                        if item == 5:
                            my_penalty_missed += 1
                        if item == 6:
                            my_missid_penalty_missed += 1
                        if item == 2:
                            my_own_goal_missed += 1
                        if  item == 0 or item == 5 or item == 6 or item == 2:
                            my_goal_missed += 1
                            if extra_events[i][j] > 0:
                                my_extra_goal_missed += 1

        goal_annotation.append('Scored: '  + str(my_goal_scored)           + ' | Missed: ' + str(my_goal_missed)           + time_range)
        goal_annotation.append('Scored: '  + str(my_normal_goal_scored)    + ' | Missed: ' + str(my_normal_goal_missed)    + time_range)
        goal_annotation.append('Scored: '  + str(my_penalty_scored)        + ' | Missed: ' + str(my_penalty_missed)        + time_range)
        goal_annotation.append('Scored: '  + str(my_missid_penalty_scored) + ' | Missed: ' + str(my_missid_penalty_missed) + time_range)
        goal_annotation.append('Scored: '  + str(my_own_goal_scored)       + ' | Missed: ' + str(my_own_goal_missed)       + time_range)
        goal_annotation.append('Scored: '  + str(my_extra_goal_scored)     + ' | Missed: ' + str(my_extra_goal_missed)     + time_range)
        other_annotation.append('Yellow: ' + str(my_yellow)                + ' | Red: '    + str(my_red)                   + time_range)
        other_annotation.append('Subst: '  + str(my_subst) + time_range)
        other_annotation.append('Var: '    + str(my_var)   + time_range)
        my_annotation.append(goal_annotation)
        my_annotation.append(other_annotation)
    
        sh_goal_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_goal_scored)           + '/' + str(my_goal_missed)           + '/' + str(my_goal_scored - my_goal_missed))
        sh_goal_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_normal_goal_scored)    + '/' + str(my_normal_goal_missed)    + '/' + str(my_normal_goal_scored - my_normal_goal_missed))
        sh_goal_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_penalty_scored)        + '/' + str(my_penalty_missed)        + '/' + str(my_penalty_scored - my_penalty_missed))
        sh_goal_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_missid_penalty_scored) + '/' + str(my_missid_penalty_missed) + '/' + str(my_own_goal_scored - my_missid_penalty_missed))
        sh_goal_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_own_goal_scored)       + '/' + str(my_own_goal_missed)       + '/' + str(my_own_goal_scored - my_own_goal_missed))
        sh_goal_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_extra_goal_scored)     + '/' + str(my_extra_goal_missed)     + '/' + str(my_extra_goal_scored - my_extra_goal_missed))
        sh_other_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_yellow)               + '/' + str(my_red))
        sh_other_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_subst))
        sh_other_annotation.append(sorted_team_list[t]['name'] + ': ' + str(my_var))
        sh_my_annotation.append(sh_goal_annotation)
        sh_my_annotation.append(sh_other_annotation)

        for k in range(len(fig.layout.updatemenus)):
            for i in range(len(fig.layout.updatemenus[k].buttons)):
                if k == 0:
                    if i > 5:
                        break
                    else:
                        fig.layout.updatemenus[k].buttons[i].args[1]['annotations[' + str(len_ann - (2*len(dim) - t)) + '].text'] = my_annotation[k][i]
                        fig.layout.updatemenus[k].buttons[i].args[1]['annotations[' + str(len_ann - 1 - t) + '].text'] = sh_my_annotation[k][i]

                else:
                    fig.layout.updatemenus[k].buttons[i].args[1]['annotations[' + str(len_ann - (2*len(dim) - t)) + '].text'] = my_annotation[k][i]
                    fig.layout.updatemenus[k].buttons[i].args[1]['annotations[' + str(len_ann - 1 - t) + '].text'] = sh_my_annotation[k][i]

        fig.layout.annotations[len_ann - 1 - t].text = sh_my_annotation[0][0]
        
        my_row = 'y' + str((t + 1) * 2)    
    
        for i in range(len(fig['layout']['annotations'])):

            target_annotations = fig['layout']['annotations'][i]

            if target_annotations['yref'] == my_row:
                if target_annotation_goals in target_annotations['name']:
                    fig.layout.annotations[i].text = '''Scored: {}| Missed: {} in time from: {} to: {} | Team: {}'''.format(
                                                                my_goal_scored, 
                                                                my_goal_missed, 
                                                                slider_range[0], 
                                                                slider_range[1], 
                                                                sorted_team_list[t]['name']
                                                                )
                    fig.layout.annotations[i].y = slider_range[0] - 5
                    
                if target_annotation_score in target_annotations['name']:
                    fig.layout.annotations[i].y = slider_range[1] + 5

                if target_annotation_team in target_annotations['name']:
                    fig.layout.annotations[i].y = (slider_range[0] + slider_range[1])/2

        if len(dim) > 1:        
            stat_x['x_0_0_0'].append(my_goal_scored)
            stat_x['x_0_1_0'].append(my_normal_goal_scored)
            stat_x['x_0_2_0'].append(my_penalty_scored)
            stat_x['x_0_3_0'].append(my_missid_penalty_scored)
            stat_x['x_0_4_0'].append(my_own_goal_scored)
            stat_x['x_0_5_0'].append(my_extra_goal_scored)
            stat_x['x_0_0_1'].append(my_goal_missed)
            stat_x['x_0_1_1'].append(my_normal_goal_missed)
            stat_x['x_0_2_1'].append(my_penalty_missed)
            stat_x['x_0_3_1'].append(my_missid_penalty_missed)
            stat_x['x_0_4_1'].append(my_own_goal_missed)
            stat_x['x_0_5_1'].append(my_extra_goal_missed)
            stat_x['x_1_0_0'].append(my_yellow)
            stat_x['x_1_0_1'].append(my_red)
            stat_x['x_1_0_2'].append(0)
            stat_x['x_1_1_2'].append(0)
            stat_x['x_1_1_1'].append(0)
            stat_x['x_1_1_0'].append(my_subst)
            stat_x['x_1_2_2'].append(0)
            stat_x['x_1_2_1'].append(0)
            stat_x['x_1_2_0'].append(my_var)

# Обновление данныз по оси Х

    if len(dim) > 1:        
        stat_x['x_0_0_2'] = [x - y for x, y in zip(stat_x['x_0_0_0'], stat_x['x_0_0_1'])]
        stat_x['x_0_1_2'] = [x - y for x, y in zip(stat_x['x_0_1_0'], stat_x['x_0_1_1'])]
        stat_x['x_0_2_2'] = [x - y for x, y in zip(stat_x['x_0_2_0'], stat_x['x_0_2_1'])]
        stat_x['x_0_3_2'] = [x - y for x, y in zip(stat_x['x_0_3_0'], stat_x['x_0_3_1'])]
        stat_x['x_0_4_2'] = [x - y for x, y in zip(stat_x['x_0_4_0'], stat_x['x_0_4_1'])]
        stat_x['x_0_5_2'] = [x - y for x, y in zip(stat_x['x_0_5_0'], stat_x['x_0_5_1'])]
        
        len_x = len(fig.layout.updatemenus[0].buttons[0].args[0]['x'])
        
        for i in range(2):
            if i == 0:
                for j in range(6):
                    my_range_max = max(max(stat_x[f'x_{str(i)}_{str(j)}_{str(0)}']), max(stat_x[f'x_{str(i)}_{str(j)}_{str(1)}']), max(stat_x[f'x_{str(i)}_{str(j)}_{str(2)}']))
                    my_range_min = min(min(stat_x[f'x_{str(i)}_{str(j)}_{str(0)}']), min(stat_x[f'x_{str(i)}_{str(j)}_{str(1)}']), min(stat_x[f'x_{str(i)}_{str(j)}_{str(2)}']))
                    fig.layout.updatemenus[i].buttons[j].args[1]['xaxis' + str(2*len(dim) - 1) + '.range'] = [my_range_max, (my_range_min if my_range_min < 0 else 0)]

                    for k in range(3):
                        stat_x[f'x_{str(i)}_{str(j)}_{str(k)}'].reverse()

                        fig.layout.updatemenus[i].buttons[j].args[0]['x'][len_x - 1 - k] = stat_x[f'x_{str(i)}_{str(j)}_{str(k)}'] 
                        fig.layout.updatemenus[i].buttons[j].args[0]['marker.opacity'].append(1.0)
                        fig.layout.updatemenus[i].buttons[j].args[1]['annotations[' + str(len_ann - 1 - k) + '].x'] = 2 if my_range_min <= 0 else my_range_min + 2
            else:
                for j in range(3):
                    my_range_max = max(max(stat_x[f'x_{str(i)}_{str(j)}_{str(0)}']), max(stat_x[f'x_{str(i)}_{str(j)}_{str(1)}']), max(stat_x[f'x_{str(i)}_{str(j)}_{str(2)}']))
                    my_range_min = min(min(stat_x[f'x_{str(i)}_{str(j)}_{str(0)}']), min(stat_x[f'x_{str(i)}_{str(j)}_{str(1)}']), min(stat_x[f'x_{str(i)}_{str(j)}_{str(2)}']))
                    fig.layout.updatemenus[i].buttons[j].args[1]['xaxis' + str(2*len(dim) - 1) + '.range'] = [my_range_max, (my_range_min if my_range_min < 0 else 0)]

                    for k in range(3):
                        stat_x[f'x_{str(i)}_{str(j)}_{str(k)}'].reverse()

                        fig.layout.updatemenus[i].buttons[j].args[0]['x'][len_x - 1 - k] = stat_x[f'x_{str(i)}_{str(j)}_{str(k)}'] 
                        fig.layout.updatemenus[i].buttons[j].args[0]['marker.opacity'].append(1.0)
                        fig.layout.updatemenus[i].buttons[j].args[1]['annotations[' + str(len_ann - 1 - k) + '].x'] = 2 if my_range_min <= 0 else my_range_min + 2

        fig['data'][len_x - 1]['x'] = stat_x['x_0_0_0'] #53
        fig['data'][len_x - 2]['x'] = stat_x['x_0_0_1'] #52
        fig['data'][len_x - 3]['x'] = stat_x['x_0_0_2'] #51

        my_max = max(max(stat_x['x_0_0_0']), max(stat_x['x_0_0_1']), max(stat_x['x_0_0_2']))
        my_min = min(min(stat_x['x_0_0_0']), min(stat_x['x_0_0_1']), min(stat_x['x_0_0_2']))
        min_max = [my_max, (my_min if my_min < 0 else 0)]
        
        my_title = fig['layout']['yaxis' + str(2*len(dim) - 1) + '.title.text']
        substring = "time:"
        new_numbers = str_time
        pattern = re.compile(r"\btime:\s*\d+<->\d+\b")
        match = pattern.search(my_title)
        if match:
            start, end = match.span()
            my_title = my_title[:start] + substring + " " + new_numbers + my_title[end:]
        else:
            my_title = my_title + sh_time_range    
            
        fig.update_layout({'xaxis' + str(2*len(dim) - 1) : {'range' : min_max}, 'yaxis' + str(2*len(dim) - 1) + '.title.text' : my_title})
    
    # Обновляем аннотации в графике
#    fig.update_layout(annotations = fig['layout']['annotations'], updatemenus = fig.layout.updatemenus)
    
    return fig

def update_shapes(sorted_team_list, fig, slider_range):
    
    fig['layout']['shapes'] = []

    for team_index in range(len(sorted_team_list)):
        fig.add_shape(
            type = 'rect',
#            xref = 'x' if team_index == 0 else 'x' + str(team_index+1),
#            yref = 'y' if team_index == 0 else 'y' + str(team_index+1),
            xref = 'x' + str(2*team_index+2),
            yref = 'y' + str(2*team_index+2),
            x0   = 1,
            x1   = total_rounds + 1,
            y0   = slider_range[0] - 1,
            y1   = slider_range[1] + 1,
            fillcolor = "yellow",
            opacity   = 0.3,
            line      = dict(width = 0),
            layer="below"    
        )

    return fig

def update_opacity(fig, slider_range, dim, event, full):

    global opacity

    my_opacity_goal = []
    my_opacity_other = []
    my_opacity = []

    if not full:
        for sub_opacity in opacity:
            my_sub_opacity = []
            for sub_arr in sub_opacity:
                my_sub_arr = []
                for i, trace in enumerate(sub_arr):
                    my_item = []
                    for j, item in enumerate(trace):
                        value = event[i][j]
                        if sub_arr[i][j] == 1 and (slider_range[0] > value or value > slider_range[1]):
                            my_item.append(0.2)
                        else:
                            my_item.append(item)            
                    
                    my_sub_arr.append(my_item)
                
                my_sub_opacity.append(my_sub_arr)

            my_opacity.append(my_sub_opacity)

        for k in range(len(fig.layout.updatemenus)):
            for i in range(len(fig.layout.updatemenus[k].buttons)):
                if k == 0 and i > 4:
                    break
                else:
                    fig.layout.updatemenus[k].buttons[i].args[0]['marker.opacity'] = my_opacity[k][i]

        data_len = len(fig.data) - 4
        for i, row in enumerate(fig.data):
            if i > data_len:
                 break
            row['marker.opacity'] = my_opacity[0][0][i]
            
    else:
        for k in range(len(fig.layout.updatemenus)):
            for i in range(len(fig.layout.updatemenus[k].buttons)):
                if k == 0 and i > 4:
                    break
                else:
                    fig.layout.updatemenus[k].buttons[i].args[0]['marker.opacity'] = opacity[k][i]

        data_len = len(fig.data) - 4
        for i, row in enumerate(fig.data):
            if i > data_len:
                break
            row['marker.opacity'] = opacity[0][0][i]

    return fig

def init_detail(app):

    @app.callback(
        Output('graph', 'figure'),
        [Input('update-button', 'n_clicks')],
        [State('y-range-slider', 'value')],
        [State('graph', 'figure')]
        )

    def update_graph(n_clicks, slider_range, upd_fig):

        global graph

#        global fig
        global league
        global season
        global sorted_team_list
        global my_slider_range
        global full_range
        global team_dimension
        global team_arr 
        global y_value_all

        global opacity

        start_time = time.time()
#        if n_clicks == None:
#            raise PreventUpdate
        
        if n_clicks > 0:
            if slider_range[1] - slider_range[0] > 20 and slider_range[1] - slider_range[0] < 60: 
                step = 10
            elif slider_range[1] - slider_range[0] > 60: 
                step = 20
            else:
                step = 5

            my_slider_range = [round(x, -1) if x != 1 else 1 for x in slider_range]

            if my_slider_range[0] == 1 and my_slider_range[1] == 90:
                full_range = True
            else:
                full_range = False    

            if slider_range[0] == 1:
                array = list(range(slider_range[0] - 1, slider_range[1] + 1, step))
                array[0] = 1
            else:    
                array = list(range(slider_range[0], slider_range[1] + 1, step))
            
            if slider_range[1] not in array:
                array.append(slider_range[1])

    #        my_tickvals = [round(x / step) * step if x != 1 else 1 for x in array]            

            if step == 10 or step == 20:    
                my_tickvals = [round(x, -1) if x != 1 else 1 for x in array]
            else:
                my_tickvals = [round(x / 5) * 5 if x != 1 else 1 for x in array]            

            y_range = [my_tickvals[0] - 10, my_tickvals[len(my_tickvals) - 1] + 10]
            
            
    #        for i in range(0, len(sorted_team_list)):
            for i in range(2, 2 * len(sorted_team_list) + 1, 2):
                fig.update_layout(
    #                {'yaxis' + str(i+1): {
                    {'yaxis' + str(i): {
                                        'range' : y_range, 
                                        'tickvals' : my_tickvals if not full_range else [1, 45, 90]
                                        }   
                    }   
                )

            # Tracing
            end_time = time.time()
            execution_time = end_time - start_time
#            print("Время выполнения update_graph:", execution_time, "секунд")
            start_time = time.time()
            # Tracing

    #        fig = update_opacity(fig, slider_range, team_dimension, y_value_all, full_range)
            update_opacity(fig, slider_range, team_dimension, y_value_all, full_range)
            # Tracing
            end_time = time.time()
            execution_time = end_time - start_time
#            print("Время выполнения update_opacity:", execution_time, "секунд")
            start_time = time.time()
            # Tracing

    #        fig = update_annotations(fig, slider_range, team_dimension, sorted_team_list, team_arr, y_value_all, symbol_marker_goals)
            opacity = copy.deepcopy(nochange_opacity)
            update_annotations(fig, slider_range, team_dimension, sorted_team_list, team_arr, y_value_all, symbol_marker_goals)
            # Tracing
            end_time = time.time()
            execution_time = end_time - start_time
#            print("Время выполнения update_annotations:", execution_time, "секунд")
            start_time = time.time()
            # Tracing

            if full_range:
                if len(fig['layout']['shapes']) != len(sorted_team_list) * 18:    
                    for row in range(0, len(sorted_team_list)):   
    #                    fig = add_shapes(fig, row + 1)          
                        add_shapes(fig, row + 1)          
            else: 
    #            fig = update_shapes(sorted_team_list, fig, my_slider_range)
                update_shapes(sorted_team_list, fig, my_slider_range)

            # Tracing
            end_time = time.time()
            execution_time = end_time - start_time
#            print("Время выполнения update_shapes:", execution_time, "секунд")
            start_time = time.time()
            # Tracing
            return fig
        else:
            return upd_fig

    @app.callback(
        Output('graph',          'figure',    allow_duplicate = True),
        Output("y-range-slider", "className", allow_duplicate = True),
        Output("theme",          "className", allow_duplicate = True),
        Output("update-button",  "className", allow_duplicate = True),
        Output("container",      "className", allow_duplicate = True),
        Output("theme",          "children",  allow_duplicate = True),
        [Input('theme', 'n_clicks')],
        [State("y-range-slider", "className")],
        [State("theme",          "className")],
        [State("update-button",  "className")],
        prevent_initial_call='initial_duplicate')

    def update_theme(n_clicks, current_class_name, current_class_name_1, current_class_name_2):

        global graph

        global fig

        current_class_name = "slider_light"

        new_class_name = 'slider_light'
        new_name       = 'Dark theme'

        if n_clicks is not None and n_clicks > 0:
            
            if n_clicks % 2 == 0:
                new_class_name = "slider_light"
                new_name       = "Dark theme"
                fig.update_layout(plot_bgcolor  = 'white', 
                                paper_bgcolor = 'white', 
                                font          = dict(color = "black"),
                                xaxis         = dict(tickfont = dict(color="black")))
            else:
                new_class_name = "slider_dark"
                new_name       = "Light theme"
                fig.update_layout(plot_bgcolor  = 'darkgray', 
                                paper_bgcolor = 'darkgray', 
                                font          = dict(color = "white"),
                                xaxis         = dict(tickfont = dict(color="white")))

            return fig, new_class_name, new_class_name, new_class_name, new_class_name, new_name

        return graph

def set_global_current_count():

    global global_time_request

    mb.stop_signal = False

    my_time = int(time.time() - global_time_request)
    print('global my_time', my_time)
    if my_time > 60:
        mb.current_count = 0 
        global_time_request = time.time()
        print('Сброс current_count')

# Функция для фоново обновления счетчика
def background_counter():
  
    while not mb.stop_signal:
        time.sleep(1)  # Имитация задержки для обновления

def set_detail(app, my_country, my_league, my_season, my_total_rounds, my_current_round, my_sorted_team_list):

    global country
    global league
    global season
    global total_rounds
    global current_round
    global sorted_team_list

    global errors
    global fig
    global fig_height

    country          = my_country
    league           = my_league
    season           = my_season
    total_rounds     = my_total_rounds
    current_round    = my_current_round
    sorted_team_list = my_sorted_team_list

    start_time = time.time()
    fig = get_detail_games(country, league, season, sorted_team_list)
    if isinstance(fig, bool):
        if not fig:
            return fig
        
    end_time = time.time()
    execution_time = end_time - start_time
    print("Время выполнения get_detail_games:", execution_time, "секунд")
#    print('info_request: ', mb.info_request)
 
    graph = html.Div(children = [
#        dcc.Interval(id="interval", interval=1000, n_intervals=0, disabled=True),
#        html.Div(id="intermediate-output"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        id='graph',
                        figure = fig,
                        className='graph'
                    ),
        #            html.Button('Dark theme', id='theme'),
                ],
#                    style={'width': '95%', 'display': 'inline-block', 'verticalAlign': 'top'}
                    style={'width': '100%','display': 'inline-block', 'verticalAlign': 'top'}
                ),
            ],
                width = 11
            ),
            dbc.Col([
                html.Div([
                    html.Div(
                        dcc.RangeSlider(
                            id        = 'y-range-slider',
                            min       = 1,
                            max       = 90,
                            step      = 10,
                            value     = [1, 90],
                            vertical  = True,
                            verticalHeight = 250,
                            className="p-3 mh-30"
                        ), 
#                            className='centered-element'  # Центрирование элементов внутри Div
                    ),
                    dbc.Button('Update', 
                                id = 'update-button', 
                                size="sm",
                                style     = {
                                    'background-color': 'lightgreen',
                                    'color': 'black',
                                    'border': '2px solid #4CAF50',
                                    'border-radius': '12px',
                                    'font-size': '12px',
                                    'font-weight': 'bold',
                                    'box-shadow': '2px 2px 5px grey',
                                    'transition': 'background-color 0.3s'
                                },
                                n_clicks = 0
                    ),
                    html.Link(
                        rel  = 'stylesheet',
                        href = 'styles.css'
                    )
                ],
                    style = {
                        'border': '1px solid black',
                        'backgroundColor': '#f2f2f2',
                        'padding': '20px',
                        'borderRadius': '20px',
                        'margin-top': "30px",
                        "margin-left": "10px",
                        "margin-right": "10px",
                        "margin-bottom": "40px",
                        "width": '110px',
                    }
                )    
                ],
                    width = 1, 
#                    style = {
#                        'display': 'inline-block',
#    #                    'width': '50%',
#                        'border': '1px solid black',
#                        'backgroundColor': '#f2f2f2',
#                        'padding': '10px',
#                        'borderRadius': '5px',
#    #                    'margin-top': "5px",
#    #                    "margin-left": "5px",
#    #                    "margin-right": "25px",
#    #                    "margin-bottom": "5px",
#                    }
                )
            ])  
        ],  
            className="slider_light",
            id="container"
    )

    return graph
