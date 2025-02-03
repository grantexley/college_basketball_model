


files = [
    "2016-2017_data.csv",
    "2017-2018_data.csv",
    "2018-2019_data.csv",
    "2019-2020_data.csv",
    "2020-2021_data.csv",
    "2021-2022_data.csv",
    "2022-2023_data.csv",
    "2023-2024_data.csv",
    "2024-2025_data.csv"
]


with open("all_data.csv", "a") as f:
    
    for file in files:
        
        with open(file, "r") as f1:
            
            for line in f1.readlines()[1:]:
                
                print(line.strip(), file=f)
    
    
    
    