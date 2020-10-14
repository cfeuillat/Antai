from app import *

#Création du dashboard

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Tabs(children=[
        dcc.Tab(label="Global", children=[
            dcc.Tabs(id='global', children=[
                dcc.Tab(label='Graphe par application', children=dcc.Graph(figure=fig_sujet)),
                dcc.Tab(label='Graphe par type de demande', children=dcc.Graph(figure=fig_type)),
                dcc.Tab(label='Graphe par statut', children=dcc.Graph(figure=fig_statut)),
                dcc.Tab(label='Graphe par priorité', children=dcc.Graph(figure=fig_priorité))

            ])
        ]),
        dcc.Tab(label="Semaine", children=[
            dcc.Tabs(id='semaine', children=[
                dcc.Tab(label='Graphe par application', children=dcc.Graph(figure=fig_sujet_semaine)),
                dcc.Tab(label='Graphe par type de demande', children=dcc.Graph(figure=fig_type_semaine)),
                dcc.Tab(label='Graphe par statut', children=dcc.Graph(figure=fig_statut_semaine)),
                dcc.Tab(label='Graphe par priorité', children=dcc.Graph(figure=fig_priorité_semaine))

            ])
        ]),
        dcc.Tab(label='Facturation', children=[
            dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(1995, 8, 5),
                    max_date_allowed=date(2020, 12, 31),
                    start_date=date(2020, 10, 12),
                    end_date=date(2020, 10, 12),
                    display_format="DD/MM/YYYY"),
            dcc.Tabs(id='facturation', children=[
                dcc.Tab(label='Reporting', children=[
                    dash_table.DataTable(
                        id='table_reporting')
                ]),
                dcc.Tab(label='Demandes de services', children=[
                    dash_table.DataTable(
                        id='table_DES')

                ]),
                dcc.Tab(label='Incidents', children=[
                    dash_table.DataTable(
                        id='table_incidents')
                ]),
                dcc.Tab(label='MCO', children=[
                    dash_table.DataTable(
                        id='table_MCO')

                ])
            ])
        ])
    ])
])



@app.callback([Output('table_reporting', 'columns'), Output('table_reporting', 'data')],
                   [Input('my-date-picker-range', 'start_date'),
                    Input('my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    start_date_object = date.fromisoformat(start_date)
    date_1 = start_date_object.strftime('%d/%m/%Y')
    end_date_object = date.fromisoformat(end_date)
    date_2 = end_date_object.strftime('%d/%m/%Y')
    ar = np.array([['Incidents résolus', incidents_clôturés.shape[0], nb_incidents_résolus(date_1, date_2)],
                   ['Incidents escaladés depuis longtemps', incidents_escaladés.shape[0],
                    nb_incidents_redirigés_depuis_longtemps(5, date_1, date_2)],
                   ['MCO', MCO_clôture.shape[0], nb_changements(date_1, date_2)],
                   ['Demandes de service', services_clôturés.shape[0], nb_demande_de_service(date_1, date_2)],
                   ["Demandes d'études statistiques", DES_clôture.shape[0], nb_études_statistiques(date_1, date_2)]])
    df = pd.DataFrame(ar, columns=['Type', 'Total', 'Clôturés sur la période'])
    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')
    return columns, data


@app.callback([Output('table_DES', 'columns'), Output('table_DES', 'data')],
              [Input('my-date-picker-range', 'start_date'), Input('my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    start_date = date.fromisoformat(start_date)
    end_date = date.fromisoformat(end_date)
    services_clôturés["N°"] = services_clôturés.index
    services_datés = services_clôturés[
        (services_clôturés["Date de clôture"] > pd.Timestamp(start_date.year, start_date.month, start_date.day))
        &
        (services_clôturés["Date de clôture"] < pd.Timestamp(end_date.year, end_date.month, end_date.day))
        ]
    columns = [{"name": i, "id": i} for i in services_datés.columns]
    data = services_datés.to_dict('records')
    return columns, data


@app.callback([Output('table_incidents', 'columns'), Output('table_incidents', 'data')],
              [Input('my-date-picker-range', 'start_date'), Input('my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    start_date = date.fromisoformat(start_date)
    end_date = date.fromisoformat(end_date)
    incidents_clôturés["N°"] = incidents_clôturés.index
    incidents_datés = incidents_clôturés[
        (incidents_clôturés["Date de clôture"] > pd.Timestamp(start_date.year, start_date.month, start_date.day))
        &
        (incidents_clôturés["Date de clôture"] < pd.Timestamp(end_date.year, end_date.month, end_date.day))
        ]

    columns = [{"name": i, "id": i} for i in incidents_datés.columns]
    data = incidents_datés.to_dict('records')

    return columns, data

@app.callback([Output('table_MCO', 'columns'), Output('table_MCO', 'data')],
              [Input('my-date-picker-range', 'start_date'), Input('my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    start_date = date.fromisoformat(start_date)
    end_date = date.fromisoformat(end_date)
    MCO_clôture["N°"] = MCO_clôture.index
    MCO_datés = MCO_clôture[
        (MCO_clôture["Date de clôture"] > pd.Timestamp(start_date.year, start_date.month, start_date.day))
        &
        (MCO_clôture["Date de clôture"] < pd.Timestamp(end_date.year, end_date.month, end_date.day))
        ]

    columns = [{"name": i, "id": i} for i in MCO_datés.columns]
    data = MCO_datés.to_dict('records')

    return columns, data

if __name__ == '__main__' :
    app.run_server(debug=True)