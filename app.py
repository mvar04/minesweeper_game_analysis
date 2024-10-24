import os
import numpy as np
import streamlit as st
from tensorflow import convert_to_tensor
import keras
from keras import layers as l
from msonline_scraper import *

# Streamlit App Setup
st.title("Minesweeper Game Analysis")
st.write("Every board in the website minesweeper.online is of the form minesweeper.online/game/<game_ID>. Enter the game ID of the game you would like to analyze below.")
st.write("Some ID's to test with:\n\
    3876363469\n\
    3877172414\n\
    3316010538")
# User input for game ID
game = st.number_input("Enter Game ID:", min_value=1, step=1)

# Create a button to trigger model prediction
if st.button("Analyze Game"):
    # Parse the game using your scraper
    parsed = parse_game(game)
    
    # Get details and stats
    details = [i for i in parsed.find(id='ResultBlock').children]
    player = int(details[1]['href'][8:])
    stats = [i.text for i in details[5].contents]

    # Fetch additional game info
    difficulty = find_difficulty(parsed)
    board_size = find_board_size(parsed, difficulty)
    best_time, completions = find_player_stats(player, difficulty)
    completed = True
    board = create_board(parsed, board_size)
    time, _3bv, _3bv_total, clicks, efficiency = find_game_stats(stats, completed)
    
    # Create input data for the model
    display = np.reshape([i for i in board], (16, 16))
    board = np.reshape([int(j) if j not in 'bF' else 0 for j in board], (1, 16, 16))
    data = np.expand_dims(np.array([best_time, completions]), axis=0)
    
    model = keras.saving.load_model('best_model.keras')

    st.write("Game Board:")
    st.table(display)
    
    # Make a prediction
    predicted_time = model.predict((board, data), verbose=0)[0][0]
    
    # Display predicted and actual values
    st.write("Predicted Time: ", round(predicted_time, 3))
    st.write("Actual Time:    ", time)
