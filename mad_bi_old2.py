# Run this app with `python3 app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import requests

app = Dash(__name__)


# Read Data from MAD2 Test Database
examinations_json = requests.get(
    url='https://api.ktm45.xyz/examinations').json()
df = pd.json_normalize(examinations_json)

fig = px.scatter(df, x='planned_examination_date',
                 y='premedication.patient_weight.value')


df_examination_types = pd.json_normalize(
    data=examinations_json, record_path='examination_types', meta=['id'])
df_examination_types.columns = ['examination_type', 'examination_id']
s = (df_examination_types.
     examination_type.
     value_counts())

fig2 = px.pie(names=s.index, values=s.values)

fig3 = px.bar(s)

app.layout = html.Div(children=[
    html.H1(children='MAD2 - Dashboard'),

    html.Div(children='''
        Reporting on MAD2 Test Data
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    ),

    dcc.Graph(
        id='example-graph-2',
        figure=fig2
    ),

    dcc.Graph(
        id='bar-chart-for-examination-types',
    ),

])

if __name__ == '__main__':
    app.run_server(debug=True)
