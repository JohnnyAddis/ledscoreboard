from data import grab_game
from nba_api.live.nba.endpoints import scoreboard
from datetime import datetime
import json

game = grab_game()


str = 'incredible'

str2 = str[:2]
print(str2)

def stutter(word):
    if len(word)<2:
        return ('too short')
    
    prefix = word[:2]
    return f'{prefix}... {prefix}... word?'