from bs4 import BeautifulSoup
import requests
import pandas as pd

url = 'http://www.baseballpress.com/lineups/'

url += "2017-04-02"

soup = BeautifulSoup(requests.get(url).text, 'html.parser')

all_games = []
print(soup)
for g in soup.find_all(class_="player"):
    players = g.find_all('a', class_='player-link')
    print("DEVON")
    print(players)
    game = {
        'players': [_.text for _ in g.find_all('a', class_='player-link')],
    }
    print(game)
    all_games.append(game)

print(all_games)

# df = pd.DataFrame.from_dict(all_games)
# writer = pd.ExcelWriter('batting lineup.xlsx')
# df.to_excel(writer, 'baseball_sheet')
# writer.save()

