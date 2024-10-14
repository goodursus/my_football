import http.client, urllib.parse
import my_lib as mb


conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': "4305558161506f5f33e4b48f1a6745d5"
    }

#conn.request("GET", "/leagues?=?=", headers=headers)
#conn.request("GET", "https://v3.football.api-sports.io/leagues?country=england&id=39&season=2022", headers=headers)
#conn.request("GET", "https://v3.football.api-sports.io/team?country=england&id=39&l&season=2022&name=Chelsea", headers=headers)
#conn.request("GET", "https://v3.football.api-sports.io/teams?country=england&league=39&season=2022&id=49", headers=headers)
#conn.request("GET", "https://v3.football.api-sports.io/standings?season=2022&team=49", headers=headers)
#conn.request("GET", "https://v3.football.api-sports.io/fixtures/rounds?league=39&season=2023&current=true", headers=headers)
#conn.request("GET", "https://v3.football.api-sports.io/fixtures?league=39&season=2022", headers=headers)
#conn.request("GET", "/fixtures/statistics?fixture=868220", headers=headers)
#conn.request("GET", "https://v3.football.api-sports.io/fixtures/players?fixture=868220", headers=headers)
#conn.request("GET", "/status", headers=headers)
#conn.request("GET", "/countries", headers=headers)
#conn.request("GET", "https://v3.football.api-sports.io/status", headers=headers)
conn.request("GET", "https://v3.football.api-sports.io/teams/statistics?league=39&team=49&season=2024", headers=headers)
res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

#file_name    = 'Statistic/leagues_current.json'
#query_params = 'leagues?current=true'
#file_name    = 'Statistic/U21/fixtures_38.json'
#query_params = 'fixtures?league=39&season=2023'
#query_params = 'fixtures/rounds?league=39&season=2023&current=true'
#query_params = 'leagues?id=39&season=2023&current=true'
#file_name    = 'Statistic/U21/statistics_967781.json'
#query_params = 'fixtures/statistics?fixture=967781' #&team=8228
#file_name    = 'Statistic/U21/statistics_players_967781.json'
#query_params = 'fixtures/players?fixture=967781' #&team=8228
#parametr = '39'
#file_name    = 'Statistic/leagues_' + parametr +'.json'
#query_params = 'teams/statistics?league=39&team=49&season=2022' #&team=8228
#query_params = 'leagues?id=' + parametr

#get("https://v3.football.api-sports.io/status")

#mb.load_json(file_name, query_params)
