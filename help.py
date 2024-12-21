import dash
from dash import html

def create_help_en():
    image_path = '/assets/help_1.jpg'  # Replace with the actual path to your local image file

    return html.Div([
        html.P('This is the first paragraph.'),
        html.P('This is the second paragraph.'),
        html.Video(src = '/assets/help.mp4', controls = True, style = {"width": "100%"}),  # Вставка видео
#        html.Img(src = image_path, style={"width": "100%"}),
#        html.Img(src = image_path, style={'width': '500px', 'height': '500px'}),
        html.P('This is the third paragraph.')
    ])

def create_help_ru():
    image_path = '/assets/help_1.jpg'  # Replace with the actual path to your local image file

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
        html.P(''),
        html.P(''),
        html.H6("Пояснение обозначений событий на графиках", className="card-subtitle"),
        html.P(''),
        html.P(''),
        html.Img(src = image_path, style={"width": "100%"}),
#        html.Img(src = image_path, style={'width': '500px', 'height': '500px'}),
        html.P('This is the third paragraph.')
    ])