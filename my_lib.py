import os
#from datetime import timedelta
from datetime import datetime
#import dash
import dash_bootstrap_components as dbc
#from dash import html, Dash, dcc, Input, Output, State
#from dash import html, Dash, dcc, Input, Output, State
import pandas as pd
from urllib.request import urlopen
import json
import http.client, urllib.parse
import requests
from folium.features import CustomIcon
#from folium import plugins
import folium
import math
#import geopandas as gpd 
import time
#import datetime
#import test_total_progress as mp
import jmespath
import sys
#import re
import pytz
import inspect
import logging
import detail_data as dd

time_request  = 0
count_request = 0
current_count = 0
range_season = {}

def setup_logger():
    logging.basicConfig(level = logging.DEBUG, 
                        filename="app.log",
                        encoding="utf-8",
                        filemode="a",
                        format  = "{asctime} - {levelname} - {message}",
                        style   = "{",
                        datefmt = "%Y-%m-%d %H:%M"
    )

def compare_date(end_season, path_file):

    # Строка даты для сравнения
    date_to_compare = end_season

    # Преобразование строки в объект datetime
    date_to_compare = datetime.strptime(date_to_compare, '%Y-%m-%d')

    # Получение даты последнего изменения файла
    file_path = path_file  # Укажите путь к файлу
    file_mod_time = os.path.getmtime(file_path)

    # Преобразование времени модификации файла в объект datetime
    file_mod_date = datetime.fromtimestamp(file_mod_time)

    return file_mod_date.date() >= date_to_compare.date()

def sleep_requests(trace = False):
    global time_request
    global count_request
    global current_count

    count_request = count_request + 1
    current_count = current_count + 1
    my_time = 0

    if count_request == 1:
#    if current_count == 1:
        time_request = time.time()
    else:
        my_time = int(time.time() - time_request)

    if trace:
        print("Время выполнения запросов:", my_time, "секунд")
#        print("Количество запросов: " + str(current_count) + "/" + str(count_request) + "раз")
        print(f"Количество запросов: {current_count}/{count_request} раз")
    if count_request % 9 == 0:    
        if my_time < 60: 
            if trace:
                print("Ожидание " + str(60 - my_time) + " секунд")
            my_pause = 60 - my_time
            for i in range(my_pause, 0, -1):
                if trace:
                    print(f'Countdown: {i} seconds', end='\r')
                time.sleep(1)
                
            time_request  = time.time()
        else:    
            time_request  = time.time()

        current_count = 0

    return my_time

def sub_call():

    caller_names = ["Вышестоящие вызывающие функции:"]
    frame = inspect.currentframe().f_back
    while frame:
        caller_names.append(frame.f_code.co_name)
        frame = frame.f_back
    
    arr_call = []
    for i, name in enumerate(caller_names):
        if i < 5:
            arr_call.append(name)

    return arr_call

def get_errors(file_name):

    with open(file_name) as my_file:
        data = json.load(my_file) 
                
    error = data["errors"]
    
#    if len(error) == 0:
#        return True, error
#    else:
    
    return error

def get_status():
    
    sleep_requests(True)

    conn = http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "4305558161506f5f33e4b48f1a6745d5"
    }

    conn.request("GET", "/" + "status", headers = headers)

    res = conn.getresponse()
    data_json = res.read()
    conn.close()    
                
    my_json = data_json.decode('utf8')

    parsed_data = json.loads(my_json)

    error = parsed_data["errors"]
    print('Request error? : ', error)
    subcall = ", ".join([f"index: {i}, value: {value}" for i, value in enumerate(sub_call())])
    logging.debug(subcall)

    if len(error) == 0:
        current = parsed_data["response"]["requests"]["current"]
        limit_day = parsed_data["response"]["requests"]["limit_day"]

        return True, current, limit_day
    else:
        return error, 0, 0

def get_error_code(query_params):

    new_string = query_params.replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_")

    with open('Statistic/Errors/error_' + new_string + '.json') as my_file:
        data = json.load(my_file) 

    if 'endpoint' in data['errors']:
        return data['errors']['endpoint']
        
    return data['errors']    

def load_json(file_name, query_params, check_zero):

    sleep_requests(True)
    subcall = ", ".join([f"index: {i}, value: {value}" for i, value in enumerate(sub_call())])
    logging.debug(subcall)

    log_mes = ''

    # Download the file from the URL
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "4305558161506f5f33e4b48f1a6745d5"
    }

    conn.request("GET", "/" + query_params, headers = headers)

    res = conn.getresponse()
    data_json = res.read()
    conn.close()    
                
    my_json      = data_json.decode('utf8')
    my_json_dict = json.loads(my_json)

    new_string = query_params.replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_")

    log_mes = f"load_json - file_name: {file_name}, query_params: {query_params}, check_zero: {check_zero}, result: {my_json_dict['results']}"
    logging.debug(log_mes)

#    if my_json_dict['results'] > 0 or not check_zero:
    if my_json_dict['results'] > 0:
        with open(file_name, 'w') as f:
            f.write(my_json)
#        print('write file')fig['layout']['shapes'][1]
        return True    
    
    elif 'rateLimit' in my_json_dict:
        print('rateLimit')
        with open('Statistic/Errors/error_'+ new_string + '.json', 'w') as f:
            f.write(my_json)
        return False
    
    elif  my_json_dict['results'] == 0 and check_zero:
        print('Look error in file: Statistic/Errors/error_'+ new_string + '.json')
        with open('Statistic/Errors/error_'+ new_string + '.json', 'w') as f:
            f.write(my_json)
        return False

def get_access(cost):
    
    access = False
    status = get_status()
    
    print('get_access.status: ' + str(status))
    if status[0]:
        if status[2] - status[1] > cost + 5:
            access = True
    else:
        access = False

    return access

def download_and_save(access, file_name, query_params, cash = True, check_zero = True, range_season = {}):

    message      = 'File downloaded.'
    file_outside = False
#    today        = datetime.datetime.now().date()
    today        = datetime.now().date()
#    status = get_status()
#    log_mes = f"download_and_save - current: {status[1]}, access: {access}, file_name: {file_name}, query_params: {query_params}, range_season: {range_season}"
    log_mes = f"download_and_save - current: status off, access: {access}, file_name: {file_name}, query_params: {query_params}, range_season: {range_season}"
    logging.debug(log_mes)

    try:
        if cash:
            # Check if the file exists
            if os.path.isfile(file_name):
                
                # проверка на вчерашнюю дату файла
                file_time = os.path.getmtime(file_name)
                file_time = int(file_time)
#                file_date = datetime.datetime.fromtimestamp(file_time).date()
                file_date = datetime.fromtimestamp(file_time).date()
 
                # Get yesterday's date and today's date
#                if query_params == 'standings?league=39&season=2023':
#                    yesterday = datetime.datetime.now().date()
#                else:    
#                    yesterday = datetime.datetime.now().date() - timedelta(days=365)

                in_range = False
                if len(range_season) == 0:
                    in_range = False
                else:    
                    data_start = datetime.strptime(range_season['start'], '%Y-%m-%d').date()                
                    data_end   = datetime.strptime(range_season['end'], '%Y-%m-%d').date() 

                    if today >= data_start and today <= data_end:
                        in_range = True
                    elif today > data_end:
                        in_range = False
                
                if access:    
                    # Check if the file date is yesterday
#                    if file_date <= yesterday:
                    if file_date < today and in_range:
                        if load_json(file_name, query_params, check_zero):  
                            message = 'File downloaded.'
                            file_outside = True
    #                        print('Ноовый поверх устаревшего File downloaded.')
                        elif not in_range:
                            error = get_error_code(query_params)
                            file_outside = True
                            return  error, 'Error isfile cash: Impossible to Download and Save File', file_outside, today
#    #                        print('Ноовый поверх устаревшего time.sleep(60)')
                    else:
                        message = 'Uploaded archive file for ' + str(file_date)
                else:
                    message = 'Attention isfile: Download limit reached. Only archive file for ' + str(file_date)  + ' date.'
            else:
                file_date = today
                if access:    
                    if load_json(file_name, query_params, check_zero):  
                        message = 'File downloaded.'
                        file_outside = True
    #                    print('Ноовый File downloaded.')
                    else:
                        error = get_error_code(query_params)
                        file_outside = True
                        return  error, 'Error no isfile cash: Impossible to Download and Save File', file_outside, today
#    ##                    print('Ноовый time.sleep(60)')
                else:
                    return  '', 'Error file_date = today: Download limit reached. Unable to Download and Save File', file_outside, today
        else:
#            file_date = datetime.datetime.now().date()
            file_date = datetime.now().date()
            if access:    
                if load_json(file_name, query_params, check_zero):  
                    message = 'File downloaded.'
                    file_outside = True
#                    print('Ноовый File downloaded.')
                else:
                    error = get_error_code(query_params)
                    file_outside = True
                    return  error, 'Error no cash: Impossible to Download and Save File', file_outside, today
##                    print('Ноовый time.sleep(60)')
            else:
                return  '', 'Error no cash: Download limit reached. Unable to Download and Save File', file_outside, today

                
        # Read the contents of the file
        with open(file_name) as my_file:
            data = json.load(my_file) # вывод как словарь dict

        return data, message, file_outside, file_date
    
    except Exception as e:
        print("Error: ", type(e).__name__)
        return  '', 'Error: Unable to Download and Save File', file_outside, today

def get_country_location(country_name):

    # Set the URL of the GeoJSON file
    url = "https://nominatim.openstreetmap.org/search?country=" + country_name + "&format=geojson&accept-language=en"

    # Make a request to the URL and convert the response to a JSON object
    response = requests.get(url)
    data = json.loads(response.text)
    location = dict()

    # Loop through the features in the JSON object
    for feature in data["features"]:
        # Check if the name property matches the country name
        if feature["properties"]["display_name"] == country_name:
            # Get the coordinates of the first geometry in the feature
            box  = feature["bbox"]
#            Lat  = feature["geometry"]["coordinates"][1]
            cord = feature["geometry"]["coordinates"]
            location = {'bbox': box, 'cord': cord}
            # Stop looping through the features
            break
    
    return location   

def set_country_marker(country_name, icon_image):
    
    location = get_country_location(country_name)
    lat = location['cord'][1]
    lon = location['cord'][0]

    country_geojson_url = "http://geojson.xyz/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
    response = requests.get(country_geojson_url)
    country_geojson = response.json()

    df = pd.DataFrame({
        "country": [country_name],
        "value": [8]
    })

    m = folium.Map(location=(30, 10), zoom_start=3, tiles="cartodb positron")

    folium.Choropleth(
        geo_data  = country_geojson,
        data      = df,
        columns=["country", "value"],
        key_on="feature.properties.name",
        bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        fill_color="OrRd",
        fill_opacity=0.4,
        line_opacity=0.1,
        nan_fill_color="white",
    ).add_to(m)

    #icon_image = 'https://media-1.api-sports.io/flags/au.svg'

    icon = CustomIcon(
        icon_image,
        icon_size=(38, 95),
    )

    marker = folium.Marker(
        location=[lat, lon], icon = icon, popup = country_name
    )
    m.add_child(marker)

#    folium.LayerControl().add_to(m)

    map_html = m._repr_html_()
    return map_html

def marker_country(country_name):
    
    m = folium.Map(location=[0, 0], zoom_start=2, width='100%', height='100%', tiles="cartodb positron")    
#   
    country_geojson_url = "http://geojson.xyz/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
    response = requests.get(country_geojson_url)
    country_geojson = response.json()

    geo_data = next((feature for feature in country_geojson['features'] if feature['properties']['name'] == country_name), None)

    #df = pd.DataFrame({
    #    "country": [country_name],
    #    "value": [8]
    #})

    my_style_function = lambda feature: {
                "fillColor": "red",
                "color": "red",
                "weight": 2,
                "dashArray": "5, 5",
    }
    layer_country = folium.GeoJson(
            geo_data,
            style_function = my_style_function,
            name = 'Layer Country',
    )
    if len(m._children) < 2:
        layer_country.add_to(m)
    else:
        m._children.get(list(m._children.keys())[1]).data =  layer_country.data   

    map_html = m.get_root().render()
    return map_html

def empty_map_html():

    # Create an empty map object
#    m = folium.Map(location=(30, 10), zoom_start=3, tiles="cartodb positron", width = 800, height = 600)    
#    m = folium.Map(location=(30, 10), zoom_start=3, tiles="cartodb positron")    
#    m = folium.Map(location=[0, 0], zoom_start=2, width=1100, height=700, tiles="cartodb positron")    
    m = folium.Map(location=[0, 0], zoom_start=2, width='100%', height='100%', tiles="cartodb positron")    
#    map_html = m._repr_html_()
    map_html = m.get_root().render()
    
    return map_html
'''
def zoom_country(country_name):
    
    country_geojson_url = "http://geojson.xyz/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
    response = requests.get(country_geojson_url)
    country_geojson = response.json()

    geo_data = next((feature for feature in country_geojson['features'] if feature['properties']['name'] == country_name), None)

    with open("geodata.geojson", "w") as outfile:
        json.dump(geo_data, outfile)

    # Read the geospatial data for the selected country
    country_data = gpd.read_file('geodata.geojson')
    
    # Calculate the bounding box of the country
    bounding_box = country_data.total_bounds

    # Calculate the width and height of the bounding box
    width = bounding_box[2] - bounding_box[0]
    height = bounding_box[3] - bounding_box[1]

    my_zoom = 2 + math.log2(160 / height)

    m = folium.Map(location=[bounding_box[1] + height / 2, bounding_box[0] + width / 2], 
                   zoom_start = my_zoom, 
                   width='100%', 
                   height='100%', 
                   tiles="cartodb positron")    

    my_style_function = lambda feature: {
                "fillColor": "red",
                "color": "red",
                "weight": 2,
                "dashArray": "5, 5",
    }
    layer_country = folium.GeoJson(
            geo_data,
            style_function = my_style_function,
            name = 'Layer Country',
    )
    
    layer_country.add_to(m)
    
    #map_html = m.get_root().render()
    return m
'''
def zoom_team(bounding_box):
    
    ## Calculate the width and height of the bounding box
    width = bounding_box[2] - bounding_box[0]
    height = bounding_box[3] - bounding_box[1]

    my_zoom = 2 + math.log2(160 / height)

    m = folium.Map(location=[bounding_box[1] + height / 2, bounding_box[0] + width / 2], 
                   zoom_start = my_zoom - 1, 
                   width='100%', 
                   height='100%', 
                   tiles="OpenStreetMap"  
                   )  
    
    folium.Marker(location=[bounding_box[1] + height / 2, bounding_box[0] + width / 2]).add_to(m)

    return m

'''
def marker_teams_map(m, x):

#    global bbox_team
    from app import bbox_team

    try:
    #        country_geojson_url = 'https://nominatim.openstreetmap.org/search?q=' + x['stud_name'] + '+' + x['city'] + '+' + x['country'] + '&format=geojson'
            country_geojson_url = 'https://nominatim.openstreetmap.org/search?q=' + x['stud_name'] + '+' + x['country'] + '&format=geojson'
            response = requests.get(country_geojson_url)
            country_geojson = response.json()
            lat = country_geojson['features'][0]['geometry']['coordinates'][1]
            lon = country_geojson['features'][0]['geometry']['coordinates'][0]

            bbox_team.append({'team_id': x['id'], 'bbox' : country_geojson['features'][0]['bbox']})

            icon_url = x['logo']

            icon = folium.CustomIcon(icon_url, icon_size=(50, 50))
        
#            folium.Marker(location=[lat, lon], icon=icon, popup=folium.Popup(x['name'], parse_html=True, show=True)).add_to(m)
            folium.Marker(location=[lat, lon], icon=icon, popup=x['name']).add_to(m)
    except:
        try:
                country_geojson_url = 'https://nominatim.openstreetmap.org/search?q=' + x['address'] + '+' + x['city'] + '+' + x['country'] + '&format=geojson'
                response = requests.get(country_geojson_url)
                country_geojson = response.json()
                lat = country_geojson['features'][0]['geometry']['coordinates'][1]
                lon = country_geojson['features'][0]['geometry']['coordinates'][0]

                bbox_team.append({'team_id': x['id'], 'bbox' : country_geojson['features'][0]['bbox']})
    
                icon_url = x['logo']

                icon = folium.CustomIcon(icon_url, icon_size=(50, 50))
            
    #            folium.Marker(location=[lat, lon], icon=icon, popup=folium.Popup(x['name'], parse_html=True, show=True)).add_to(m)
                folium.Marker(location=[lat, lon], icon=icon, popup=x['name']).add_to(m)
        except:
                print("Team: " + x['name'])     
    finally:
    #        my_counter += 1
        return [m, bbox_team]
    #return m
'''
def get_standing(league, season):

    
    data_json = download_and_save(True, 'Statistic/standing_' + league + '_' + season + '.json', 'standings?league=' + league + '&season=' + season, True, True, range_season)
#    data = data_json['response'][0]['league']['standings'][0]
    data = data_json[0]['response'][0]['league']['standings'][0]
    
#    columns     = []
    ex_columns  = []
    standing    = []
    ex_standing = []
    result      = []

    '''
    columns = [
        {'name': ["Total", 'Место'],      'id': 'rank'},
        {'name': ["Total", 'Команда'],    'id': 'name'},
        {'name': ["Total", 'Id'],         'id': 'name_Id'},
        {'name': ["Total", 'Игр'],        'id': 'played'},
        {'name': ["Total", '✌️ Побед'],   'id': 'win'},
        {'name': ["Total", 'Ничьих'],     'id': 'draw'},
        {'name': ["Total", 'Проигрышей'],  'id': 'lose'},
        {'name': ["Total", 'Забито'],     'id': 'for'},
        {'name': ["Total", 'Пропущено'],  'id': 'against'},
        {'name': ["Total", 'Разница'],    'id': 'goals'},
        {'name': ["Total", 'Очков'],      'id': 'points'},
        {'name': ["🏠 Home", 'Игр'],         'id': 'h_played'},
        {'name': ["🏠 Home", '✌️ Побед'],    'id': 'h_win'},
        {'name': ["🏠 Home", 'Ничьих'],      'id': 'h_draw'},
        {'name': ["🏠 Home", 'Проигрышей'],  'id': 'h_lose'},
        {'name': ["🏠 Home", 'Забито'],      'id': 'h_for'},
        {'name': ["🏠 Home", 'Пропущено'],   'id': 'h_against'},
        {'name': ["🏠 Home", 'Разница'],            'id': 'h_goals_dif'},
        {'name': ["🏠 Home", 'Очков'],              'id': 'h_points'},
        {'name': ["Away", 'Игр'],        'id': 'a_played'},
        {'name': ["Away", '✌️ Побед'],   'id': 'a_win'},
        {'name': ["Away", 'Ничьих'],     'id': 'a_draw'},
        {'name': ["Away", 'Проигрышей'], 'id': 'a_lose'},
        {'name': ["Away", 'Забито'],     'id': 'a_for'},
        {'name': ["Away", 'Пропущено'],  'id': 'a_against'},
        {'name': ["Away", 'Разница'],            'id': 'a_goals_dif'},
        {'name': ["Away", 'Очков'],              'id': 'a_points'},
    ]

    ex_columns = [
        {'name': ["Total", 'Место'],              'id': 'rank'},
        {'name': ["Total", 'Команда'],            'id': 'name'},
        {'name': ["Total", 'Id'],                 'id': 'name_Id'},
        {'name': ["🏠 Home", 'Игр'],         'id': 'h_played'},
        {'name': ["🏠 Home", '✌️ Побед'],    'id': 'h_win'},
        {'name': ["🏠 Home", 'Ничьих'],      'id': 'h_draw'},
        {'name': ["🏠 Home", 'Проигрышей'],  'id': 'h_lose'},
        {'name': ["🏠 Home", 'Забито'],      'id': 'h_for'},
        {'name': ["🏠 Home", 'Пропущено'],   'id': 'h_against'},
        {'name': ["Away", 'Игр'],        'id': 'a_played'},
        {'name': ["Away", '✌️ Побед'],   'id': 'a_win'},
        {'name': ["Awayх", 'Ничьих'],     'id': 'a_draw'},
        {'name': ["Away", 'Проигрышей'], 'id': 'a_lose'},
        {'name': ["Away", 'Забито'],     'id': 'a_for'},
        {'name': ["Away", 'Пропущено'],  'id': 'a_against'},
        {'name': ["", 'Разница'],            'id': 'ex_goals'},
        {'name': ["", 'Очков'],              'id': 'ex_points'},
    ]
    '''
    columns = [
        {'name': ["Total", 'Ranking'],      'id': 'rank'},
        {'name': ["Total", 'Team'],    'id': 'name'},
        {'name': ["Total", 'Id'],         'id': 'name_Id'},
        {'name': ["Total", 'Games'],        'id': 'played'},
        {'name': ["Total", '✌️ Wins'],   'id': 'win'},
        {'name': ["Total", 'Draws'],     'id': 'draw'},
        {'name': ["Total", 'Losses'],  'id': 'lose'},
        {'name': ["Total", 'Scored'],     'id': 'for'},
        {'name': ["Total", 'Conceded'],  'id': 'against'},
        {'name': ["Total", 'Difference'],    'id': 'goals'},
        {'name': ["Total", 'Points'],      'id': 'points'},
        {'name': ["🏠 Home", 'Games'],         'id': 'h_played'},
        {'name': ["🏠 Home", '✌️ Wins'],    'id': 'h_win'},
        {'name': ["🏠 Home", 'Draws'],      'id': 'h_draw'},
        {'name': ["🏠 Home", 'Losses'],  'id': 'h_lose'},
        {'name': ["🏠 Home", 'Scored'],      'id': 'h_for'},
        {'name': ["🏠 Home", 'Conceded'],   'id': 'h_against'},
        {'name': ["🏠 Home", 'Difference'],            'id': 'h_goals_dif'},
        {'name': ["🏠 Home", 'Points'],              'id': 'h_points'},
        {'name': ["Away", 'Games'],        'id': 'a_played'},
        {'name': ["Away", '✌️ Wins'],   'id': 'a_win'},
        {'name': ["Away", 'Draws'],     'id': 'a_draw'},
        {'name': ["Away", 'Losses'], 'id': 'a_lose'},
        {'name': ["Away", 'Scored'],     'id': 'a_for'},
        {'name': ["Away", 'Conceded'],  'id': 'a_against'},
        {'name': ["Away", 'Difference'],            'id': 'a_goals_dif'},
        {'name': ["Away", 'Points'],              'id': 'a_points'},
    ]

    ex_columns = [
        {'name': ["Total", 'Место'],              'id': 'rank'},
        {'name': ["Total", 'Команда'],            'id': 'name'},
        {'name': ["Total", 'Id'],                 'id': 'name_Id'},
        {'name': ["🏠 Home", 'Игр'],         'id': 'h_played'},
        {'name': ["🏠 Home", '✌️ Побед'],    'id': 'h_win'},
        {'name': ["🏠 Home", 'Ничьих'],      'id': 'h_draw'},
        {'name': ["🏠 Home", 'Проигрышей'],  'id': 'h_lose'},
        {'name': ["🏠 Home", 'Забито'],      'id': 'h_for'},
        {'name': ["🏠 Home", 'Пропущено'],   'id': 'h_against'},
        {'name': ["Away", 'Игр'],        'id': 'a_played'},
        {'name': ["Away", '✌️ Побед'],   'id': 'a_win'},
        {'name': ["Awayх", 'Ничьих'],     'id': 'a_draw'},
        {'name': ["Away", 'Проигрышей'], 'id': 'a_lose'},
        {'name': ["Away", 'Забито'],     'id': 'a_for'},
        {'name': ["Away", 'Пропущено'],  'id': 'a_against'},
        {'name': ["", 'Разница'],            'id': 'ex_goals'},
        {'name': ["", 'Очков'],              'id': 'ex_points'},
    ]

    for i in data:
        my_dict    = dict()
        my_dict["rank"]        = i['rank']
        my_dict["name"]        = i['team']['name']
        my_dict["name_id"]     = i['team']['id']
        my_dict["played"]      = i['all']['played']
        my_dict["win"]         = i['all']['win']
        my_dict["draw"]        = i['all']['draw']
        my_dict["lose"]        = i['all']['lose']
        my_dict["for"]         = i['all']['goals']['for']
        my_dict["against"]     = i['all']['goals']['against']
        my_dict["goals"]       = i['goalsDiff']
        my_dict["points"]      = i['points']
        my_dict["h_played"]    = i['home']['played']
        my_dict["h_win"]       = i['home']['win']
        my_dict["h_draw"]      = i['home']['draw']
        my_dict["h_lose"]      = i['home']['lose']
        my_dict["h_for"]       = i['home']['goals']['for']
        my_dict["h_against"]   = i['home']['goals']['against']
        my_dict["h_goals_dif"] = i['home']['goals']['for'] - i['home']['goals']['against']
        my_dict["h_points"]    = i['home']['win']*3 + i['home']['draw']
        my_dict["a_played"]    = i['away']['played']
        my_dict["a_win"]       = i['away']['win']
        my_dict["a_draw"]      = i['away']['draw']
        my_dict["a_lose"]      = i['away']['lose']
        my_dict["a_for"]       = i['away']['goals']['for']
        my_dict["a_against"]   = i['away']['goals']['against']
        my_dict["a_goals_dif"] = i['away']['goals']['for'] - i['away']['goals']['against']
        my_dict["a_points"]    = i['away']['win']*3 + i['away']['draw']
        standing.append(my_dict)

        ex_dict = dict()
        ex_dict["rank"]      = i['rank']
        ex_dict["name"]      = i['team']['name']
        ex_dict["name_id"]   = i['team']['id']
        ex_dict["h_played"]  = i['home']['played']
        ex_dict["h_win"]     = i['home']['win']
        ex_dict["h_draw"]    = i['home']['draw']
        ex_dict["h_lose"]    = i['home']['lose']
        ex_dict["h_for"]     = i['home']['goals']['for']
        ex_dict["h_against"] = i['home']['goals']['against']
        ex_dict["a_played"]  = i['away']['played']
        ex_dict["a_win"]     = i['away']['win']
        ex_dict["a_draw"]    = i['away']['draw']
        ex_dict["a_lose"]    = i['away']['lose']
        ex_dict["a_for"]     = i['away']['goals']['for']
        ex_dict["a_against"] = i['away']['goals']['against']
        ex_dict["ex_goals"]  = i['goalsDiff']
        ex_dict["ex_points"] = i['points']
        ex_standing.append(ex_dict)

#    df = pd.DataFrame(standing)
#    return df
    result.append(standing)
    result.append(ex_standing)
    result.append(columns)
    result.append(ex_columns)

    return result

def build_directory(root, league, season, rounds):

    try:
        path      = root
        new       = 'Errors/'
        full_path = os.path.join(path, new)

        if not os.path.exists(full_path):
            os.mkdir(full_path)
#            print("Каталог Errors успешно создан.")
#        else:
#            print("Каталог Errors уже существует.")

        path      = root
        new       = str(league)
        full_path = os.path.join(path, new)

        if not os.path.exists(full_path):
            os.mkdir(full_path)
#            print("Каталог " + str(league) + " успешно создан.")
#        else:
#            print("Каталог " + str(league) + " уже существует.")

        path      = root + str(league) + "/"
        new       = str(season)
        full_path = os.path.join(path, new)

        if not os.path.exists(full_path):
            os.mkdir(full_path)
#            print("Каталог " + str(season) + " успешно создан.")
#        else:
#            print("Каталог " + str(season) + " уже существует.")

        path      = root + str(league) + "/" + str(season) + "/"
        new       = "Rounds"
        full_path = os.path.join(path, new)

        if not os.path.exists(full_path):
            os.mkdir(full_path)
#            print("Каталог Games успешно создан.")
#        else:
#            print("Каталог Games уже существует.")

        path      = root + str(league) + "/" + str(season) + "/Rounds/"
#        for round in range(1, rounds + 1):        
        for round in range(1, rounds + 1):        
            new       = str(round)
            full_path = os.path.join(path, new)
            if not os.path.exists(full_path):
                os.mkdir(full_path)
#                print("Каталог " + new + " успешно создан.")
#            else:
#                print("Каталог " + new + " уже существует.")

        return True

    except OSError as e:
        return f"Ошибка при создании каталога: {e}"

def build_directory_0(root, league, season):

    try:
        path      = root
        new       = 'Errors/'
        full_path = os.path.join(path, new)

        if not os.path.exists(full_path):
            os.mkdir(full_path)
#            print("Каталог Errors успешно создан.")
#        else:
#            print("Каталог Errors уже существует.")

        path      = root
        new       = str(league)
        full_path = os.path.join(path, new)

        if not os.path.exists(full_path):
            os.mkdir(full_path)
#            print("Каталог " + str(league) + " успешно создан.")
#        else:
#            print("Каталог " + str(league) + " уже существует.")

        path      = root + str(league) + "/"
        new       = str(season)
        full_path = os.path.join(path, new)

        if not os.path.exists(full_path):
            os.mkdir(full_path)
#            print("Каталог " + str(season) + " успешно создан.")
#        else:
#            print("Каталог " + str(season) + " уже существует.")

        return True

    except OSError as e:
        return f"Ошибка при создании каталога: {e}"

def get_fixture_league(league, season):
    
    count         = 0
    cash          = True
#    current_round = 0

    while True:
#        access = get_access(1)
        access = True
        data_json = download_and_save(access, 
                                        'Statistic/' + str(league) + '/' + str(season) + '/progress_' + str(league) + '_' + str(season) + '.json', 
                                        'fixtures?league=' + str(league) + '&season=' + str(season), cash, check_zero = True, range_season = {})
        print('fixtures?league=' + str(league) + '&season=' + str(season) + ': ' + data_json[1])
        if not access:
            sys.exit()
        
        # Получаем текущее локальное время
#        local_time = datetime.datetime.now()
        local_time = datetime.now()

        # Определяем временную зону вашей локации
#        local_timezone = pytz.timezone('Australia/Sydney')  # Замените на вашу временную зону

        # Преобразуем локальное время во временную зону GMT
        gmt_time = local_time.astimezone(pytz.timezone('GMT'))

        # Форматируем время в нужном формате
        current_date = gmt_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
#        current_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ") #Время местное, а в файле - по гринвичу - коллизия
        archive_date = data_json[3]

        expression = "response[? fixture.date > `" + format(archive_date) + "` && fixture.date < `" + format(current_date) + "`].{Status: fixture.status.short, Round: league.round}"

        #result = jmespath.search(expression, data_json[0])[0]
        result_date = jmespath.search(expression, data_json[0])
        # Выводим результат
        print('result_date: ', result_date)

#        current_round = get_current_round(league, season)
#        print('current_round: ' + str(current_round))

        if not result_date:
            print('Повтор не нужен')
            break

        status = result_date[0]
        print(status)

        count += 1
        print('count: ' + str(count))

        cash = False

        if count == 2:
            break

    return data_json        

def get_rang_season(file_name, season):
    
    global range_season

    with open(file_name) as my_file:
        data = json.load(my_file) # вывод как словарь dict

    data_leagues = pd.json_normalize(data['response'][0]['seasons'],)
    range_season['year']    = data_leagues.loc[data_leagues['year'] == season, 'year'].values[0]
    range_season['start']   = data_leagues.loc[data_leagues['year'] == season, 'start'].values[0]
    range_season['end']     = data_leagues.loc[data_leagues['year'] == season, 'end'].values[0]
    range_season['current'] = data_leagues.loc[data_leagues['year'] == season, 'current'].values[0]

    range_season = range_season
    dd.range_season = range_season

    return range_season

