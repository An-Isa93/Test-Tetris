import sqlite3
import json
from datetime import datetime
def create_table():
    conn = sqlite3.connect("tetris.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             init_board TEXT,
             end_board TEXT,
             currentPiece TEXT,
             nextPieces TEXT, 
             holdPiece TEXT,
             moves TEXT, 
             score INT,
             elapsed_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             hold_used BINARY DEFAULT 0,
             game_ended BINARY               
                   
                   )
    """)
    conn.commit()
    conn.close
#create_table()

def save_game(init_board,end_board, currentPiece, nextPieces, holdPiece, moves, score,hold_used, game_ended):
    conn=sqlite3.connect("tetris.db")
    cursor = conn.cursor()
    initGrid = json.dumps(init_board)
    endGrid = json.dumps(end_board)
    next_piece_json = json.dumps(nextPieces)
    moves_json= json.dumps(moves)
    #current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
   

    cursor.execute("""
    INSERT INTO games(init_board, end_board, currentPiece, nextPieces, holdPiece, moves, score,elapsed_time,hold_used, game_ended)
    VALUES(?,?,?,?,?,?,?,?,?,?)              
    """,
    (
        initGrid,
        endGrid,
        currentPiece,
        next_piece_json,
        holdPiece,
        moves_json,
        score, 
        current_time,
        hold_used,       
        game_ended 
    ))
    conn.commit()
    conn.close() 

def get_all_games():
    conn = sqlite3.connect("tetris.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM games")

    # get all results
    games = cursor.fetchall()

    games_dict = []
    for game in games:
        games_dict.append({
            'id': game[0],
            'init_board': json.loads(game[1]), 
            'end_board': json.loads(game[2]),
            'currentPiece': game[3],
            'nextPieces': json.loads(game[4]),
            'holdPiece': game[5],
            'moves': json.loads(game[6]),
            'score': game[7],
            'elapsed_time': game[8],
            'hold_used': game[9],
            'game_ended': game[10]
        })

    conn.close()
    return games_dict
games = get_all_games()

for game in games:
    print(f"ID: {game['id']}")
    print(f"Initial Board: {game['init_board']}")
    print(f"End Board: {game['end_board']}")
    print(f"Current Piece: {game['currentPiece']}")
    print(f"Next Pieces: {game['nextPieces']}")
    print(f"Hold Piece: {game['holdPiece']}")
    print(f"Moves: {game['moves']}")
    print(f"Score: {game['score']}")
    print(f"Elapsed Time: {game['elapsed_time']}")
    print(f"Hold Used: {game['hold_used']}")
    print(f"Game Ended: {game['game_ended']}")
    print("---")