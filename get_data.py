#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from name_mapping import name_lookup
import sys
import time

def fetch_table(begin, end):

    base_url = "https://barttorvik.com/trank.php"
        
    params = {
        "year": end[:4],
        "sort": "",
        "hteam": "",
        "t2value": "",
        "conlimit": "All",
        "state": "All",
        "begin": begin,
        "end": end,
        "top": 0,
        "revquad": 0,
        "quad": 5,
        "venue": "All",
        "type": "All",
        "mingames": 0
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if not table:
        print("Could not find 'scheduletable' in the HTML. Possibly JavaScript-driven or no data.")
        return None

    header_row = table.find("thead")
    headers = [th.get_text(strip=True) for th in header_row.find_all("th")][13:]
    headers.insert(5, "Conf Rec")

    body = table.find("tbody")
    row_data = []
    for row in body.find_all("tr"):
        if 'extraheader' in row.get('class', []): 
            continue
        
        cols = row.find_all(["td", "th"])
        parsed_cols = []

        for col in cols:
            if 'teamname' in col.get('class', []):
                team_anchor = col.find('a')
                if team_anchor:
                    for span in team_anchor.find_all('span'):
                        span.decompose()
                    text_value = team_anchor.get_text(strip=True)
                parsed_cols.append(text_value)
            elif "text-align:center;border-right:solid 1px black" == col.get('style', "no"):
                total_rec = col.find('a')
                conf_rec = col.find('span')
                parsed_cols.append(total_rec.get_text(strip=True))
                parsed_cols.append(conf_rec.get_text(strip=True))
            else:
                text_value = col.get_text(strip=True)
                parsed_cols.append(text_value)

        row_data.append(parsed_cols)

    df = pd.DataFrame(row_data, columns=headers)
    return df



def get_stats_year(year):
    
    df = pd.DataFrame()

    for month, year in [(11, year), (12, year), (1, year+1), (2, year+1), (3, year+1), (4, year+1)]:
        for day in range(1, 32):
            
            day_df = get_stats_day(year, month, day)
            if day_df is not None:
                df = pd.concat([df, day_df], ignore_index=True)
        
            print(f"\n\nfinished day {month} {day}\n\n")
    print(df)
    
    return df
    
    
def get_stats_day(year, month, day):
    
    day_df = pd.DataFrame()
    
    base_url = "https://www.sports-reference.com/cbb/boxscores/index.cgi?"

    date = f"{year:04d}{month:02d}{day:02d}"
    
    begin_date = subtract_n_days(date)
    if not begin_date: 
        return None
    
    table = fetch_table(begin_date, date)
    while table is None:
        print("issue loading stats, waiting 5 min")
        time.sleep(300)
        table = fetch_table(begin_date, date)
    
    params = {
        "month": month,
        "day": day,
        "year": year
    }

    response = requests.get(base_url, params=params)
    while response.status_code != 200:
        print("issue loading games, waiting 5 min")
        time.sleep(300)
        response = requests.get(base_url, params=params)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    games = soup.find_all("div", class_="game_summary nohover gender-m")
    
    for game in games:
        teams_table = game.find("table", class_="teams")
        team_rows = [tr for tr in teams_table.find_all("tr") if tr.find("a")]

        away_team = team_rows[0].find("a").get_text(strip=True)
        home_team = team_rows[1].find("a").get_text(strip=True)
        
        away_score = team_rows[0].find("td", class_="right").get_text(strip=True)
        home_score = team_rows[1].find("td", class_="right").get_text(strip=True)

        home_team = name_lookup.get(home_team, home_team)
        away_team = name_lookup.get(away_team, away_team)
                
        game_info = pd.DataFrame([{"date": date, "home_team": home_team, "home_score": home_score, "away_team": away_team, "away_score": away_score}])
        game_info.reset_index(drop=True)
        
        home_team_stats = table[table["Team"] == home_team].add_prefix("home_").reset_index(drop=True)
        away_team_stats = table[table["Team"] == away_team].add_prefix("away_").reset_index(drop=True)
        
        if home_team_stats.empty or away_team_stats.empty:
            continue
        
        game_df = game_info.join(home_team_stats).join(away_team_stats)
        
        if game_df.isnull().values.any():
            continue
        
        day_df = pd.concat([day_df, game_df], ignore_index=True)

    return day_df
    
def subtract_n_days(date, days=61):
    try:
        date_obj = datetime.strptime(date, '%Y%m%d')
        new_date = date_obj - timedelta(days=days)
    except:
        return None
    return new_date.strftime('%Y%m%d')
    
def main():
    year = int(sys.argv[1])
    df = get_stats_year(year)
    df.to_csv(f"data/{year}-{year+1}_data.csv", index=False, encoding="utf-8")
    
    

if __name__ == "__main__":
    main()
