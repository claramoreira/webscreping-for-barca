import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pprint import pprint
from bs4 import BeautifulSoup
import re


def get_teams(list_of_elements):
    teams = {
        'home_team': list_of_elements[0].text,
        'away_team': list_of_elements[1].text,
    }
    return teams


def get_score(list_of_elements):
    score_element = list_of_elements[0].text.split('\n')
    scores = {
        'home_team_score': score_element[0],
        'away_team_score': score_element[2]
    }
    return scores


def get_events(list_of_elements):
    events_list = []
    for event in list_of_elements:
        event_type = event.find_element_by_tag_name('img').get_attribute('alt')
        event_text = event.text.split('\n')
        event_time = event_text[0]
        player_1 = event_text[1]
        if len(event_text) >= 3:
            player_2 = event_text[2]
        else:
            player_2 = ''
        event_detail = {
            'time': int(re.findall(r'\d+', event_time)[0]) if len(re.findall(r'\d+', event_time)) else event_time,
            'player_1': player_1,
            'player_2': player_2,
            'event': event_type
        }
        events_list.append(event_detail)
    return events_list


def get_stats(list_of_elements):
    stats_list = []
    for stat in list_of_elements:
        stats_text = stat.text.split('\n')
        home_team_stat = stats_text[0]
        stat_name = stats_text[1]
        away_team_stat = stats_text[2]
        stats_detail = {
            'home_team_stat': home_team_stat,
            'away_team_stat': away_team_stat,
            'stat_name': stat_name
        }
        stats_list.append(stats_detail)
    return stats_list


def get_infos(list_of_elements):
    infos_list = []
    for info in list_of_elements:
        info_text = info.text.split('\n')
        info_title = info_text[0]
        info_content = info_text[1]
        info_detail = {
            'info_title': info_title,
            'info_content': info_content,
        }
        infos_list.append(info_detail)
    return infos_list


def get_all_match_information(match_url):

    CHROMEDRIVER_PATH = 'chromedriver.exe'
    WINDOW_SIZE = "1920,1080"

    # Não abrir a janela do chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                              chrome_options=chrome_options
                             )
    # driver = webdriver.Chrome('chromedriver.exe')  # Optional argument, if not specified will search path.

    driver.get(match_url)
    
    # Aceitar cookies:
    cookies = driver.find_elements_by_xpath("//button[contains(@aria-label, 'Agree to our data processing and close')]")
    if len(cookies):
        cookies[0].click()
        
    # Verificar se o jogo não foi adiado
    if not len(driver.find_elements_by_xpath("//span[contains(text(), 'Adiado')]")):
    
        # Quem está jogando:
        search = driver.find_elements_by_xpath("//of-match-score-team")
        teams = get_teams(search)

        # Placar:
        search = driver.find_elements_by_xpath("//p[contains(@class, 'match-score-scores')]")
        score = get_score(search)

        # Escalação dos times:
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        home_team = []
        for tag in soup.findAll('span', attrs={'class': re.compile('match-lineup-v2__player-name')}):
            home_team.append(tag.text)

        search_box = driver.find_elements_by_xpath("//button[contains(@title, '" + teams['away_team'] + "')]")
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        away_team = []
        for tag in soup.findAll('span', attrs={'class': re.compile('match-lineup-v2__player-name')}):
            away_team.append(tag.text)

        # Expandir a lista de eventos:
        events_expand = driver.find_elements_by_xpath("//button[contains(@class, 'match-events__toggle-button')]")
        if len(events_expand):
            events_expand[0].click()

        # Eventos:
        events_tags = driver.find_elements_by_xpath("//li[contains(@class, 'match-events__item')]")
        events = get_events(events_tags)

        # Estatísticas:
        stats_tags = driver.find_elements_by_xpath("//li[contains(@class, 'match-stats__list-item')]")
        stats = get_stats(stats_tags)

        # Informações da partida:
        general_infos = driver.find_elements_by_xpath("//li[contains(@class, 'match-info__entry')]")
        infos = get_infos(general_infos)

        """
        pprint('Teams:')
        pprint(teams)

        pprint('Score:')
        pprint(score)

        pprint('Home team:')
        pprint(home_team)

        pprint('Away team:')
        pprint(away_team)

        pprint('Events:')
        pprint(events)

        pprint('Stats:')
        pprint(stats)

        pprint('Infos:')
        pprint(infos)
        """
        
        return teams, score, home_team, away_team, events, stats, infos
    
    else:
        return ([] for i in range(7))