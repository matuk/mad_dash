# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

df_wide = pd.pivot(df, index='Fruit', columns='City',
                   values='Amount').reset_index()

fig_wide = px.bar(df_wide,
                  x="Fruit",
                  y=['SF', 'Montreal'],
                  barmode="group",
                  category_orders={"Fruit": ["Apples", "Oranges", "Bananas"]}
                  )

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data. (long)
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    ),

    html.Div(children='''
        Dash: A web application framework for your data. (wide)
    '''),

    dcc.Graph(
        id='example-graph-wide',
        figure=fig_wide
    ),



])

if __name__ == '__main__':
    app.run_server(debug=True)
