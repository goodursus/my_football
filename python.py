#!C:\Users\goodu\AppData\Local\Programs\Python\Python311\python.exe

import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
   'x-rapidapi-key': "4305558161506f5f33e4b48f1a6745d5"
    }

conn.request("GET", "/status", headers=headers)

res = conn.getresponse()

#if res.status == 200:
#    print("Успешный запрос")
#else:
#    print(f"Ошибка: {res.status}")

data = res.read()

print(data.decode("utf-8"))

print("Content-Type: text/html\n\n")

print("Hello world! Python works!")

