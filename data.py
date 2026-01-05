from nba_api.live.nba.endpoints import scoreboard
from datetime import datetime
import json

SCHEDULED = 1
LIVE = 2
FINAL = 3

def grab_game():
    #TODO: get rid of hardcoded games[0]
    sb = scoreboard.ScoreBoard()
    games = sb.games.get_dict()
    game = games[0]

    start_time = None
    if game["gameStatus"] == 1:
        dt = datetime.fromisoformat(game["gameEt"].replace("Z", ""))
        start_time = dt.strftime("%I:%M %p").lstrip("0")

    return {
        'homeName' : game['homeTeam']['teamTricode'], 
        'awayName' : game['awayTeam']['teamTricode'],
        'homeScore' : game['homeTeam']['score'],
        'awayScore' : game['awayTeam']['score'],
        'gameClock' :  game['gameClock'],
        'period' : game['period'],
        'status' : game['gameStatus'],
        'statusText' : game['gameStatusText'],
        'startTime' : start_time
    }

#GAME STATUSES:
#1: scheduled
#2: live
#3: final
def derive_state(game):
    status = game.get('status')
    statusText = (game.get('statusText') or '').lower()
    clock = game.get('gameClock')
    period = game.get('period')

    
    if status == 3:
        return 'FINAL'

    if 'half' in statusText:
        return 'HALFTIME'

    if status == 2 and period and period >= 1 and clock:
        return 'LIVE'

    return 'SCHEDULED'
