import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    # Адаптивный контейнер
    html.Div([
        html.Iframe(
            src="https://embed.app.guidde.com/playbooks/bwDtTmt8erPZJaZFJsnAeu",
            title="How to use my football",
            style={
                "position": "absolute",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "borderRadius": "10px",
                "border": "0"
            },
            allow="clipboard-write",
            sandbox="allow-popups allow-popups-to-escape-sandbox allow-scripts allow-forms allow-same-origin allow-presentation"
            # ⚠️ Dash не поддерживает allowfullscreen напрямую
        )
    ], style={
        "position": "relative",
        "paddingBottom": "56.25%",  # 16:9
        "height": "0",
        "overflow": "hidden"
    }),

    # Скрытые субтитры
    html.P(
        "00:00: Представляем нашу новую функцию в моей футбол разработанную,\n\n"
        "05:43: Спасибо за внимание.",
        style={"display": "none"}
    )
], style={"maxWidth": "800px", "margin": "0 auto", "padding": "20px"})

if __name__ == '__main__':
    app.run(debug=True)

