import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import TetrisEngine
from services.database import get_db_size, truncate_table
tetris = TetrisEngine.Graphics()

get_db_size()
tetris.drawTitleScreen()

#truncate_table()