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
from ScrapingEZ import actions

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


