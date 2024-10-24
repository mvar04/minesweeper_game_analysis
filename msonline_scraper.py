from bs4 import BeautifulSoup
import requests, re, json

def parse_game(game):
    page = requests.get(f'https://minesweeper.online/game/{str(game)}').content
    parsed = BeautifulSoup(page, 'html.parser')
    return parsed
def find_difficulty(parsed):
    difficulty = None
    if parsed.find(id = 'level_select_1'):
        #Level is in Standard mode
        if 'active' in parsed.find(id = 'level_select_1')['class']: difficulty = 'Beginner'
        elif 'active' in parsed.find(id = 'level_select_2')['class']: difficulty = 'Intermediate'
        elif 'active' in parsed.find(id = 'level_select_3')['class']: difficulty = 'Expert'
        else: difficulty = 'Custom'

    elif parsed.find(id = 'level_select_11'):
        #Level is in No Guessing Mode
        if 'active' in parsed.find(id = 'level_select_11')['class']: difficulty = 'NG_Easy'
        elif 'active' in parsed.find(id = 'level_select_12')['class']: difficulty = 'NG_Medium'
        elif 'active' in parsed.find(id = 'level_select_13')['class']: difficulty = 'NG_Hard'
        elif 'active' in parsed.find(id = 'level_select_14')['class']: difficulty = 'NG_Evil'
        else: difficulty = 'NG_Custom'

    return difficulty
def find_board_size(parsed, difficulty):
    size = {
        'Beginner': (9, 9), 
        'Intermediate': (16, 16), 
        'Expert': (30, 16),
        'NG_Easy': (9, 9),
        'NG_Medium': (16, 16),
        'NG_Hard': (30, 16),
        'NG_Evil': (30, 20)
    }

    if difficulty in ('Custom', 'NG_Custom'): 
        board_size = (int(parsed.find(id = 'custom_width')['value']), int(parsed.find(id = 'custom_height')['value']))
    else: 
        board_size = size[difficulty]

    return board_size
def find_player_stats(player, difficulty):
    diff_converter = {
        'Beginner:': 'Beginner',
        'Intermediate:': 'Intermediate',
        'Expert:': 'Expert',
        'Custom:': 'Custom',
        'Easy NG:': 'NG_Easy',
        'Medium NG:': 'NG_Medium',
        'Hard NG:': 'NG_Hard',
        'Evil NG:': 'NG_Evil',
        'Custom NG:': 'NG_Custom',
    }

    player_page = requests.get(f'https://minesweeper.online/player/{player}').content
    player_parsed = BeautifulSoup(player_page, 'html.parser')
    best_times = player_parsed.find(id = 'player_positions').find_all(class_ = 'form-group-player-info')

    best_time = -1
    completions = 0

    for i in best_times:
        if diff_converter.get(i.contents[0].text, '') == difficulty:
            try: best_time = float(i.contents[1].text)
            except: best_time = -1

            completions = int(i.contents[2].text)
            break
    
    return (best_time, completions)
def create_board(parsed, board_size):
    conv = {'hd_type0': '0', 'hd_type1': '1', 'hd_type2': '2', 'hd_type3': '3', 'hd_type4': '4', 'hd_type5': '5', 'hd_type6': '6', 'hd_type7': '7', 'hd_type8': '8', 'hd_type9': '-', 'hd_type10': 'B', 'hd_type11': 'b', 'hd_flag': 'F', 'hd_closed' : '?', 'hd_type12': 'f'}

    board = [[0 for _ in range(board_size[0])] for _ in range(board_size[1])]
    elements = parsed.find_all(id = re.compile('cell_\\d+_\\d+'))
    for i in elements:
        board[int(i['data-y'])][int(i['data-x'])] = conv[i['class'][-1]]
    
    return ''.join([''.join(i) for i in board])
def find_game_stats(stats, completed):
    Time, _3BV, _3BV_Total, Clicks, Efficiency = 0, 0, 0, 0, 0
    if stats[0] == 'Arena: ': stats = stats[3:]
    if stats[0] == 'Original: ': return (Time, _3BV, _3BV_Total, Clicks, Efficiency)
    c = len(stats)
    Time = float(stats[1])

    if c == 10: # 3BV = 0 with no wasted clicks
        _3BV, _3BV_Total = [int(i) for i in stats[5][1:].split('/')]
        Clicks = int(stats[8])

    elif c == 11: # 3BV = 0 with wasted clicks
        _3BV, _3BV_Total = [int(i) for i in stats[5][1:].split('/')]
        Clicks = int(stats[-2][1:]) + int(stats[-3])

    elif c == 18: # [3BV = 1 / Completion] with no wasted clicks
        Efficiency = int(stats[-2][:-1])
        Clicks = int(stats[-6])
        if completed: _3BV, _3BV_Total = int(stats[5][1:]), int(stats[5][1:])
        else: _3BV, _3BV_Total = [int(i) for i in stats[5][1:].split('/')]

    elif c == 19: # [3BV = 1 / Completion] with wasted clicks
        Efficiency = int(stats[-2][:-1])
        Clicks = int(stats[-6][1:]) + int(stats[-7])

        if completed: _3BV, _3BV_Total = int(stats[5][1:]), int(stats[5][1:])
        else: _3BV, _3BV_Total = [int(i) for i in stats[5][1:].split('/')]

    elif c == 20: # 3BV > 1 with no wasted clicks
        Efficiency = int(stats[-2][:-1])
        Clicks = int(stats[-6])

        if completed: _3BV, _3BV_Total = int(stats[7][1:]), int(stats[7][1:])
        else: _3BV, _3BV_Total = [int(i) for i in stats[7][1:].split('/')]

    elif c == 21: # 3BV > 1 with wasted clicks
        Time = float(stats[1])
        Efficiency = int(stats[-2][:-1])
        Clicks = int(stats[-6][1:]) + int(stats[-7])

        if completed: _3BV, _3BV_Total = int(stats[7][1:]), int(stats[7][1:])
        else: _3BV, _3BV_Total = [int(i) for i in stats[7][1:].split('/')]

    else:
        print('     ', c, game, stats)
    
    return (Time, _3BV, _3BV_Total, Clicks, Efficiency)

if __name__ == '__main__':    
    game = 3000000000
    count = 0
    while game < 3000000000 + 1000000:
        for attempt in range(2):
            try:
                parsed = parse_game(game)

                details = [i for i in parsed.find(id = 'ResultBlock').children]
                player = int(details[1]['href'][8:])
                stats = [i.text for i in details[5].contents]

                difficulty = find_difficulty(parsed)
                board_size = find_board_size(parsed, difficulty)
                best_time, completions = find_player_stats(player, difficulty)
                completed = True if parsed.find(id = 'top_area_face')['class'][-1] == 'hd_top-area-face-win' else False
                board = create_board(parsed, board_size)

                time, _3bv, _3bv_total, clicks, efficiency = find_game_stats(stats, completed)
                if time == 0: break

                info = {
                    'Game': game,
                    'Difficulty': difficulty,
                    'Board_Size': board_size,
                    'Board': board,
                    'PlayerID': player,
                    'Best_Time': best_time,
                    'Completions': completions,
                    'Completed': completed,
                    'Time': time,
                    '3BV': _3bv,
                    '3BV_Total': _3bv_total,
                    'Clicks': clicks,
                    'Efficiency': efficiency
                }
                
                if difficulty != 'Intermediate':
                    game += 5
                    break

                if completed:
                    with open('data.json', 'a', encoding='utf-8') as f:
                        f.write(', ')
                        json.dump(info, f, ensure_ascii = False, indent = 4)
                    count += 1
                    print(game, count)
                
                game += 1
                break
            except TypeError as e: 
                print(e)
                print(f'{game} Failed to retrieve data, attempt {attempt + 1}')
                continue
            
            except AttributeError as f: 
                print(f)
                print(f'{game} Failed to retrieve data, attempt {attempt + 1}')
                continue

            except KeyError as g:
                print(g)
                print(f'{game} Failed to retrieve data, attempt {attempt + 1}')
                continue

            except Exception as h:
                print(f"Unexpected error for game {game}", h)
            
        game += 5       