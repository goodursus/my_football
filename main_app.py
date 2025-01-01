import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import my_lib as mb
import pandas as pd
import re
from decimal import Decimal, getcontext
from dash import dash_table
#from dash.dash_table.Format import Group
from dash.exceptions import PreventUpdate
import jmespath
#import datetime
import sys
#import pytz
#import math
import detail_data as dd
import help as hlp
import logging
from datetime import datetime
import os
import time
import threading

my_status = []

my_round         = 0
my_team          = 0
my_game          = 0
my_mode          = 1
my_league        = 0
my_season        = 0
my_events        = []
my_selected_team = []
my_games         = []
my_country       = ''
my_country_id    = 0

total_rounds    = 1
current_round   = 1
season_is_ended = False

fig_height    = 200

data_info_stand = []
my_status       = []

range_season = {}

conditionals = []

global_time_request = time.time()

stop_signal   = True  # Переменная для остановки функции обновления
current_team  = []

incache = False

#==========================================================
def get_error_message():
    
    global my_status

    my_status =  mb.get_status()

    mb.info_request['request'] = my_status[1] 
    mb.info_request['limit']   = my_status[2]

    if my_status[1] < my_status[2] - 5:
        message = html.Div('Request: ' + str(my_status[1]) + '. Total: ' + str(my_status[2]),
                            style={
                                    'fontSize': '16px',  # Задаем размер шрифта
                                    'color': 'green'  # Задаем цвет текста
                            },
                            className='error-message'
                        )
                        
    elif (my_status[1] + dd.count_games_load) > (my_status[2] - 5):
        text_message = "If request wil be continue than limit used: Request: " + str(my_status[1]) + ", Planning count request: " +  str(dd.count_games_load) + ", Total: " + str(my_status[2]) + " ( You can only use data from previous requests in the cache)."
        message = html.Div(text_message, 
                            style={
                                    'fontSize': '20px',  # Задаем размер шрифта
                                    'color': 'red'  # Задаем цвет текста
                            },
                            className='error-message'
                        )
        
        mb.info_request['mes_error'] = text_message

    else:
        text_message = "Request limit used: Request: " + str(my_status[1]) + ". Total: " + str(my_status[2] + " ( You can only use data from previous requests in the cache).")
        message = html.Div(text_message, 
                            style={
                                    'fontSize': '20px',  # Задаем размер шрифта
                                    'color': 'red'  # Задаем цвет текста
                            },
                            className='error-message'
                        )
        
        mb.info_request['mes_error'] = text_message

    info = get_info_message()
    return info    

def get_total_round(league, season):
    global total_rounds
    global season_is_ended 

    cash     = True

#    access = mb.get_access(1)
    access = True
    data_json = mb.download_and_save(access, 
                                    'Statistic/' + str(my_country) + '/' + str(league) + '/' + str(season) + '/total_round_' + str(league) + '_' + str(season) + '.json', 
                                    'fixtures/rounds?league=' + str(league) + '&season=' + str(season), cash, True, range_season)
#    print('fixtures/rounds?league=' + str(league) + '&season=' + str(season) + ':' + data_json[1])
    if not access:
        sys.exit()
    
    search_string = 'Regular Season'

    # Подсчет количества вхождений строки в каждом элементе списка
    counts = [text.count(search_string) for text in data_json[0]['response']]

    # Суммирование счетчиков
    round_results = sum(counts)

    # Отнять один раунд, который для стыковых матчей
#    round_results = data_json[0]['results'] - 1

    total_rounds = round_results 
    
    return round_results

def get_current_round(league, season):
    global current_round
    global total_rounds

    data_start = datetime.strptime(range_season['start'], '%Y-%m-%d').date()                
    data_end   = datetime.strptime(range_season['end'], '%Y-%m-%d').date() 

    current_date = datetime.now().date()

    today        = datetime.now().date()

    if today <= data_start and today >= data_end:
        current_round = total_rounds
        
        return current_round
    
    count      = 0
    cash       = True
    check_zero = False
    only_new   = True

    while True:
    #    access = mb.get_access(1)
        access = True
        data_json = mb.download_and_save(access, 
                                        'Statistic/' + str(my_country) + '/' + str(league) + '/' + str(season) + '/current_round_' + str(league) + '_' + str(season) + '.json', 
                                        'fixtures/rounds?league=' + str(league) + '&season=' + str(season) + '&current=true', cash, check_zero, range_season, only_new)
#        print('fixtures/rounds?league=' + str(league) + '&season=' + str(season) + '&current=true: ' + data_json[1])
        if not access:
            sys.exit()

        archive_date = data_json[3]

        if archive_date >= current_date or data_json[0]['results'] == 0:
            
            break
            
        else:
            count += 1
#            print('count: ' + str(count))

            cash = False

            if count == 2:
                break
    
    if data_json[0]['results'] == 0:
        current_round = total_rounds
    else:
        current_round_str = 'response[]'
        round_results = jmespath.search(current_round_str, data_json[0])

        current_round = int(re.findall(r'\d+', round_results[0])[0])
    
    dd.current_round = current_round
    return current_round

def get_info_stand(league, season):

    global my_country
    global my_round
    global my_team
    global total_rounds
    global my_games

#    result_dict_0 = mb.build_directory_0("Statistic/", league, season)
#    result_dict_0 = mb.build_directory("Statistic/", my_country, league, season)
#    if isinstance(result_dict_0, str):
#        print(result_dict)
#        exit(1)

    total_rounds = get_total_round(league, season)
#    print('total_rounds: ' + str(total_rounds))

    current_round = get_current_round(league, season)
#    print('current_round: ' + str(current_round))

    result_dict = mb.build_directory("Statistic/", my_country, league, season, current_round)
    if isinstance(result_dict, str):
    #    print(result_dict)
        exit(1)

    data_json = mb.get_fixture_league(my_country, league, season)
    
    data = pd.json_normalize(data_json[0]['response'],)
    
    teams_info  = []
    teams_score = []
    team_list   = []

    for i, row in data.iterrows():
        
        match_ok = True

        my_info  = dict()
        my_score = dict()
        my_list  = dict()
        game_id = row['fixture.id']
        
        if 'Regular Season' in row['league.round']:
            my_round = int(re.findall(r'\d+', row['league.round'])[0])
        else:
#            break
            continue

        if current_round < my_round:
            continue
        
        if not 'FT' in row['fixture.status.short']:
            match_ok = False
        
        if row['goals.home'] > row['goals.away']: # home winner   
            my_score = {'round': my_round,
                    'game_id':   game_id,    
                    'team_name': row['teams.home.name'],
                    'team_id':   row['teams.home.id'],
                    'for':       row['goals.home'] if match_ok else 0,
                    'against':   row['goals.away'] if match_ok else 0,
                    'points':    3 if match_ok else 0,
                    'status':    match_ok
            }
            teams_score.append(my_score)
            if my_round == 1:
                my_list  = {'team_name': row['teams.home.name'],
                            'team_id':   row['teams.home.id'],
                            }
                team_list.append(my_list)
            
            my_score = {'round': my_round,
                    'game_id':   game_id,    
                    'team_name': row['teams.away.name'],
                    'team_id':   row['teams.away.id'],
                    'for':       row['goals.away'] if match_ok else 0,
                    'against':   row['goals.home'] if match_ok else 0,
                    'points':    0,
                    'status':    match_ok
            }
            teams_score.append(my_score)
            if my_round == 1:
                my_list  = {'team_name': row['teams.away.name'],
                            'team_id':   row['teams.away.id'],
                            }
                team_list.append(my_list)
 
        elif row['goals.home'] < row['goals.away']: # away winner   
            my_score = {'round': my_round,
                    'game_id':   game_id,    
                    'team_name': row['teams.home.name'],
                    'team_id':   row['teams.home.id'],
                    'for':       row['goals.home'] if match_ok else 0,
                    'against':   row['goals.away'] if match_ok else 0,
                    'points':    0,
                    'status':    match_ok
            }
            teams_score.append(my_score)
            if my_round == 1:
                my_list  = {'team_name': row['teams.home.name'],
                            'team_id':   row['teams.home.id'],
                            }
                team_list.append(my_list)
             
            my_score = {'round': my_round,
                    'game_id':   game_id,    
                    'team_name': row['teams.away.name'],
                    'team_id':   row['teams.away.id'],
                    'for':       row['goals.away'] if match_ok else 0,
                    'against':   row['goals.home'] if match_ok else 0,
                    'points':    3 if match_ok else 0,
                    'status':    match_ok
            }
            teams_score.append(my_score)
            if my_round == 1:
                my_list  = {'team_name': row['teams.away.name'],
                            'team_id':   row['teams.away.id'],
                            }
                team_list.append(my_list)

        else: 
            my_score = {'round': my_round,
                    'game_id':   game_id,    
                    'team_name': row['teams.home.name'],
                    'team_id':   row['teams.home.id'],
                    'for':       row['goals.home'] if match_ok else 0,
                    'against':   row['goals.away'] if match_ok else 0,
                    'points':    1 if match_ok else 0,
                    'status':    match_ok
            }
            teams_score.append(my_score)
            if my_round == 1:
                my_list  = {'team_name': row['teams.home.name'],
                            'team_id':   row['teams.home.id'],
                            }
                team_list.append(my_list)
             
            my_score = {'round': my_round,
                    'game_id':   game_id,    
                    'team_name': row['teams.away.name'],
                    'team_id':   row['teams.away.id'],
                    'for':       row['goals.away'] if match_ok else 0,
                    'against':   row['goals.home'] if match_ok else 0,
                    'points':    1 if match_ok else 0,
                    'status':    match_ok
            }
            teams_score.append(my_score)
            if my_round == 1:
                my_list  = {'team_name': row['teams.away.name'],
                            'team_id':   row['teams.away.id'],
                            }
                team_list.append(my_list)
 
        my_info = {'round':        my_round,
                    'game_id':     game_id,    
                    'home_name':   row['teams.home.name'],
                    'home_id':     row['teams.home.id'],
                    'away_name':   row['teams.away.name'],
                    'away_id':     row['teams.away.id'],
                    'goals_home':  row['goals.home'] if match_ok else 0,
                    'goals_away':  row['goals.away'] if match_ok else 0,
        }    
        teams_info.append(my_info)

    my_list_round = []
    for my_round in range(1, current_round + 1):    
        filtered_list = list(filter(filter_by_team_round, teams_score))        
        detail_round = []
        for i in filtered_list:
            my_detail = dict()
            if i['round'] == 1:
                my_detail = {'team_id': i['team_id'],
                            'game_id':  i['game_id'],
                            'for':      i['for'],
                            'against':  i['against'],
                            'diff':     i['for'] - i['against'],
                            'win':      i['points'],
                            'points':   i['points'],
                            'status':   i['status']
                }
            else:
                my_team = i['team_id']
                my_team_list = list(filter(filter_by_team_id, my_list_round[my_round-2]))
                if not i['status']:
                    my_detail = {'team_id': my_team_list[0]['team_id'],
                                'game_id':  i['game_id'],
                                'for':      my_team_list[0]['for'],
                                'against':  my_team_list[0]['against'],
                                'diff':     my_team_list[0]['for'] - my_team_list[0]['against'],
                                'win':      my_team_list[0]['points'],
                                'points':   my_team_list[0]['points'],
                                'status':   i['status']
                    }
                else:
                    my_detail = {'team_id': my_team_list[0]['team_id'],
                                'game_id':  i['game_id'],
                                'for':      my_team_list[0]['for'] + i['for'],
                                'against':  my_team_list[0]['against'] + i['against'],
                                'diff':     (my_team_list[0]['for'] + i['for']) - (my_team_list[0]['against'] + i['against']),
                                'win':      i['points'],
                                'points':   my_team_list[0]['points'] + i['points'],
                                'status':   i['status']
                    }
            detail_round.append(my_detail)   

        my_list_round.append(detail_round)

    my_games = jmespath.search('response[0:' + str(my_round - 2) + '].[league.round, teams.home.id, fixture.id]', data_json[0])

    return [my_list_round, teams_info, team_list, my_games]

def get_team_stand(team, list_round):
    
    my_team = int(team)
    result = []
    my_round = 1
    while my_round < current_round + 1:
        sorted_list = sort_dicts(list_round[my_round-1], ['points', 'diff'])
        index = index_of_dict_value(sorted_list, 'team_id', my_team) + 1

        my_round += 1
        result.append(index)

    return result

# filter_by_round
def filter_by_team_round(item):
    global my_round
    return item['round'] == my_round

# filter_by_team_id
def filter_by_team_id(item):
    global my_team
    return item['team_id'] == my_team

def sort_dicts(list_of_dicts, keys):
    sorted_list = sorted(list_of_dicts, key=lambda x: [x[key] for key in keys], reverse=True)
    return sorted_list

def index_of_dict_value(list_of_dicts, key, value):
    for i, dict in enumerate(list_of_dicts):
        if dict[key] == value:
            return i
    return -1 # если элемент не найден

def filter_by_game_team_id(item):
    global my_team
    global my_game
    return item['game_id'] == my_game and (item['home_id'] == my_team or item['away_id'] == my_team)

def get_team_info(team, list_round, info_list, data_progress):
    global total_rounds
    global current_round
    global my_game
    global my_team
    
    results_team  = []
    results_score = []
    results_win   = []
    my_round = 1
    my_team = team

    for my_round in range(1, current_round + 1):
        list_game = list(filter(filter_by_team_id, list_round[my_round-1]))
        if not list_game[0]['status']: 
            results_score.append("Match not played yet...")
            results_win.append(-1)
            results_team.append("Match not played yet...")
            results_score_value = "Match not played yet..."
        else:
            for item in list_game:
                my_game = item['game_id']
                results_win.append(item['win'])
                list_info = list(filter(filter_by_game_team_id, info_list)) 
                for i in list_info:
                    home = i['home_name']
                    away = i['away_name']
                    goals_home = i['goals_home'] 
                    goals_away = i['goals_away'] 

                    results_score_value = str(int(goals_home)) + ":" + str(int(goals_away))

                    results_team.append(home + " - " + away + '<br>' + results_score_value)
  
    df = pd.DataFrame({
        'x': list(range(1, current_round + 1)),
        'y': data_progress,
        'name': results_team,
        'win': results_win
    })

    return df

def assign_color(val): 
    if val == 0: return '#FF0000' # Red 
    elif val == 3: return '#00FF00' # Green 
    elif val == 1: return '#FFFF00' # Yellow 
    else: return '#000000' # Black (default)

def set_standing_table(country, league, season):

    global app
    global conditionals

        # Вывод таблицы чемпионата
    my_data = mb.get_standing(country, str(league), str(season))

    base_colors = ['rgb(255, 255, 255)', 'rgb(220, 255, 220)', 'rgb(255, 220, 220)'] #Светлозеленый, Чуть темнее светлозеленого
    dark_colors = ['rgb(220, 220, 220)', 'rgb(170, 255, 170)', 'rgb(255, 170, 170)']  #Светлорозовый, Чуть темнее светлорозового

    # Добавление стилей для колонок 1 и 2 с использованием base_colors и dark_colors
    for i, column in enumerate(my_data[2][0:11]):
        conditionals.append({
            'if': {
                'column_id': column['id'],
                'row_index': 'odd'
            },
            'backgroundColor': dark_colors[0],
            'color': 'black'
        })
        conditionals.append({
            'if': {
                'column_id': column['id'],
                'row_index': 'even'
            },
            'backgroundColor': base_colors[0],
            'color': 'black'
        })

    # Добавление стилей для колонок 3 и 4
    for i, column in enumerate(my_data[2][11:19]):
        conditionals.append({
            'if': {
                'column_id': column['id'],
                'row_index': 'odd'
            },
            'backgroundColor': dark_colors[1],  # 'pink' для нечетных строк
            'color': 'black'
        })
        conditionals.append({
            'if': {
                'column_id': column['id'],
                'row_index': 'even'
            },
            'backgroundColor': base_colors[1],  # 'darkred' для четных строк
            'color': 'black'
        })

    # Добавление стилей для колонок 5 и 6
    for i, column in enumerate(my_data[2][19:27]):
        conditionals.append({
            'if': {
                'column_id': column['id'],
                'row_index': 'odd'
            },
            'backgroundColor': dark_colors[2],  # 'lightgreen' для нечетных строк
            'color': 'black'
        })
        conditionals.append({
            'if': {
                'column_id': column['id'],
                'row_index': 'even'
            },
            'backgroundColor': base_colors[2],  # 'darkgreen' для четных строк
            'color': 'black'
        })


    # Create the DataTable
    table = dash_table.DataTable(
        id            = "my-table",
        data          = my_data[0],
        columns       = my_data[2],
        merge_duplicate_headers = True,
        style_cell = {
            'textAlign': 'center',  # Default alignment for all cells
            'whiteSpace': 'normal',  # To wrap cell content if necessary
        },
        style_data_conditional = conditionals,
        row_selectable = False,
        selected_rows  = [],
        style_header   = {'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
#        hidden_columns = ['name_Id'],
   )

    # Create the Store
    store = dcc.Store(id="my-store")

#    # Create the Div to display the clicked cell data
#    output_div = html.Div(id="output-div")

    # Define your layout
    stat_container = dbc.Container(
        [
            dbc.Row([
                html.Div(id = "output", children = ''),
                dbc.Col(table,      width = 12), 
                dcc.Loading([html.Div(id = "loading-demo")]),
                dbc.Col(store,      width = 10), 
            ]),
        ],
        fluid = True,
    )
    
    return stat_container   

def set_team_graph(teams):

    global data_info_stand 
    global my_team

    data          = data_info_stand    
    list_round    = data[0]
    info_list     = data[1]
    team_list     = data[2]
    sorted_team_list =  teams
    colors = {0: 'red', 3: 'green', 1: 'yellow', -1: 'blue'}

    my_row = 1 

    if len(teams) == 0: 
        return []
    
    fig = make_subplots(rows = len(sorted_team_list), cols = 1, vertical_spacing = 0.01)

    delta = 1/len(sorted_team_list)
    str_delta = str(delta)
    subplot_height = [Decimal(str_delta) for _ in range(len(sorted_team_list))]    

    start_end_stand = []
    min_max         = []
    start_end_stand = []
    min_max         = []

    for team in sorted_team_list:


        data_progress = get_team_stand(team['name_id'], list_round)
        my_team = team
        df = get_team_info(team['name_id'], list_round, info_list, data_progress)
        
        fig.add_trace(
            go.Scatter(
                mode = 'markers+lines',
                x = df['x'], 
                y = df['y'],  
                text = df['name'], 
                hovertemplate = 'Round: %{x}<br>Stand: %{y}<br>%{text}<extra></extra>', 
                marker = dict(
                    size  = 15,
                    line  = {'width': 0.5, 'color': 'white'},
                    color = [colors.get(val, 'blue') for val in df['win']]
                ),
            ), row = my_row, col = 1
        )
        my_row += 1
        my_dict = {'start' : data_progress[0], 'end' : data_progress[len(data_progress)-1]}
        start_end_stand.append(my_dict)
        min_max.append([min(data_progress), max(data_progress)])

    fig.update_layout(showlegend=False, 
                    margin_autoexpand=True,
#                    width        = 1000,
                    margin_b   = 100,
                    margin_l   = 0,
                    margin_r   = 10,
                    margin_t   = 20,
                    margin_pad = 0,
                    hoverlabel = dict(
                                    align = 'auto',
                                    bgcolor = "blue",
                                    font_size = 16,
                                    font_family = "Rockwell"
                        )
                )

    array_tick = [1, 5, 10, 15, 20]

    for i in range(0, len(sorted_team_list)):
        if i == 0: 
            fig.update_layout(
                xaxis = {'title' : 'Rounds', 
                         'showgrid' : True, 
                         'gridcolor' : 'blue', 
                         'showticklabels': True, 
                         'tickmode' : 'array', 
                         'tickvals' : list(range(1, total_rounds)), 
                         'automargin' :True, 
                         'range' : [0.8, current_round + 0.2]
                         },    
                yaxis     = {'title_text' : sorted_team_list[i]['name'], 
                                    'rangemode' : 'normal', 
#                                   'autorange' : 'reversed',
                                    'range' : [25, -5],
                                    'tickmode' : 'array', 
#                                   'tickvals' : min_max_val, 
#                                    'tickvals' : list(range(1, 21, 5)), 
                                     'tickvals' : array_tick, 
                                   'tickcolor' : 'blue', 
                                    'gridcolor' : 'blue',
                                    'tick0' : 5, 
                                    'dtick': 5, 
                                    'automargin' :True,
                                    'showgrid' : True,  
                                    'title_standoff' : 25,
#                                    'showline'  : True, 
#                                    'zeroline'  : True
                            }
            )    
        else:            
            fig.update_layout(
                **{f'xaxis{i+1}': {'showgrid' : True, 
                                    'gridcolor' : 'blue', 
                                    'showticklabels': False, 
                                    'tickmode' : 'array', 
                                    'tickvals' : list(range(1, total_rounds)), 
                                    'automargin' :True, 
                                    'range' : [0.8, current_round + 0.2]
                                    }},         
                **{f'yaxis{i+1}': {'title_text' : sorted_team_list[i]['name'], 
                                    'rangemode' : 'normal', 
#                                   'autorange' : 'reversed',
                                    'range' : [25, -5],
                                    'tickmode' : 'array', 
#                                   'tickvals' : min_max_val, 
                                    'tickvals' : array_tick, 
                                    'tickcolor' : 'blue', 
                                    'gridcolor' : 'blue',
                                    'tick0' : 5, 
                                    'dtick': 5, 
                                    'automargin' :True,
                                    'showgrid' : True,  
                                    'title_standoff' : 25,
#                                    'showline'  : True, 
#                                    'zeroline'  : True
                                    }}
            )

    for i, height in enumerate(subplot_height):
        fig.update_layout(
            {'yaxis' + str(i+1): {'domain': [sum(subplot_height[:i]), 
                                            sum(subplot_height[:i+1])]}}
        )

    fig.update_layout(height = fig_height * len(sorted_team_list) if len(sorted_team_list) > 1 else fig_height + 100,
                        plot_bgcolor  = "white",
                        paper_bgcolor = "white",
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
            'displayModeBar': False
            }

    return [dcc.Graph(figure = fig, config = conf)]

def set_add_graph(teams):
    
    return                                 

def set_list_team_graph(teams):

    global total_rounds
    global data_info_stand 
    global my_mode
    global my_league
    global my_season
    global current_round

    if my_mode  == 1:
        return set_team_graph(teams)
    elif my_mode == 2:
        if len(teams) == 0:
            return ""
        else:
            result = dd.set_detail(app,
                                my_country,    
                                my_league, 
                                my_season, 
                                total_rounds, 
                                current_round, 
                                teams)
            return result
    else:
        return set_add_graph(teams)   

def get_list_countries():
    
    data_json = mb.download_and_save(True, 'Statistic/Countries.json', 'countries', True, True, range_season)
    if isinstance(data_json[0], str):
        return data_json[1]
    else:    
        data = pd.json_normalize(data_json[0]['response'],)
        countries = []

        for i, row in data.iterrows():
            my_dict = dict()
            my_dict = {"label": html.Span(
                    [
                        html.Img(src = row['flag'], height=20),
                        html.Span(row['name'], style={'font-size': 15, 'padding-left': 10}),
                    ], style={'align-items': 'center', 'justify-content': 'center'}
                ), 
                'value': row['name']}
        
            countries.append(my_dict)

        return countries

def get_list_leagues(country):

    if country == None:
        return []
    
    data_json = mb.download_and_save(True, 'Statistic/' + country + '/' + 'leagues_' + country +'.json', 'leagues?country=' + country, True, True, range_season)
    data = pd.json_normalize(data_json[0]['response'],)
    leagues = []

    for i, row in data.iterrows():
        my_dict = dict()
        my_dict = {"label": html.Span(
                [
                    html.Img(src=row[4], height=20),
                    html.Span(row[2], style={'font-size': 15, 'padding-left': 10}),
                ], style={'align-items': 'center', 'justify-content': 'center'}
            ), 
            'value': row[1]}

        leagues.append(my_dict)

    return leagues

def get_list_leagues_seasons(country, parametr):

    if parametr == None:
        return []

    data_json = mb.download_and_save(True, 'Statistic/' + country + '/' + str(parametr) + '/' + 'leagues_' + parametr +'.json', 'leagues?id=' + parametr, True, True, range_season)
    data_leagues = pd.json_normalize(data_json[0]['response'][0]['seasons'],)
    data = data_leagues
    seasons = []

    for i, row in data.iterrows():
        my_dict = dict()
        my_dict["label"] = str(row['year'])
        my_dict["value"] = row['year']
        seasons.append(my_dict)
        
    return seasons

def set_global_current_count():

    global global_time_request
    global stop_signal

#    stop_signal = False

    my_time = int(time.time() - global_time_request)
    print('global my_time', my_time)
    if my_time > 60:
        mb.current_count = 0 
        global_time_request = time.time()
        print('Сброс current_count', my_time)

 #mb.setup_logger()

def get_info_message():

    request     = f"today request: {mb.info_request['request']} from {mb.info_request['limit']}"
    round       = f"round: {mb.info_request['round']}"
    count       = f"count: {mb.info_request['count']}"
    delay       = f"delay: {mb.info_request['delay']}"
    count_delay = f"count delay: {mb.info_request['count_delay']}"
    request     = f"request: {mb.info_request['request']} from {mb.info_request['limit']}"
    mes_error   = f"error: {mb.info_request['mes_error']}"

#    team = ''
    team = 'My team'
#    if current_team and mb.info_request['team'] != 'My team':
#        team = [team for team in current_team if team["name_id"] == mb.info_request['team']][0]['name'] 

    for i in current_team:
        if mb.info_request['team'] != 'My team':
            if i['name_id'] == mb.info_request['team']:
                team = i['name']    

    info =  [
            dbc.Badge(request,     id = "output_request", color="primary", text_color="light", className="ms-1 fs-6 text"),
            dbc.Badge(team,        id = "output_team", color="success", text_color="light", className="ms-1 fs-6 text"),
            dbc.Badge(round,       id = "output_round", color="success", text_color="light", className="ms-1 fs-6 text"),
            dbc.Badge(count,       id = "output_count", color="success", text_color="light", className="ms-1 fs-6 text"),
            dbc.Badge(delay,       id = "output_delay", color="success", text_color="light", className="ms-1 fs-6 text"),
            dbc.Badge(count_delay, id = "output_counr_delay", color="warning", text_color="black", className="ms-1 fs-5 text"),
            dbc.Badge(mes_error,   id = "output_error", color="danger", text_color="black", className="ms-1 fs-6 text"),
        ]       

    return info

def create_colored_dropdown(options_dict, folder_path):
    
    existing_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    
    # Создаем список опций с стилизацией
    formatted_options = []
    for option in options_dict:
        # Извлекаем название страны из значения label
        country_name = option['value']
        
        # Проверяем наличие папки
        is_folder_exists = country_name in existing_folders
        
        # Получаем оригинальный Span из label
        original_span = option['label']
        
        # Создаем новый Span с измененным стилем
        new_span = html.Span(
            [
                original_span.children[0],  # Изображение флага
                html.Span(
                    original_span.children[1].children,  # Текст названия страны
                    style={
                        'font-size': 15, 
                        'padding-left': 10,
                        'color': 'red' if is_folder_exists else 'black',
                        'font-weight': 'bold' if is_folder_exists else 'normal'
                    }
                )
            ],
            style={'align-items': 'center', 'justify-content': 'center'}
        )
        
        # Создаем новую опцию
        new_option = {
            'label': new_span,
            'value': option['value']
        }
        
        formatted_options.append(new_option)

    return formatted_options

def create_country_dropdown(options_dict, folder_path):
    
    existing_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    
    # Создаем список опций с стилизацией
    new_options = []
    for option in options_dict:
        # Извлекаем название страны из значения label
        country_name = str(option['value'])
        
        # Проверяем наличие папки
        is_folder_exists = country_name in existing_folders
        
        if is_folder_exists:
            new_options.append(option)

    return new_options

# Функция для получения структуры папок
def get_folder_structure(root_path):
    folder_structure = {}
    if os.path.exists(root_path):
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path):
                folder_structure[item] = [
                    subfolder for subfolder in os.listdir(item_path)
                    if os.path.isdir(os.path.join(item_path, subfolder))
                ]
    return folder_structure

#logging.info("**********************  Start *******************")

ROOT_PATH = "Statistic"  # Укажите путь к корневой папке
folder_structure = get_folder_structure(ROOT_PATH)
info_string = get_error_message()

#app/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
app = dash.Dash(__name__, 
                suppress_callback_exceptions = True, 
                prevent_initial_callbacks = 'initial_duplicate', 
                external_stylesheets=[dbc.themes.BOOTSTRAP], 
                assets_folder='assets'
                )
#app = dash.Dash(__name__, suppress_callback_exceptions=True, prevent_initial_callbacks = 'initial_duplicate')

# Flask сервер для Gunicorn
server = app.server

#app.layout = dbc.Container([
app.layout = html.Div(children = [

    dcc.Interval(id = "interval", interval = 1000, n_intervals = 0, disabled = True), #init True
#    html.Div(id = 'error-message', style = {'display': 'block'}, children = get_error_message()),
    html.Div(id = 'error-message', children = [
#        html.Span(id = 'output_info', children = get_info_message()), 
        html.Span(id = 'output_info', children = info_string), 
        ]),        
    
    dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Dropdown(
                        id='dropdown',
                        options=[
                            {'label': 'English', 'value': 'item1'},
                            {'label': 'Another', 'value': 'item2'}
                        ],
                        placeholder="Chose lenguage for help",
                        className="w-75 text-black shadow mt-3 ms-5 mb-3 bg-white rounded", # p-1
                    ),
                    
                    dbc.Modal(
                        [
                            dbc.ModalHeader(id="modal-header"),
                            dbc.ModalBody(id="modal-body"),
                        ],
                        id      = "modal",
                        is_open = False,
                        size="lg"  # Размер модального окна: 'sm', 'lg', 'xl'
                    ),
                ]),
                html.Div([
                    # Переключатель Да-Нет
                    html.Div([
#                        html.Label("Already exists: "),
                        dbc.Switch(
                                id    = "exists-radio",
                                label = "Already in cache: ",
                                value = False,
                    )]),    

                    html.P("Country"),
                    dcc.Dropdown(
                        id        = "select_country",
#                        options   = get_list_countries(),
                        options   = create_colored_dropdown(get_list_countries(), 'Statistic'),
#                        value     = 'England',
#                        value     = 'Ukraine',
                        clearable = False
                    ),
                    html.P("League"),
                    dcc.Dropdown(
                        id        = "select_league",
#                        value     = 39,
#                        value     = 333,
                        clearable = False
                    ),
                    html.P("Season"),
#                               dbc.Select(
                    dcc.Dropdown(
                        id = "select_season",
#                                   placeholder = 'Выберите сезон.',
#                                   value = 2024
                    )
                ],
                    style = {
                        'border': '1px solid black',
                        'backgroundColor': '#f2f2f2',
                        'padding': '20px',
                        'borderRadius': '20px',
                        'margin-top': "10px",
                        "margin-left": "20px",
                        "margin-right": "30px",
                        "margin-bottom": "40px",
                     }
                ),
                html.Div(id = 'mode'
                     )
                ],
                width = 2
#                width={'size': 3}
            ),
            dbc.Col(width = 10, children = html.Div(id = 'standing')), #, style={"height": "70vh"},)
            ]
    ),
    dbc.Row(
        [
            dbc.Col(id = 'detail', width = 12, children = html.Div(id = 'graph-container'))
        ]
    ),
    dd.init_detail(app)
])

# Callback для обновления списка стран
@app.callback(
    Output('select_country', 'options'),
    [Input('exists-radio', 'value')]
)
def update_country_dropdown(exists):

    global incache

    if exists:
        incache = True
        # Показываем только существующие папки
        return create_country_dropdown(get_list_countries(), 'Statistic')
    else:
        incache = False
        # Показываем все страны
        return create_colored_dropdown(get_list_countries(), 'Statistic')

@app.callback(
    Output('select_league', 'options'),
    Input('select_country', 'value'),
    prevent_initial_call='initial_duplicate'
    )
def set_country_options(selected_country): # формируем список лиг выбранной страны
    global my_status
    global stop_signal
    global my_country
    global incache

#    message = get_error_message()

    if selected_country == None:
        raise PreventUpdate

    if my_status[0]:
        set_global_current_count()
        result_dict = mb.build_directory("Statistic/", selected_country)
        if isinstance(result_dict, str):
            print('exit: ', result_dict)
            exit(1)

        if incache:
            # Показываем только существующие папки
            list_leagues = create_country_dropdown(get_list_leagues(selected_country), 'Statistic/' + selected_country)
        else:
           # Показываем все страны
            list_leagues = create_colored_dropdown(get_list_leagues(selected_country), 'Statistic/' + selected_country)

#        list_leagues = get_list_leagues(selected_country)
        mb.info_request['team'] = 'My team'
        my_country = selected_country
    else:
        list_leagues = []
  
#    return list_leagues, message
    return list_leagues

@app.callback(  #select_league
    Output('select_season', 'options'),
    Output('select_season', 'value'),
    Input('select_league', 'value'),
    prevent_initial_call='initial_duplicate'
    )
def set_leagues_options(selected_league): # подготовка списка сезонов выборанной лиги
    global my_status
    global stop_signal

    if selected_league == None:
        raise PreventUpdate

    if my_status[0]:
        str_league = str(selected_league)
        set_global_current_count()
        result_dict = mb.build_directory("Statistic/", my_country, selected_league)
        if isinstance(result_dict, str):
            print('exit: ', result_dict)
            exit(1)

        if incache:
            # Показываем только существующие папки
            list_season = create_country_dropdown(get_list_leagues_seasons(my_country, str_league), 'Statistic/' + my_country + '/' + str_league)
        else:
           # Показываем все страны
            list_season = create_colored_dropdown(get_list_leagues_seasons(my_country, str_league), 'Statistic/' + my_country + '/' + str_league)

#        list_season = get_list_leagues_seasons(my_country, str_league)
#        stop_signal = True
        sorted_options = sorted(list_season, key=lambda x: x['label'], reverse=True)
    else:
        sorted_options = []

    return sorted_options, None
    
@app.callback(
    Output('standing', 'children'), 
    Output('mode',     'children'), 
    Input('select_season', 'value'),
    State('select_country', 'value'),
    State('select_league', 'value'),
    prevent_initial_call='initial_duplicate'
)
def update_graph(select_season, country, select_league):
    global total_rounds
    global data_info_stand
    global my_country
    global my_league
    global my_season
    global my_status
    global range_season
    global stop_signal
    global my_selected_team

    my_selected_team = []
    
    if select_season == None:
        raise PreventUpdate

    result_dict = mb.build_directory("Statistic/", country, select_league, select_season)
    if isinstance(result_dict, str):
        print('exit: ', result_dict)
        exit(1)

    set_global_current_count()
    range_season = mb.get_rang_season('Statistic/' + country + '/' + str(select_league) + '/' + 'leagues_' + str(select_league) +'.json', select_season)

    my_country = country
    my_league  = select_league
    my_season  = select_season

    if my_status[0]:
        standing = set_standing_table(country, str(select_league), str(select_season))

        mode =  html.Div([
                    dbc.RadioItems(
                        id="radios",
                        className="btn-group-vertical d-sm-flex",  # Вертикальное расположение кнопок
                        options=[
                            {"label": "By Rounds", "value": 1},
                            {"label": "By Goals", "value": 2},
                            {"label": "By Anything", "value": 3},
                        ],
                        value = 1,
                    )],
                        style = {
                            'border': '1px solid black',
                            'backgroundColor': '#f2f2f2',
                            'padding': '20px',
                            'borderRadius': '20px',
                            'margin-top': "10px",
                            "margin-left": "20px",
                            "margin-right": "30px",
                            "margin-bottom": "40px",
                            }
                )

        data_info_stand = get_info_stand(my_league, my_season) 
    else:
        standing = dbc.Container([])
    
#    stop_signal = True

    return standing, mode

@app.callback(
    Output('my-table', 'selected_rows'),
    Output('my-table', 'style_data_conditional'),
    Output('graph-container', 'children', allow_duplicate = True), 
    Input('my-table', 'active_cell'),
    State('my-table', 'selected_rows'),
    State('my-table', 'style_data_conditional'),
    State('my-table', 'derived_virtual_data'),
    prevent_initial_call='initial_duplicate'
)
def process_selected_rows(active_cell, selected_rows, style_data_conditional, rows):

    global my_selected_team
    global conditionals
    global stop_signal
    global current_team

    my_graph = None
    
    if active_cell:
        selected_row = active_cell['row']
        if selected_row in selected_rows:
            # Deselect the row if it was already selected
            selected_rows.remove(selected_row)
            conditionals.remove({
                'if': {
                    'row_index': selected_row
                },
                'backgroundColor': 'lightblue',
                'color': 'black'
            })
        else:
            # Select the row if it was not already selected
            selected_rows.append(selected_row)
            conditionals.append({
                'if': {
                    'row_index': selected_row
                },
                'backgroundColor': 'lightblue',
                'color': 'black'
            })
        
        if selected_rows:
            selected_data = [rows[i] for i in selected_rows]
            selected_keys = ["name_id", "name"]
            selected_team = []
            for index in selected_rows:
                if index < len(rows):
                    item = rows[index]
                    selected_item = {key: item[key] for key in selected_keys}
                    selected_team.append(selected_item)
            output_text = f"You selected {len(selected_data)} rows:\n"
            current_team = selected_team

            set_global_current_count()
            my_graph = set_list_team_graph(selected_team)
#            stop_signal = True
            my_selected_team = selected_team

            return selected_rows, conditionals, my_graph
        
        else:
            
            return selected_rows, conditionals, my_graph
    
    return selected_rows, conditionals, my_graph

@app.callback(
    Output("output", "children"), 
    Output('graph-container', 'children', allow_duplicate = True),
    Output("loading-demo", "children"),
    Output("error-message", "children"), 
    Input("radios", "value"),
    prevent_initial_call='initial_duplicate'
    )
def display_value(value):
    global my_mode
    global data_info_stand
    global my_league
    global my_season
    global my_events
    global my_selected_team
    global total_rounds 
    global current_round
    global stop_signal

    my_mode = value
    if my_mode == 1:

#        stop_signal = False
#        stop_signal = True
#        print('stop_signal False Input("radios", "value"): ', value)
        set_global_current_count()
        my_graph = set_list_team_graph(my_selected_team)
#        stop_signal = True
#        print('stop_signal False Input("radios", "value"): ', value)
        message = 'Displaying the movement of teams in the ranking by rounds'

        return message, my_graph, '', get_error_message()

    elif my_mode == 2:

        stop_signal = False
        print('set stop_signal = False and Input("radios", "value"): ', value)
        set_global_current_count()
        my_graph = dd.set_detail(app,
                                my_country, 
                                my_league, 
                                my_season, 
                                total_rounds, 
                                current_round, 
                                my_selected_team)
#        stop_signal = True
#        print('stop_signal True Input("radios", "value"): ', value)
        
        message = 'When teams scored and conceded in rounds.'  

        if isinstance(my_graph, bool):
            if not my_graph:
                stop_signal = True
                print('set stop_signal = True, radios = 2 and my_graph = ', my_graph)
                return message, '', '', get_error_message()

        else:
            stop_signal = True
            print('set stop_signal = True, radios = 2 and type of my_graph =  ', type(my_graph))
            return message, my_graph, '', get_error_message()

    else:
        result = 'Other statistics'          
    return result, '', ''

# HELP, HELP
@app.callback(
    Output('modal',        'is_open'),
    Output('modal-header', 'children'),
    Output('modal-body',   'children'),
    Input('dropdown',      'value'),
    prevent_initial_call = True
)
def display_modal(selected_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    if ctx.triggered[0]['prop_id'] == 'close-modal.n_clicks':
        return False, "", ""
    
    if selected_value == 'item1':
        header = "Help"
        body = html.Div([hlp.create_help_en()
        ])
        return True, header, body
    
    elif selected_value == 'item2':
        header = "Помощь"
        body = html.Div([hlp.create_help_ru()
        ])
        return True, header, body

    return False, "", ""

@app.callback(
    Output("error-message", "children", allow_duplicate = True),
    Output("interval", "disabled"),
    Input("radios", "value"),
    Input("interval", "n_intervals"),
    prevent_initial_call = True,
)
def manage_counter(value, n_intervals):
    global stop_signal

    # Определяем, какой input вызвал колбэк
    triggered_id = callback_context.triggered[0]["prop_id"]
    if stop_signal:
        print('triggered_id: ', triggered_id)
        print('triggered_id stop_signal: ', stop_signal)

    info = get_info_message()
#    info = get_error_message()

    # Если запуск от кнопки
    if triggered_id == "radios.value":
#        if not stop_signal:
        if value == 2 and not stop_signal:
            print('Пришел сигнал СТАРТ: ', stop_signal)
            return info, False  # Активируем interval
#        return '', True  # Blocking interval

    # Если запуск от interval
#    if stop_signal and mb.info_request['count_delay'] == 0:
    if stop_signal:
        print('Пришел сигнал СТОП: ', mb.info_request['count_delay'])
#        info = get_info_message()
        return info, True  # Останавливаем interval
    
    if stop_signal:
        print('Здесь должен быть вывод на экран mb.info_request:', mb.info_request)
#    info = get_info_message()
    
    return info, False 
#    return info, True 

if __name__ == '__main__':
#    app.run_server(debug = False) # Для отладки
    app.run_server(debug = False, host = '0.0.0.0')
#    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
