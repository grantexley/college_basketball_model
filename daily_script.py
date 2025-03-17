#!/usr/bin/env python3

import pandas as pd
import os
from get_data import get_stats_day
from datetime import datetime, timedelta

def main():

    now = datetime.now() - timedelta(days=1)
    
    print(f"Running automated data updates for {now.year, now.month, now.day}")

    todays_data = get_stats_day(now.year, now.month, now.day)
    
    print(f"Today's data: {todays_data}")
    
    if todays_data is None:
        print("Could not fetch data for today.")
        return 1
    
    if len(todays_data) == 0:
        print("No data to fetch. Likely no games today.")
        return 0
    
    try:
        todays_data.to_csv("data/all_data.csv", mode='a', index=False, header=False)
        todays_data.to_csv("data/2024-2025_data.csv", mode='a', index=False, header=False)
    except Exception as e:
        print(f"Error appending data: {e}")
        return 1
    
    print("Data update Sucessful")
    return 0

if __name__ == '__main__':
    main()