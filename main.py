import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import TetrisEngine
from services.database import get_db_size, get_moves, print_sequences, count_where_length, remove_long_sequences, truncate_table
tetris = TetrisEngine.Graphics()

get_db_size()
get_moves()
# count_where_length(15)
# remove_long_sequences(15)
# get_db_size()

tetris.drawTitleScreen()

#truncate_table()