import dash
from dash import html

def create_help_en():

    return html.Div([
        html.H4("Description of the interface", className="card-title"),
        html.H6("Request limits", className="card-subtitle"),
        html.P('At the moment, data requests are not subject to payment.'),
        html.P('In connection with this, there is a limit of 100 requests per day and no more than 10 requests per minute.'),
        html.P('Some information on already executed requests may be cached.'),
        html.P('If there is no information in the cache and 10 requests are executed in less than 60 seconds,'),
        html.P('for example, in 15 seconds, then a delay in loading is activated for the remaining 45 seconds.'),
        html.P('In this case, loading fresh information may take quite a long time.'),
        html.P('Current information on the status of requests is displayed in the top line in the left corner of the screen.'),
        html.Video(src = '/assets/help.mp4', controls = True, style = {"width": "100%"}),  # Вставка видео
    ])

def create_help_ru():

    return html.Div([
        html.H4("Описание интерфейса", className="card-title"),
        html.H6("Ограничения по запросам", className="card-subtitle"),
        html.P('На данный момент запрос данных не является платным.'),
        html.P('В связи с этим существует ограничение в 100 запросов в день и не больше 10 запросов в минуту.'),
        html.P('Часть информации по уже выполненным запросам может быть кэширована.'),
        html.P('В случае отсутствия информации в кэше и выполнения 10 запросов за время меньше, чем 60 секунд,'),
        html.P('например, за 15 секунд, то включается задержка выполнения загрузки на оставшиеся 45 секунд.'),
        html.P('В таком случае загрузка свежей информации может занять довольно продолжительное время.'),
        html.P('Текущая информация по состоянию запросов отражается в верхней строке в левом углу экрана.'),
        html.Video(src = '/assets/help.mp4', controls = True, style = {"width": "100%"}),  # Вставка видео
    ])