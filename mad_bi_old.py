from collections import Counter
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# ---------- Import and clean data (importing csv into pandas)

ex = pd.read_json("http://127.0.0.1:8000/examinations")

c = Counter()
for e in ex.examination_types:
    c.update(dict((i, e.count(i)) for i in e))

d = dict(c)


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("MAD2 Dashboards", style={'text-align': 'center'}),

    dcc.Dropdown(id="select_ex_types",
                 options=[
                     {"label": "Gastroskopie", "value": "Gastroskopie"},
                     {"label": "Kolonoskopie", "value": "Kolonoskopie"},
                     {"label": "Bravokapsel mit Gastroskopie",
                      "value": "Bravokapsel mit Gastroskopie"},
                     {"label": "Infusionstherapie", "value": "Infusionstherapie"},
                     {"label": "Rektoskopie", "value": "Rektoskopie"}],
                 multi=True,
                 value=["Gastroskopie", "Kolonoskopie",
                        "Bravokapsel mit Gastroskopie", "Infusionstherapie", "Rektoskopie"],
                 style={'width': "40%"}
                 ),
    html.Br(),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='ex_types_donut', figure={})

])

# Connect the plotly graphs with the Dash components


@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='ex_types_donut', component_property='figure')],
    [Input(component_id='select_ex_types', component_property='value')]
)
def update_ex_types_donut(ex_types_selected):
    print(ex_types_selected)
    print(type(ex_types_selected))
    print(','.join(ex_types_selected))

    container = "The examination types selected are: {}".format(
        ex_types_selected)

    data_filtered = {key: value for key,
                     value in d.items() if key in ex_types_selected}
    print(data_filtered)

    labels = list(data_filtered.keys())
    values = list(data_filtered.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

    return container, fig


    # Plotly Graph Objects (GO)
    # fig = go.Figure(
    #     data=[go.Choropleth(
    #         locationmode='USA-states',
    #         locations=dff['state_code'],
    #         z=dff["Pct of Colonies Impacted"].astype(float),
    #         colorscale='Reds',
    #     )]
    # )
    #
    # fig.update_layout(
    #     title_text="Bees Affected by Mites in the USA",
    #     title_xanchor="center",
    #     title_font=dict(size=24),
    #     title_x=0.5,
    #     geo=dict(scope='usa'),
    # )
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)


# https://youtu.be/hSPmj7mK6ng
