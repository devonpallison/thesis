from pybaseball import schedule_and_record
import pandas as pd
abbreviations = ["ARI",
                 "ATL",
                 "BAL",
                 "BOS",
                 "CHW",
                 "CHC",
                 "CIN",
                 "CLE",
                 "COL",
                 "DET",
                 "HOU",
                 "KC",
                 "LAA",
                 "LAD",
                 "MIA",
                 "MIL",
                 "MIN",
                 "NYM",
                 "NYY",
                 "OAK",
                 "PHI",
                 "PIT",
                 "SD",
                 "SF",
                 "SEA",
                 "STL",
                 "TB",
                 "TEX",
                 "TOR",
                 "WSN"]

for team in abbreviations:
    print(team)
    try:
        df = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/schedules/" + team + ".pkl")
        for i in range(1, len(df) + 1):
            dfdate = df["Date"][i]
            new_date = dfdate.split(",")[1].strip().split()
            month = new_date[0]
            day = new_date[1]

            if month == "Apr":
                month_int = "04"
            elif month == "May":
                month_int = "05"
            elif month == "Jun":
                month_int = "06"
            elif month == "Jul":
                month_int = "07"
            elif month == "Aug":
                month_int = "08"
            elif month == "Sep":
                month_int = "09"
            elif month == "Oct":
                month_int = "10"
            else:
                raise Exception("Unknown month = {}".format(month))

            if len(day) == 2:
                day_int = day
            elif len(day) == 1:
                day_int = "0" + day
            else:
                raise Exception("Unknown day format = {}".format(day))

            to_write = "2017-{}-{}".format(month_int, day_int)
            df["Date"][i] = to_write
        df.to_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/data/schedules/" + team + "2.pkl")
    except ValueError:
        print("Couldn't find data " + team)
#print(data)

# import pandas as pd
# df = pd.read_pickle("/Users/devonallison/code/Monopoly/src/main/thesis/PHI.pkl")
# print(df)
