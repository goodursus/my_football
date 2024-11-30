from dash import Dash, dcc, html, Input, Output
import random
import os

app = Dash(__name__)

# Создаем список стран
countries = [
    'England', 'Ukraine', 'France', 'Germany', 'Italy', 
    'Spain', 'Portugal', 'Netherlands', 'Belgium', 'Sweden'
]

# Создаем структуру данных для стран и их значений
country_values = {
    'England': ['36', '37', '38', '39', '40'],
    'Ukraine': ['330', '332', '332', '333', '334', '335']
}

# Добавляем случайные значения для остальных стран
for country in countries:
    if country not in country_values:
        country_values[country] = [str(random.randint(1, 100)) for _ in range(5)]

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

# Получаем реальную структуру папок
ROOT_PATH = "Statistic"  # Укажите путь к корневой папке
folder_structure = get_folder_structure(ROOT_PATH)

app.layout = html.Div([
    html.H1("Выбор страны и значения"),
    
    # Первый dropdown для стран
    dcc.Dropdown(
        id='country-dropdown',
        placeholder="Выберите страну"
    ),
    
    # Второй dropdown для значений
    dcc.Dropdown(
        id='value-dropdown',
        placeholder="Выберите значение"
    ),
    
    # Переключатель Да-Нет
    html.Div([
        html.Label("Already exists: "),
        dcc.RadioItems(
            id='exists-radio',
            options=[
                {'label': 'Yes', 'value': 'yes'},
                {'label': 'No', 'value': 'no'}
            ],
            value='no',
            inline=True
        )
    ], style={'margin': '20px 0'})
])

# Callback для обновления списка стран
@app.callback(
    Output('country-dropdown', 'options'),
    [Input('exists-radio', 'value')]
)
def update_country_dropdown(exists):
    if exists == 'yes':
        # Показываем только существующие папки
        existing_countries = [
            {'label': country, 'value': country}
            for country in countries
            if country in folder_structure
        ]
        return existing_countries
    else:
        # Показываем все страны
        return [{'label': country, 'value': country} for country in countries]

# Callback для обновления списка значений
@app.callback(
    Output('value-dropdown', 'options'),
    [Input('country-dropdown', 'value'),
     Input('exists-radio', 'value')]
)
def update_value_dropdown(selected_country, exists):
    if not selected_country:
        return []
    
    if exists == 'yes':
        # Показываем только существующие вложенные папки
        if selected_country in folder_structure:
            existing_values = folder_structure[selected_country]
            return [{'label': value, 'value': value} 
                   for value in existing_values 
                   if value in country_values[selected_country]]
        return []
    else:
        # Показываем все возможные значения для выбранной страны
        values = country_values.get(selected_country, [])
        return [{'label': value, 'value': value} for value in values]

if __name__ == '__main__':
    app.run_server(debug=True)
