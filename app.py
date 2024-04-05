import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load data and preprocess
data = pd.read_csv("data.csv")
data = data[data['quantity'] != 0]

# Use a dark theme from Dash Bootstrap Components
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Prepare dropdown options for commodities
commodities = [{'label': commodity, 'value': commodity} for commodity in data['commodity'].unique()]

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Trade From London (1760 - 1830)", className="text-center text-primary, mb-4"))),
    
    dbc.Row(dbc.Col([
        html.Label("Select Commodity:", className="text-light"),
        dcc.Dropdown(id='commodity-dropdown', options=commodities, value=commodities[0]['value']),
    ], width=12)),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='trade-trends-graph'), width=6),
        dbc.Col(dcc.Graph(id='commodity-value-graph'), width=6)
    ]),
    
    html.H2("Sum Of All Trade", className="text-center text-light, mb-4"),
    
    dbc.Row(dbc.Col(dash_table.DataTable(
        id='trade-breakdown-table',
        columns=[
            {'name': 'Port', 'id': 'port'},
            {'name': 'Type', 'id': 'type'},
            {'name': 'Total Value', 'id': 'value'},
            {'name': 'Quantity', 'id': 'quantity'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={
            'color': 'white',
            'minWidth': '80px', 'width': '120px', 'maxWidth': '180px',
            'whiteSpace': 'normal'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'border': '1px solid grey'
        },
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'border': '1px solid grey'
        },
    ), width=12)),
], fluid=True)

@app.callback(
    Output('trade-trends-graph', 'figure'),
    [Input('commodity-dropdown', 'value')]
)
def update_trade_trends(selected_commodity):
    filtered_data = data[data['commodity'] == selected_commodity]

    # Creating a new column 'port_type' to concatenate 'port' and 'type' for unique line labels
    filtered_data['port_type'] = filtered_data['port'] + " (" + filtered_data['type'] + ")"

    fig = px.line(filtered_data, x='year', y='quantity', color='port_type',
                  title=f'Quantity for {selected_commodity} by Year, Port, and Type')
    fig.update_xaxes(title_text='Year')
    fig.update_yaxes(title_text='Quantity')
    return fig

@app.callback(
    Output('commodity-value-graph', 'figure'),
    [Input('commodity-dropdown', 'value')]
)
def update_commodity_price(selected_commodity):
    filtered_data = data[data['commodity'] == selected_commodity]

    unit_name = filtered_data['unit'].values[0]
    # Creating a new column 'port_type' to concatenate 'port' and 'type' for unique line labels
    filtered_data['price_per_unit'] = filtered_data['quantity'] / filtered_data['value']

    fig = px.line(filtered_data, x='year', y='price_per_unit', color='port',
                  title=f'Price per {unit_name} for {selected_commodity} by Year, and Port')
    fig.update_xaxes(title_text='Year')
    fig.update_yaxes(title_text=f'Price Per {unit_name}')
    return fig

@app.callback(
    Output('trade-breakdown-table', 'data'),
    [Input('commodity-dropdown', 'value')]
)
def update_trade_breakdown(selected_commodity):
    filtered_data = data[data['commodity'] == selected_commodity]
    
    # No need to adjust for 'destination_source' as previously, use 'port' directly
    aggregated_data = filtered_data.groupby(['port', 'type']).agg({
        'value': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    return aggregated_data.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
