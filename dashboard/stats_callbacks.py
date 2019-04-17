from .server import app
import os
import pandas as pd
import numpy as np
import json
from dash.dependencies import Input, Output, State
from scrape_data.queries import *
from tools.stats_tools import *
import plotly.graph_objs as go
from tools.footy_tools import *
from scrape_data.queries import *
import dash_html_components as html
import dash_table


try:
    import MySQLdb
except:
    import pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb

plotConfig = {'showLink': False,
              'modeBarButtonsToRemove': ['sendDataToCloud'],
              'displaylogo': False,
              'backgroundColor': 'green'}
legendConfig = dict(orientation='h', x=0, y=1.1)

@app.callback(
    Output('indi-teams','options'),
    [Input('divisions', 'value')],
    [State('countries', 'value')]
)
def populate_teams(country, division):
    """

    :param country:
    :param division:
    :return:
    """
    if country is None: return []

    team_names = choose_team(country, division)
    teams = []

    for index, row in team_names.iterrows():
        teams.append(
        dict(label=row['home_team'], value=row['home_team'].lower()
    ))

    return teams

@app.callback(
    Output('pct_store','data'),
    [Input('win_pct_button', 'n_clicks')],
    [State('indi-teams','value'),
     State('countries','value'),
     State('overall_download', 'data')]
)
def store_pct_data(n_clicks, team_name, country, data):
    """

    :param n_clicks:
    :param team_name:
    :param country:
    :param data:
    :return:
    """
    if n_clicks == 0:
        return []

    prodConn = footy_connect()
    df = pd.read_json(data)
    df = run_win_pct(team_name, df)

    prodConn.close()

    return df.to_json()

@app.callback(
    Output('win_pct_graph','figure'),
    [Input('pct_store','data')],
    [State('indi-teams','value'),
     State('win_pct_button','n_clicks')]
)
def win_pct_graph(data, team_name, n_clicks):
    """

    :param df:
    :param n_clicks:
    :param team_name:
    :return:
    """
    if n_clicks == 0:
        return {'display':'none'}

    df = pd.read_json(data)
    df = df.sort_values(by='dateYear', ascending=True)

    traces = [go.Scatter(x=df['dateYear'], y=df['Win PCT'], name='Win %',
                         line=dict(color=footy_colors('MAASTRICHT BLUE'))),
              go.Scatter(x=df['dateYear'], y=df['Loss PCT'], name='Loss %',
                         line=dict(color=footy_colors('INDEPENDENCE'))),
              go.Scatter(x=df['dateYear'], y=df['Draw PCT'], name='Draw %',
                         line=dict(color=footy_colors('ILLUMINATING EMERALD')))]

    layout = dict(title=team_name.title() + ' (Win-Tie-Loss) %.',
                  showlegend = True,
                  xaxis=dict(tickvals=df.dateYear, ticktext=df.dateYear),
                  paper_bgcolor='#EEEEEE',
                  plot_bgcolor='#EEEEEE'
                  )

    return (dict(data=traces, layout = layout))

@app.callback(
    Output('home_win_pct_graph', 'figure'),
    [Input('pct_store','data')],
    [State('indi-teams', 'value'),
     State('win_pct_button','n_clicks')]
)
def win_home_loss_pct(data, team_name, n_clicks):
    """

    :param n_clicks:
    :param team_name:
    :return:
    """
    if n_clicks == 0:
        return []

    df = pd.read_json(data)
    df = df.sort_values(by='dateYear', ascending=True)

    traces = [go.Scatter(x=df['dateYear'], y=df['Home Win PCT'], name='Home Win %',
                        line=(dict(color=footy_colors('ILLUMINATING EMERALD')))),
              go.Scatter(x=df['dateYear'], y=df['Away Win PCT'], name='Away Win %',
                         line=dict(color=footy_colors('YANKEES BLUE')))]
    layout = dict(title=team_name.title() + ' Home-Away Win %.',
                  showlegend=True,
                    paper_bgcolor = '#EEEEEE',
                    plot_bgcolor = '#EEEEEE'
    )

    return (dict(data=traces, layout=layout))


@app.callback(
    Output('loss_win_pct_graph', 'figure'),
    [Input('pct_store','data')],
    [State('indi-teams', 'value'),
     State('win_pct_button','n_clicks')]
)
def loss_home_pct(data, team_name, n_clicks):
    """

    :param n_clicks:
    :param team_name:
    :return:
    """
    if n_clicks == 0:
        return []

    df = pd.read_json(data)
    df = df.sort_values(by='dateYear', ascending=True)

    traces = [go.Scatter(x=df['dateYear'], y=df['Home Loss PCT'], name='Home Loss %',
                         line=(dict(color=footy_colors('ILLUMINATING EMERALD')))),
              go.Scatter(x=df['dateYear'], y=df['Away Loss PCT'], name='Away Loss %',
                         line=dict(color=footy_colors('YANKEES BLUE')))]
    layout = dict(title=team_name.title() + ' Home-Away Loss %',
                  showlegend=True,
                  paper_bgcolor='#EEEEEE',
                  plot_bgcolor='#EEEEEE'
                  )

    return (dict(data=traces, layout=layout))

@app.callback(
    Output('seasonlist','options'),
    [Input('countries','value')]
)
def season_list(country):
    """

    :param data:
    :param country:
    :return:
    """

    if country is None:
        return []

    df = create_seasons_list(df = None, country =country)
    season = list(df['dateYear'].unique())
    season.sort()

    seasons = []

    for x in range(0, len(season)): seasons.append(
        dict(label=season[x], value=season[x]
    ))

    return seasons

@app.callback(
    Output('divisions', 'options'),
    [Input('countries', 'value')]
)

def division_list(country):
    """

    :param country:
    :return:
    """
    if country is None: return []

    conn = footy_connect()
    divisions = grab_divisions(conn, country)

    divs = []

    for x in range(0, len(divisions)): divs.append(
        dict(label=divisions['division'][x], value=divisions['division'][x]
    ))

    return divs

@app.callback(
    Output('table-name','children'),
    [Input('seasonlist', 'value')],
    [State('divisions', 'value')]
)
def table_name(season, division):
    """

    :param n_clicks:
    :param division:
    :param season:
    :return:
    """

    if season is None:
        return str('Please enter a League and Table Year!')
    else:
        return str(division) + " Table for the Season of " + str(season)

@app.callback(
    Output('perseason','data'),
    [Input('table-button','n_clicks'),
     Input('overall_download', 'data')],
    [State('divisions', 'value'),
     State('seasonlist', 'value')]
)
def show_league_tables(n_clicks, data, division, season):
    """

    :param n_clicks:
    :param data:
    :param division:
    :param season:
    :return:
    """
    if n_clicks == 0:
        return [{}]

    df = pd.read_json(data)

    table = table_per_season(df, division, season)

    return table.to_dict(orient='records')

@app.callback(
    Output('goals-scored', 'figure'),
    [Input('win_pct_button', 'n_clicks')],
    [State('overall_download', 'data'),
     State('indi-teams', 'value')]
)
def goal_pct(n_clicks, data, team):
    """

    :param n_clicks:
    :param data:
    :param division:
    :param team:
    :return:
    """
    if n_clicks == 0:
        return []

    df = pd.read_json(data)
    df = goal_stats(df, team)

    overall_pct = go.Bar(
        x=df['season'],
        y=df['overall_pct'],
        marker=dict(color=footy_colors('MAASTRICHT BLUE')),
        name='Overall %'
    )

    home_pct = go.Bar(
        x=df['season'],
        y=df['home_pct'],
        marker=dict(color=footy_colors('MIDNIGHT GREEN')),
        name='Home %'
    )

    away_pct = go.Bar(
        x=df['season'],
        y=df['away_pct'],
        marker=dict(color=footy_colors('ILLUMINATING EMERALD')),
        name='Away %'
    )
    data = [overall_pct, home_pct, away_pct]

    layout = dict(title= team.title() + ' Goal % (Overall-Home-Away)',
                  showlegend=True,
                  paper_bgcolor='#EEEEEE',
                  plot_bgcolor='#EEEEEE',
                  xaxis=dict(tickangle=45))

    return dict(data=data, layout=layout)

@app.callback(
    Output('shot-stats', 'figure'),
    [Input('win_pct_button', 'n_clicks')],
    [State('overall_download', 'data'),
     State('indi-teams', 'value')]
)
def shot_data(n_clicks, data, team):
    """

    :param data:
    :param division:
    :param team:
    :param n_clicks:
    :return:
    """
    if n_clicks == 0:
        return []

    df = pd.read_json(data)
    df = shot_stats(df, team)

    home_pct = go.Bar(
        x=df['season'],
        y=df['home_pct'],
        marker=dict(color=footy_colors('MAASTRICHT BLUE')),
        name='Home Shot %'
    )

    away_pct = go.Bar(
        x=df['season'],
        y=df['away_pct'],
        marker=dict(color=footy_colors('ILLUMINATING EMERALD')),
        name='Away Shot %'
    )
    data = [home_pct, away_pct]

    layout = dict(title= team.title() + ' Shots on Target % (Home-Away)',
                  showlegend=True,
                  paper_bgcolor='#EEEEEE',
                  plot_bgcolor='#EEEEEE',
                  xaxis=dict(tickangle=45))

    return dict(data=data, layout=layout)

@app.callback(
    Output('foul-stats', 'figure'),
    [Input('win_pct_button', 'n_clicks')],
    [State('overall_download', 'data'),
     State('indi-teams', 'value')]
)
def show_foul_stats(n_clicks, data, team):
    """

    :param data:
    :param division:
    :param team:
    :param n_clicks:
    :return:
    """

    if n_clicks == 0:
        return []

    df = pd.read_json(data)
    df = foul_stats(df, team)

    home_yellow = go.Bar(
        x=df['season'],
        y=df['home_yellow_pct'],
        marker=dict(color=footy_colors('MAASTRICHT BLUE')),
        name='Home Yellow PCT'
    )

    home_red = go.Bar(
        x=df['season'],
        y=df['home_red_pct'],
        marker=dict(color=footy_colors('YANKEES BLUE')),
        name='Home Red %'
    )

    away_yellow = go.Bar(
        x=df['season'],
        y=df['away_yellow_pct'],
        marker=dict(color=footy_colors('MIDNIGHT GREEN')),
        name='Away Yellow %'
    )

    away_red = go.Bar(
        x=df['season'],
        y=df['away_red_pct'],
        marker=dict(color=footy_colors('ILLUMINATING EMERALD')),
        name='Away Red %'
    )

    data = [home_yellow, home_red, away_yellow, away_red]

    layout = dict(title= team.title() + ' Yellow and Red Card % (Home-Away)',
                  showlegend=True,
                  paper_bgcolor='#EEEEEE',
                  plot_bgcolor='#EEEEEE',
                  xaxis=dict(tickangle=45))

    return dict(data=data, layout=layout)

#this is how you update by clicking on the tabs!
@app.callback(
    Output('tab-update', 'children'),
    [Input('league-tab', 'n_clicks')]
)
def league_stats(n_clicks):
    """
    This function just returns a sentence to update the tab h2 element
    pretty much an initial test to see how updating the tab works
    :param n_clicks:
    :return: string
    """
    if n_clicks == 0:
        return None

    return str("Overall League Statistics.")

@app.callback(
    Output('overall_download', 'data'),
    [Input('league-tab', 'n_clicks')]
)
def store_overall_data(n_clicks):
    """
    Loading the entire dataframe to the tab to start manipulating data
    so I don't need to keep reloading it
    :param n_clicks:
    :return: df
    """

    if n_clicks == 0:
        return []

    conn = footy_connect()

    df = grab_data(conn)
    df = create_seasons_list(df=df, country=None)
    return df.to_json()

@app.callback(
    Output('per_league_wins', 'figure'),
    [Input('overall_download', 'data'),
     Input('league-tab', 'n_clicks')]
)
def show_overall_wins(data, n_clicks):
    """

    :param data:
    :return:
    """
    if n_clicks == 0:
        return []

    df = pd.read_json(data)
    wins = home_win_per_league(df)
    wins = wins.sort_values(by = 'dateYear', ascending=True)

    bundes = wins[wins['division'] == 'Bundesliga']
    bundes = bundes[2:]
    liga = wins[wins['division'] == 'La Liga']
    liga = liga[1:]
    ligue = wins[wins['division'] == 'Ligue 1']
    prem = wins[wins['division'] == 'Premier League']
    prem = prem[6:]
    serie = wins[wins['division'] == 'Serie A']
    serie = serie[1:]

    traces = [go.Scatter(x=bundes['dateYear'], y=bundes['full_time_results'], name='Bundesliga',
                         line=(dict(color=footy_colors('MAASTRICHT BLUE')))),
              go.Scatter(x=liga['dateYear'], y=liga['full_time_results'], name='La Liga',
                         line=(dict(color=footy_colors('YANKEES BLUE')))),
              go.Scatter(x=ligue['dateYear'], y=ligue['full_time_results'], name='Ligue 1',
                         line=(dict(color=footy_colors('INDEPENDENCE')))),
              go.Scatter(x=prem['dateYear'], y=prem['full_time_results'], name='Premier League',
                         line=(dict(color=footy_colors('MIDNIGHT GREEN')))),
              go.Scatter(x=serie['dateYear'], y=serie['full_time_results'], name='Serie A',
                         line=(dict(color=footy_colors('ILLUMINATING EMERALD'))))
              ]

    layout = dict(title='Wins by Each Division per Year',
                  showlegend=True,
                  paper_bgcolor='#EEEEEE',
                  plot_bgcolor='#EEEEEE',
                  xaxis=dict(tickvals=prem.dateYear, ticktext=prem.dateYear)
                  )

    return (dict(data=traces, layout=layout))



