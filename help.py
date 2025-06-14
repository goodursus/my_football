import dash
from dash import html

#def create_help_en():

#    return html.Div([
#        html.H4("Description of the interface", className="card-title"),
#        html.H6("Request limits", className="card-subtitle"),
#        html.P('At the moment, data requests are not subject to payment.'),
#        html.P('In connection with this, there is a limit of 100 requests per day and no more than 10 requests per minute.'),
#        html.P('Some information on already executed requests may be cached.'),
#        html.P('If there is no information in the cache and 10 requests are executed in less than 60 seconds,'),
#        html.P('for example, in 15 seconds, then a delay in loading is activated for the remaining 45 seconds.'),
#        html.P('In this case, loading fresh information may take quite a long time.'),
#        html.P('Current information on the status of requests is displayed in the top line in the left corner of the screen.'),
#        html.Video(src = '/assets/help.mp4', controls = True, style = {"width": "100%"}),  # Вставка видео
#    ])

def create_help_en(width="100%", height="100vh", fullscreen=False):
    # Добавляем параметры для контроля размеров
    iframe_style = {
        "position": "absolute",
        "top": "0",
        "left": "0",
        "width": "100%",
        "height": "100%",
        "borderRadius": "10px",
        "border": "0"
    }
    
    container_style = {
        "position": "relative",
        "width": "100%",
        "height": "100%",
        "overflow": "hidden"
    }
    
    return html.Div([
        # Адаптивный контейнер
        html.Div([
            html.Iframe(
                src     = "https://embed.app.guidde.com/playbooks/5zkb1xrtk4SJdMbNbkHpBc",
                title   = "How to use my football",
                style   = iframe_style,
                allow   = "clipboard-write",
                sandbox = "allow-popups allow-popups-to-escape-sandbox allow-scripts allow-forms allow-same-origin allow-presentation"
            )
        ], style = container_style),

        # Скрытые субтитры (оставляем как есть)
        html.P(
            '''00:00: Introducing our new feature in my football designed for both passionate fans

                00:04: and analysts This feature allows you to dive deep into team results

                00:08: and lead Dynamics ensuring. You can make data-driven decisions and have information

                00:12: at your fingertips.

                00:14: Due to the fact that free data access mode is used to obtain results.

                00:18: There are restrictions on the number of requests 100 per day, which

                00:22: is displayed in the top panel. Also with a large number of requests

                00:26: per unit of time, there is a limit of no more than 10 requests per minute, which

                00:30: leads to pauses when loading data while waiting for the end of the minute for the next requests.

                00:35: And what is also displayed in the top information panel here.

                00:39: You can get help in two languages English and Russian

                00:42: Choose a country with football competitions.

                00:46: But if you have already viewed a country before your data is in the Cache and does not

                00:50: require a new download which speeds up the output of results.

                00:53: It is recommended to always turn on this mode.

                00:56: Of course for your favourite championships.

                01:00: When you select the Cache mode, you will only see your favourite countries.

                01:05: Select a country.

                01:07: Select your favourite league, but if you want to get data on other Leagues you need

                01:11: to use the no cache mode.

                01:13: The same applies to the choice of season.

                01:16: After selecting a season you will see a league table with current results.

                01:22: Click on the line with your favourite team, and at the bottom.

                01:24: You will see a graph of how your team. Went to success by rounds.

                01:27: Green marks are victories red marks are defeats and yellow marks are

                01:32: drawers with an indication of their current place in the tournament table.

                01:36: If you've already enjoyed your team's growth curve now, you can take a closer look at

                01:40: how it happened.

                01:42: Select my goals be a little patient if the team data is in the

                01:46: Cache it won't take very long. Otherwise, the data for several

                01:50: rounds will be loaded and it may take quite a long time.

                01:53: If you still don't have enough patience, then refresh the page and repeat all the steps

                01:57: up to this point, and things will go more fun for you now since some of the information will

                02:02: already be in the Cache

                02:04: Displays detailed information on goals scored and missed penalties.

                02:08: What time of the match and when you click on the mark you can see the statistics of the event

                02:12: using the slider on the right you can set the range of information displayed

                02:17: by setting the time period of the game.

                02:20: The update button is used to set the time interval of the game.

                02:24: Change the time to the last 10 minutes of the game and click update.

                02:28: You will only see events in the specified time range.

                02:32: Use the slider to set the first 10 minutes of the game.

                02:36: The results of the first 10 minutes of the game are also displayed

                02:40: This drop-down menu is used to filter specific types of goal events during a

                02:44: match.

                02:46: By default. All goals are shown selecting this option will show goals

                02:50: without penalties.

                02:52: The triangle marks with penalties are almost invisible only clear goals

                02:56: also shown in the Green Line a scored missed goal difference

                03:02: Only penalties are displayed.

                03:04: Missed penalties

                03:06: Own goals

                03:08: Goals in extra time

                03:10: Power Play goals

                03:12: Goals while playing short-handed

                03:15: Received cards cards received an extra timer in the yellow frame.

                03:20: Substitutions substitutions made in extra timer in yellow

                03:25: Using var during a match in the reason if you click on the tag

                03:30: Jump into buy rounds mode

                03:32: If you want to compare your favorite team's results with those of your competitors, then after

                03:36: returning to the rounds mode click in the table in the row with another team.

                03:40: If there is no data on this team in the Cache there may be a delay in providing information

                03:45: as described earlier.

                03:48: Once the results of the second command appear, you can compare them visually.

                03:53: And if you decide to really figure out, what indicators your team is better by then

                03:57: select the buy goals mode.

                03:59: Now you can enjoy a detailed comparison of the indicators by which your team is

                04:03: better or unfortunately worse than the competitor.

                04:08: After your deep analysis return to round mode

                04:12: To exclude a command from analysis click the mouse in the line with this command preferably

                04:16: in a different column than the one by which he previously selected the command.

                04:21: Here you can see how many of your daily requests you have already used up.

                04:26: And here is the counter of seconds for which the delay occurs when the number of requests

                04:30: is more than 10 within one minute.

                04:33: This is where the current tour number is indicated when executing the request.

                04:38: The time of the delay itself is shown.

                04:41: You can choose another championship.

                04:44: Accordingly the League of this championship.

                04:48: And the season

                04:49: Thank you for your attention.''',
            style = {"display": "none"}
        )
    ], style = {
        "width": "100%",
        "height": "100%",
        "margin": "0",
        "padding": "0",
        "overflow": "hidden"
    })

def create_help_ru(width="100%", height="100vh", fullscreen=False):
    # Добавляем параметры для контроля размеров
    iframe_style = {
        "position": "absolute",
        "top": "0",
        "left": "0",
        "width": "100%",
        "height": "100%",
        "borderRadius": "10px",
        "border": "0"
    }
    
    container_style = {
        "position": "relative",
        "width": "100%",
        "height": "100%",
        "overflow": "hidden"
    }
    
    return html.Div([
        # Адаптивный контейнер
        html.Div([
            html.Iframe(
                src="https://embed.app.guidde.com/playbooks/bwDtTmt8erPZJaZFJsnAeu",
                title="How to use my football",
                style=iframe_style,
                allow="clipboard-write",
                sandbox="allow-popups allow-popups-to-escape-sandbox allow-scripts allow-forms allow-same-origin allow-presentation"
            )
        ], style=container_style),

        # Скрытые субтитры (оставляем как есть)
        html.P(
            '''00:00: Представляем нашу новую функцию в моей футбол разработанную,
            05:43: Спасибо за внимание.''',
            style={"display": "none"}
        )
    ], style={
        "width": "100%",
        "height": "100%",
        "margin": "0",
        "padding": "0",
        "overflow": "hidden"
    })
