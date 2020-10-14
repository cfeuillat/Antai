
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from datetime import date
from datetime import datetime
import plotly.express as px
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import csv

#Le code est programmé pour tourner tous les jours afin de s'actualiser

#Scraping des données EasyVista
#On télécharge le csv qui servira de "base" (téléchargé depuis EasyVista le 14 Octobre à 15h30, il contient toutes les actions
#effectuées avant cette date)
actions = pd.read_csv(r"C:\Users\Polyconseil\Desktop\ANTAI\Mission Data\Les actions de mes groupes.csv",
                              sep=';', index_col = False)

#On conserve uniquement les colonnes qu'on utilisera pour le dashboard
actions = actions[["Date de création", "Priorité", "N°", "Sujet", "Titre",
                   "Description", "Groupe", "Statut", "Date d'émission", "Type d'action"]]


#Avec Selenium, on récupère les informations des 50 dernières actions effectuées, qu'on collecte dans un DataFrame

data = {}
data["Date de création"] = []
data["Priorité"] = []
data["N°"] = []
data["Sujet"] = []
data["Titre"] = []
data["Description"] = []
data["Groupe"] = []
data["Statut"] = []
data["Date d'émission"] = []
data["Type d'action"] = []

driver = webdriver.Chrome()

driver.get('https://itsm-se.antai.gouv.fr/index_prod.html')

driver.maximize_window()
driver.implicitly_wait(20)

driver.find_element_by_id("url_login").send_keys("celestine.feuillat")
driver.find_element_by_id("url_password").send_keys("Q(KN_6Opb5")
driver.find_element_by_xpath("/html/body/div[4]/form/p[7]/button").click()

driver.implicitly_wait(20)
driver.find_element_by_xpath("//*[@id='modulesContent']/menu-sidebar/div[2]/div[1]").click()

driver.implicitly_wait(20)
driver.find_element_by_xpath("//*[@id='global-menu-btn']/i").click()

driver.implicitly_wait(20)
driver.find_element_by_xpath("/html/body/div[5]/div[1]/div[1]/menu-sidebar/div[1]/div/div/div/ul/li[2]/ul/li[1]/ul/li[1]/a/div[2]").click()

driver.implicitly_wait(20)
driver.find_element_by_xpath("/html/body/div[5]/div[1]/div[2]/div[1]/grid-header/div[3]/div[1]/div[1]/a").click()

driver.implicitly_wait(20)
driver.find_element_by_xpath(
    "/html/body/div[5]/div[1]/div[2]/div[1]/grid-header/div[3]/div[1]/div[1]/ul/li[4]/a").click()

for i in range(1, 50):
    data["Date de création"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[4]".format(i)).text)
    data["Priorité"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[5]".format(i)).text)
    data["N°"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[6]".format(i)).text)
    data["Sujet"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[7]".format(i)).text)
    data["Titre"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[8]".format(i)).text)

driver.implicitly_wait(20)
driver.find_element_by_xpath("/html/body/div[5]/div[1]/div[2]/div[1]/grid-header/div[2]/div/div/a[2]/span").click()

driver.implicitly_wait(10)

time.sleep(20)

for i in range(1, 50):
    data["Description"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[9]".format(i)).text)
    data["Groupe"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[10]".format(i)).text)

driver.find_element_by_xpath("/html/body/div[5]/div[1]/div[2]/div[1]/grid-header/div[2]/div/div/a[3]/span").click()

driver.implicitly_wait(10)

time.sleep(20)

for i in range(1, 50):
    data["Statut"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[12]".format(i)).text)
    data["Date d'émission"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[15]".format(i)).text)

driver.find_element_by_xpath("/html/body/div[5]/div[1]/div[2]/div[1]/grid-header/div[2]/div/div/a[4]/span").click()

driver.implicitly_wait(10)

time.sleep(20)

for i in range(1, 50):
    data["Type d'action"].append(driver.find_element_by_xpath("//table/tbody/tr[{}]/td[18]".format(i)).text)

new_actions = pd.DataFrame.from_dict(data)

#On ajoute au dataframe de base les actions nouvelles
for i in range(new_actions.shape[0]) :
    if new_actions.iloc[i].values not in actions.values :
        actions = actions.append(new_actions.iloc[i])

#On enregistre le DataFrame actualisé en tant que nouveau csv qui servira de base la prochaine fois que le script
#sera lancé (demain)
actions.to_csv(r"C:\Users\Polyconseil\Desktop\ANTAI\Mission Data\Les actions de mes groupes.csv", sep=';', index=False)


#Support de niveau 3
#Incident résolus

# Tout d'abord, on convertit les dates en un format exploitable
actions.loc[:, "Date de création"] = pd.to_datetime(actions["Date de création"], format='%d/%m/%Y %H:%M:%S')
actions.loc[:, "Date d'émission"] = pd.to_datetime(actions["Date d'émission"], format='%d/%m/%Y %H:%M:%S')


#On trie les actions par odre de date décroissante, ainsi pour chaque ticket la première ligne correspondra à la
#dernière action effectuée sur le ticket

actions = actions.sort_values(by="Date de création", ascending=False)

# On crée un DataFrame avec le numéro des tickets clôturés, leur Date de clôture ainsi que leur sujet (Phénix, Minos..)

incidents = actions[actions["N°"].str.contains('I')]
incidents_clôturés = incidents[incidents["Statut"].isin(["Résolu", "Clôturé", "Incident lié"])]
incident_list = list(incidents_clôturés["N°"].unique())
incident_dict = {}

for i in incident_list:
    incident_dict[i] = [incidents_clôturés[incidents_clôturés["N°"] == i].iloc[0]["Date de création"]] #comme les dates sont triées, cela correspond à la date de dernière action du ticket (donc la clôture)
    if len(incident_dict[i]) == 1:
        incident_dict[i].append(incidents_clôturés[incidents_clôturés["N°"] == i].iloc[0]["Sujet"])

incidents_clôturés = pd.DataFrame.from_dict(incident_dict, orient='index', columns=["Date de clôture", "Sujet"])


# Incidents escaladés
# On créé un dataframe avec les tickets qui ont été redirigé. On regarde la date de la dernière
# action effectuée de notre part.

incidents_long = incidents[incidents["Statut"].isin(["Redirigé vers un niveau inférieur", "Redirigé", "Escaladé", "Suspendu"])]
incident_long_list = list(incidents_long["N°"].unique())
incident_long_dict = {}

for i in incident_long_list:
    incident_long_dict[i] = [incidents_long[incidents_long["N°"] == i].iloc[0]["Date de création"]]
    if len(incident_long_dict[i]) == 1:
        incident_long_dict[i].append(incidents_long[incidents_long["N°"] == i].iloc[0]["Sujet"])

incidents_escaladés = pd.DataFrame.from_dict(incident_long_dict, orient='index',
                                             columns=["Date de dernière action", "Sujet"])


#Changements correctifs
#On procède comme précedemment, cette fois avec les tickets correspondant à des demandes de changement.
changements = actions[actions["N°"].str.contains("C")]
MCO = changements[changements["Sujet"].isin(["Changement Normal", "Correction applicative"])]

#On garde uniquement les changements correctifs.
MCO = (MCO[(MCO["Description"].str.contains(
    "Correction|Corrections|Correctif|Correctifs|correction|corrections|correctif|correctifs"
))|MCO["Titre"].str.contains("Correction|Corrections|Correctif|Correctifs|correction|corrections|correctif|correctifs")])

MCO_clôturés = MCO[MCO["Statut"].isin(["Résolu", "Clôturé", "Incident lié"])]
MCO_list = list(MCO_clôturés["N°"].unique())

MCO_dict = {}
for i in MCO_list :
    MCO_dict[i] = [MCO_clôturés[MCO_clôturés["N°"] == i].iloc[0]["Date de création"]]
    if len(MCO_dict[i]) == 1 :
        MCO_dict[i].append(MCO_clôturés[MCO_clôturés["N°"] == i].iloc[0]["Sujet"])

MCO_clôture = pd.DataFrame.from_dict(MCO_dict, orient = 'index', columns = ["Date de clôture", "Sujet"])

#Demandes de services
#On procède encore pareil pour les demandes de service

demandes_de_service = actions[actions["N°"].str.contains('S')]
demandes_clôturées = demandes_de_service[demandes_de_service["Statut"] == "Clôturé"]
service_list = list(demandes_clôturées["N°"].unique())

demande_dict = {}
for i in service_list :
    demande_dict[i] = [demandes_clôturées[demandes_clôturées["N°"] == i].iloc[0]["Date de création"]]
    if len(demande_dict[i]) == 1 :
        demande_dict[i].append(demandes_clôturées[demandes_clôturées["N°"] == i].iloc[0]["Sujet"])

services_clôturés = pd.DataFrame.from_dict(demande_dict, orient = 'index', columns = ["Date de clôture", "Sujet"])

#Demandes d'études statistiques
#Pour cela on se base sur le csv correspondant aux DES effectuées par la TMA Partenaire (sur Easyvista)
#Et on procède comme précedemment
DES = actions[actions["Sujet"] == "Demande d'étude statistique"]
DES_clôturées = DES[DES["Statut"] == "Clôturé"]

DES_list = list(DES_clôturées["N°"].unique())
DES_dict = {}
for i in DES_list:
    DES_dict[i] = [DES_clôturées[DES_clôturées["N°"] == i].iloc[0]["Date de création"]]
    if len(DES_dict[i]) == 1:
        DES_dict[i].append(DES_clôturées[DES_clôturées["N°"] == i].iloc[0]["Sujet"])

DES_clôture = pd.DataFrame.from_dict(DES_dict, orient='index', columns=["Date de clôture", "Sujet"])



#Pour chaque type de ticket, on crée une fonction qui prend en argument deux dates et renvoient le nombre de tickets
#clôturés entre ces deux dates
def nb_incidents_résolus(date_1, date_2):
    date_1 = datetime.strptime(date_1, "%d/%m/%Y")
    date_2 = datetime.strptime(date_2, "%d/%m/%Y")
    return ((incidents_clôturés[
        (incidents_clôturés["Date de clôture"] > pd.Timestamp(date_1.year, date_1.month, date_1.day)) & (
                    incidents_clôturés["Date de clôture"] < pd.Timestamp(date_2.year, date_2.month, date_2.day))][
        "Sujet"]).shape[0])


def nb_incidents_redirigés_depuis_longtemps(n, date_1, date_2):
    date_1 = datetime.strptime(date_1, "%d/%m/%Y")
    date_2 = datetime.strptime(date_2, "%d/%m/%Y")
    return ((incidents_escaladés[
        (incidents_escaladés["Date de dernière action"] > pd.Timestamp(date_1.year, date_1.month,
                                                                       date_1.day) - pd.Timedelta('{} days'.format(n)))
        & (incidents_escaladés["Date de dernière action"] < pd.Timestamp(date_2.year, date_2.month,
                                                                         date_2.day) - pd.Timedelta(
            '{} days'.format(n)))
        ]

    ).shape[0])

def nb_changements(date_1, date_2):
    date_1 = datetime.strptime(date_1, "%d/%m/%Y")
    date_2 = datetime.strptime(date_2, "%d/%m/%Y")
    return ((MCO_clôture[(MCO_clôture["Date de clôture"] > pd.Timestamp(date_1.year, date_1.month, date_1.day)) & (
                MCO_clôture["Date de clôture"] < pd.Timestamp(date_2.year, date_2.month, date_2.day))]["Sujet"]).shape[
        0])

def nb_demande_de_service(date_1, date_2):
    date_1 = datetime.strptime(date_1, "%d/%m/%Y")
    date_2 = datetime.strptime(date_2, "%d/%m/%Y")
    return (services_clôturés[
        (services_clôturés["Date de clôture"] > pd.Timestamp(date_1.year, date_1.month, date_1.day)) & (
                    services_clôturés["Date de clôture"] < pd.Timestamp(date_2.year, date_2.month, date_2.day))][
        "Sujet"].shape[0])

def nb_études_statistiques(date_1, date_2) :
    date_1 = datetime.strptime(date_1, "%d/%m/%Y")
    date_2 = datetime.strptime(date_2, "%d/%m/%Y")
    return(DES_clôture[(DES_clôture["Date de clôture"] > pd.Timestamp(date_1.year, date_1.month, date_1.day)) & (
            DES_clôture["Date de clôture"] < pd.Timestamp(date_2.year,date_2.month,date_2.day)) ][
              "Sujet"].shape[0])



#Partie Dashboard
#Création graphe de visualisation

tickets_list = list(actions["N°"].unique())
tickets_dict = {}

for i in tickets_list :
    tickets_dict[i] = [actions[actions["N°"] == i]["Sujet"].iloc[0]]
    tickets_dict[i].append(actions[actions["N°"] == i]["Statut"].iloc[0])
    tickets_dict[i].append(actions[actions["N°"] == i]["Description"].iloc[0])
    tickets_dict[i].append(actions[actions["N°"] == i]["Date d'émission"].iloc[0])
    tickets_dict[i].append(actions[actions["N°"] == i]["Priorité"].iloc[0])
    if 'I' in i:
        tickets_dict[i].append('Incident')
    if 'C' in i:
        tickets_dict[i].append('Changement')
    if 'S' in i:
        tickets_dict[i].append('Demande de service')


#Création de Piechart sur tous les tickets
tickets_statut = pd.DataFrame.from_dict(tickets_dict, orient = 'index', columns = ["Sujet", "Statut", "Description", "Date d'émission", "Priorité", "Type de demande"])
fig_sujet = px.pie(tickets_statut, names='Sujet')
fig_statut = px.pie(tickets_statut, names='Statut')
fig_type = px.pie(tickets_statut, names="Type de demande")
fig_priorité = px.pie(tickets_statut, names="Priorité")


#Création de Piechart sur les tickets de la semaine dernière
ajd = pd.Timestamp.today()
tickets_semaine = tickets_statut[tickets_statut["Date d'émission"] > ajd - pd.Timedelta("7 days")]

fig_sujet_semaine = px.pie(tickets_semaine, names='Sujet')
fig_statut_semaine = px.pie(tickets_semaine, names='Statut')
fig_type_semaine = px.pie(tickets_semaine, names="Type de demande")
fig_priorité_semaine = px.pie(tickets_semaine, names="Priorité")


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