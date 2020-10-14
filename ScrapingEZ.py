from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
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