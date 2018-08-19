# Dash app that takes an airbnb url and returns amenity and natural language processing results

import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.plotly as py
from dash.dependencies import Input, Output, State

from PropertyAnalyzer import PropertyAnalyzer

property_name = '#### Property title: '
app = dash.Dash()

## Initialize tables
figure = ff.create_table(pd.DataFrame(columns=['Amenities', 'Coeff']))
figure1 = ff.create_table(pd.DataFrame(columns=['Words', 'Coeff']))

app.layout = html.Div(children=[
    html.Div(
        [
            dcc.Markdown(
                """
                ## AirBNB Amenity Analysis
                ***
                """.replace('  ', ''),
                className='eight columns offset-by-two'
            )
        ],
        className='row',
        style=dict(textAlign="center", marginBottom="15px")
    ),
    html.Div([
        dcc.Input(id='airbnb_url', placeholder="Enter an Airbnb URL:",
                  type='text', value='', autofocus=True, inputmode='url'),
        html.Button(id='submit-button', n_clicks=0, children='Submit'),
    ], style=dict(textAlign="center")),

    html.Div([dcc.Markdown(id='loading_text')]), html.Div(
        [dcc.Markdown(property_name, id='property_name')]),

    html.Div([dcc.Graph(id='amenity_table', figure=figure)], id='my_div',
             style=dict(textAlign="center", marginBottom="15px")),

    html.Div([dcc.Graph(id='nlp_table', figure=figure1)], id='my_div2',
             style=dict(textAlign="center", marginBottom="15px")),

    html.Div(id='intermediate-value', style={'display': 'none'})
])
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css' #thanks to Chris P for the stylesheet
})

# Submit buttion
@app.callback(
    Output('intermediate-value', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State(component_id='airbnb_url', component_property='value')]
)
def update_output_div(n_clicks, url):
    """Analyzes the property and outputs results in json to an intermediate div""""
    prp = PropertyAnalyzer(url, verbose=True, num_comps=30)
    prp.get_comps()
    amenities = prp.best_amenities()
    amenities = amenities.reset_index()
    amenities.columns = ['Amenity', 'Revenue Potential ($)']
    amenities = amenities[amenities['Revenue Potential ($)'] > 0]
    amenities.Amenity = amenities.Amenity.str.title().str.replace('_', ' ')
    amenities['Revenue Potential ($)'] = amenities['Revenue Potential ($)'].astype('float').round(1)
    amenities_table = amenities.head(10)

    coeffs = prp.NLP()
    coeffs = coeffs.reset_index()
    coeffs.columns = ['Words', 'Coefficient']
    coeffs['Coefficient'] = coeffs['Coefficient'].astype('float').round(1)
    words_table = coeffs.sort_values(by='Coefficient', ascending=False)
    datasets = {'amenities': amenities_table.to_json(orient='split', date_format='iso'), 'words':  words_table.to_json(
        orient='split', date_format='iso'), 'title': prp.my_property['title']}
    return json.dumps(datasets)

#Loading text
@app.callback(
    Output(component_id='loading_text', component_property='children'),
    [Input('submit-button', 'n_clicks')],
    [State('amenity_table', 'figure')]
)
def update_loading(n_clicks, figure):
    if n_clicks == 0:
        return("## Press submit to analyze!")
    else:
        return ("## Personalized listing recommendations: ")

#Property title
@app.callback(
    Output(component_id='property_name', component_property='children'),
    [Input('intermediate-value', 'children')]
)
def update_name(dataset):
    datasets = json.loads(dataset)
    return ("#### Property Title: " + datasets['title'])

#NLP results
@app.callback(
    Output('nlp_table', 'figure'),
    [Input('intermediate-value', 'children')]
)
def update_words(dataset):
    datasets = json.loads(dataset)

    return ff.create_table(pd.read_json(datasets['words'], orient='split'))

#Amenite results
@app.callback(
    Output('amenity_table', 'figure'),
    [Input('intermediate-value', 'children')]
)
def update_amenities(dataset):
    datasets = json.loads(dataset)
    return ff.create_table(pd.read_json(datasets['amenities'], orient='split'))


if __name__ == '__main__':
    app.run_server(debug=True)
