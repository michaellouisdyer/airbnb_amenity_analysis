import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from local_amenities import PropertyAnalyzer
from dash.dependencies import Input, Output, State
import plotly.figure_factory as ff
import plotly.plotly as py
import plotly.graph_objs as go
import jsonpickle
from utils import return_markdown



prp = None
property_name  = '#### Results:'
app = dash.Dash()
figure = ff.create_table(pd.DataFrame(columns=['Amenities', 'Coeff']))
figure1 = ff.create_table(pd.DataFrame(columns=['Words', 'Coeff']))
app.layout = html.Div(children=[
    html.Div(
        [
            dcc.Markdown(
                """
                ## Should I Buy a Hot Tub?
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
    html.Div([dcc.Markdown(id='loading_text')]),html.Div([dcc.Markdown(property_name, id='property_name')]),
    html.Div([dcc.Graph(id='amenity_table', figure=figure)], id='my_div', style=dict(textAlign="center", marginBottom="15px")),
    html.Div([dcc.Graph(id='nlp_table', figure=figure1)], id='my_div2', style=dict(textAlign="center", marginBottom="15px"))
])
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


@app.callback(
    Output('amenity_table', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State(component_id='airbnb_url', component_property='value')]
)
def update_output_div(n_clicks, url):
    global prp
    prp = PropertyAnalyzer(url, verbose=True, num_comps=30)
    prp.get_comps()
    amenities = prp.best_amenities()
    amenities = amenities.reset_index()
    amenities.columns = ['Amenity', 'Revenue Potential ($)']
    amenities = amenities[amenities['Revenue Potential ($)'] > 0]
    amenities.Amenity = amenities.Amenity.str.title().str.replace('_', ' ')
    amenities['Revenue Potential ($)'] = amenities['Revenue Potential ($)'].astype('float').round(1)
    table = ff.create_table(amenities.head(10))
    return table

@app.callback(
    Output(component_id='loading_text', component_property='children'),
    [Input('submit-button', 'n_clicks')],
    [State('amenity_table', 'figure')]

)
def update_loading(n_clicks, figure):
    if n_clicks == 0:
        return("## Press submit to analyze!")
    else:
        return ("## Analyzing the top amenities for your listing... ")

@app.callback(
    Output(component_id='property_name', component_property='children'),
    [ Input('amenity_table', 'figure')]
)
def update_name(figure):
    # if n_clicks == 0:
    #     return("## Press submit to analyze!")
    # if:
    import pdb; pdb.set_trace()
    return ("## " + prp.my_property['title'])

@app.callback(
    Output('nlp_table', 'figure'),
    [ Input('amenity_table', 'figure')]
    )
def update_output(figure):
    coeffs = prp.do_NLP()
    coeffs = coeffs.reset_index()
    coeffs.columns = ['Words', 'Coefficient']
    coeffs['Coefficient'] = coeffs['Coefficient'].astype('float').round(1)
    table = ff.create_table(coeffs.sort_values(by='Coefficient', ascending =  False))
    return table


if __name__ == '__main__':
    app.run_server(debug=True)
