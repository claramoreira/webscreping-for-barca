import time
from selenium import webdriver
from pprint import pprint
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import re
import pandas as pd
import time
from datetime import datetime
import sys

from .FinishedMatch import get_all_match_information

def get_all_team_matches(team_name):
    
    CHROMEDRIVER_PATH = 'chromedriver.exe'
    WINDOW_SIZE = "1920,1080"
    ONEFOOTBALL_URL = 'https://onefootball.com/pt-br/'
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                              chrome_options=chrome_options
                             )
    
    driver.get(ONEFOOTBALL_URL)
    
    time.sleep(2)
    
    # Aceitar cookies:
    cookies = driver.find_elements_by_xpath("//button[contains(@aria-label, 'Agree to our data processing and close')]")
    if len(cookies):
        cookies[0].click()
    
    search_box = driver.find_element_by_class_name('popup-search__input')
    search_box.send_keys(team_name)
    time.sleep(10)
    
    team_selector = driver.find_elements_by_xpath("//li[contains(@class, 'search-result-list__item')]")
    
    print('Procurando o time: ', team_name)
    
    if len(team_selector):
        print('Team found: ', team_selector[0].text)
    else:
        print('Unable to locate team!')
        sys.exit()
    
    team_selector[0].click()
    
    time.sleep(5)
    current_url = driver.current_url
    print(current_url)
    driver.get(current_url + '/resultados');
    
    mostrar_todos = driver.find_elements_by_xpath("//span[contains(text(), 'Mostrar todos os resultados')]")
    
    if len(mostrar_todos):
        mostrar_todos[0].click()
        
    time.sleep(5)
        
    all_matches = driver.find_elements_by_xpath("//li[contains(@class, 'simple-match-cards-list__match-card')]")
    print('Partidas encontradas: ', len(all_matches))
    
    all_teams, all_scores, all_home_team, all_away_team, all_events, all_stats, all_infos = ([] for i in range(7))

    for tag in all_matches:
        link = tag.find_elements_by_tag_name("a")[0].get_attribute('href')
        print(link)
        teams, score, home_team, away_team, events, stats, infos = get_all_match_information(link)
        if len(teams):
            all_teams.append(teams)
            all_scores.append(score)
            all_home_team.append(home_team)
            all_away_team.append(away_team)
            all_events.append(events)
            all_stats.append(stats)
            all_infos.append(infos)
        
    if len(all_scores):
        df = pd.DataFrame({
                   'match_date': [l[1]['info_content'] for l in all_infos],
                   'home_team': [row['home_team'] for row in all_teams],
                   'away_team': [row['away_team'] for row in all_teams],
                   'home_team_score': [row['home_team_score'] for row in all_scores],
                   'away_team_score': [row['away_team_score'] for row in all_scores],
                   'home_team_players': all_home_team,
                   'away_team_players': all_away_team,
                   'events': all_events,
                   'stats': all_stats,
                   'infos': all_infos
                  })

        file_name = team_name.replace(" ", "") + '_' + datetime.today().strftime('%Y%m%d%H%M%S') + '.csv'
        df.to_csv('datasets/' + file_name)

        return df
    
    else:
        None