from msonline_scraper import *
import sys
import numpy as np
from tensorflow import convert_to_tensor
import keras
from keras import layers as l

game = int(sys.argv[1])
parsed = parse_game(game)
details = [i for i in parsed.find(id = 'ResultBlock').children]
player = int(details[1]['href'][8:])
stats = [i.text for i in details[5].contents]

difficulty = find_difficulty(parsed)
board_size = find_board_size(parsed, difficulty)
best_time, completions = find_player_stats(player, difficulty)
completed = True
board = create_board(parsed, board_size)
time, _3bv, _3bv_total, clicks, efficiency = find_game_stats(stats, completed)
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
board_copy = np.reshape([i for i in board], (16, 16))

board = np.reshape([int(j) if j not in 'bF' else 0 for j in board], (1, 16, 16))
data = np.expand_dims(np.array([best_time, completions]), axis = 0)

boardInput = l.Input(shape = (16, 16, 1, ), name = 'boardInput')
statsInput = l.Input(shape = (2, ), name = 'statsInput')
model = keras.saving.load_model('best_model.keras')

print("\n")
for i in board_copy:
    for j in i: print(j, end = ' ')
    print('')

print("Predicted: ", int(model.predict((board, data), verbose = 0)[0][0] * 1000) / 1000)
print("Actual:    ", time)

# python predict.py 3830842294