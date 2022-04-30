# Run this app with `python3 app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, dash_table
import plotly.express as px
import pandas as pd
import requests
import datetime as dt

app = Dash(__name__)


# Read Data from MAD2 Test Database
examinations_json = requests.get(
    url='https://api.ktm45.xyz/examinations').json()

df_examinations = pd.json_normalize(examinations_json)

# Timeline mit der Anzahl Untersuchungen
cols = ['id', 'planned_examination_date', 'examination_date']
df_projection = (df_examinations[cols]
 .astype({'planned_examination_date': 'datetime64[ns]',
       'examination_date': 'datetime64[ns]'}))

df_frequency = df_projection.groupby(df_projection.planned_examination_date.dt.to_period('M')).agg('count')[['planned_examination_date', 'examination_date']]
df_frequency.index = df_frequency.index.strftime('%Y-%m')
df_frequency.columns = ['planned examinations', 'examinations']

fig_examinations_over_time = px.bar(df_frequency, barmode='group',
    title='Geplante und durchgeführte Eingriffe pro Monat',
    labels={'value': 'Anzahl', 'planned_examination_date': '' },)

# Patienten Alter mit Verteilung

patients = requests.get(url='https://api.ktm45.xyz/patients').json()
df_patients = pd.json_normalize(patients)
dfp = (df_patients.
astype({'date_of_birth': 'datetime64'}))

def age(born):
    today = dt.date.today()
    lhs = (today.month, today.day)
    rhs = pd.Series([b for b in zip(born.dt.month, born.dt.day)])
    return today.year - born.dt.year - (lhs < rhs)

df_patients = (dfp.
assign(age=age(dfp.date_of_birth)))

fig_age_hist = px.histogram(df_patients['age'],
    title='Altersverteilung der Patienten',
    labels={'count': 'Anzahl', 'value': 'Alter [J]', })



# Balkendiagramm der Eingriffstypen
df_examination_types = pd.json_normalize(
    data=examinations_json, record_path='examination_types', meta=['id'])

df_examination_types.columns = ['examination_type', 'examination_id']
examination_counts = (df_examination_types.
     examination_type.
     value_counts())

fig_ex_types_pie = px.pie(names=examination_counts.index, values=examination_counts.values, 
    title='Eingriffstypen'
    )

fig_ex_types_bar = px.bar(examination_counts,
   title='Balkendiagramm der Eingriffstypen')



# Eingriffszeiten (Durchschnitt, Max, Min, Histogramm) 
cols_eingriffszeiten = ['id', 'anesthesia.start_anesthesia_ts', 'anesthesia.stop_anesthesia_ts', 'anesthesia.start_intervention_ts', 'anesthesia.stop_intervention_ts']
df_ex_times = df_examinations[cols_eingriffszeiten]
cols_eingriffzeiten_neu = ['id', 'start_anesthesia_ts', 'stop_anesthesia_ts', 'start_intervention_ts', 'stop_intervention_ts']
df_ex_times.columns = cols_eingriffzeiten_neu

df_ex_duration = (df_ex_times
 .query('not start_anesthesia_ts.isna() & not stop_anesthesia_ts.isna() & not start_intervention_ts.isna() & not stop_intervention_ts.isna()')
 .astype({'start_anesthesia_ts': 'datetime64'})
 .astype({'stop_anesthesia_ts': 'datetime64'})
 .astype({'start_intervention_ts': 'datetime64'})
 .astype({'stop_intervention_ts': 'datetime64'})
 .assign(duration_anesthesia = lambda x: x.stop_anesthesia_ts - x.start_anesthesia_ts)
 .pipe(lambda x: x.loc[x.duration_anesthesia > pd.Timedelta(0)])
 .pipe(lambda x: x.loc[x.duration_anesthesia < pd.Timedelta(1, 'h')])
 .assign(duration_intervention = lambda x: x.stop_intervention_ts - x.start_intervention_ts)
 .pipe(lambda x: x.loc[x.duration_intervention > pd.Timedelta(0)])
 .pipe(lambda x: x.loc[x.duration_intervention < pd.Timedelta(1, 'h')])
 .assign(dur_ana_min = lambda x: x.duration_anesthesia.dt.total_seconds()/60)
 .assign(dur_int_min = lambda x: x.duration_intervention.dt.total_seconds()/60)
)

df_stats = df_ex_duration[['dur_ana_min', 'dur_int_min']].describe().reset_index()
df_stats.columns = ['Statistik', 'Anästhesie', 'Intervention']

fig_dur_hist = px.histogram(df_ex_duration[['dur_ana_min', 'dur_int_min']] ,barmode='group')


# Top 5 Special Medication
cols = ['postmedication.special_med']
df_medis = df_examinations[cols]
df_medis.columns = ['special_med']
flattened = [item for sublist in df_medis.special_med for item in sublist]
df_top5 = pd.DataFrame(pd.value_counts(flattened).head(5)).reset_index()
df_top5.columns = ['Medikament', 'Anzahl']



# Layout

app.layout = html.Div(children=[
    html.H1(children='MAD2 - Dashboard'),

    html.Div(children='''
        MAD2 Test Daten
    '''),

    html.Div(children=
        dcc.Graph(
            id='examinations-over-time',
            figure=fig_examinations_over_time
        ),
        style={'width': '50%'}
    ),

    html.Div(children=[
        dcc.Graph(
            id='patient_age_distribution',
            figure=fig_age_hist
        ),
    ],
    style={'width': '50%'}
    ),

    html.Div(children=[
        dcc.Graph(
            id='ex-types-pie',
            figure=fig_ex_types_pie
        ),
        dcc.Graph(
            id='ex-types-bar',
            figure=fig_ex_types_bar
        ),
    ],
    style={'width': '50%'}
    ),

    html.Div(children=[
        html.H3('Anästhesie- und Eingriffsdauern'),
        dash_table.DataTable(data=df_stats.to_dict('records')),
        dcc.Graph(
            id='durations',
            figure=fig_dur_hist
        ),
    ],
    style={'width': '50%'}
    ),

    html.Div(children=[
       html.H3('Top-5 Medikamente'),
       dash_table.DataTable(data=df_top5.to_dict('records')),
    ],
    style={'width': '50%'}
    ),
    

    
])

if __name__ == '__main__':
    app.run_server(debug=True)
