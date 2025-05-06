import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import pandas as pd
import numpy as np
import json
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tf_keras.preprocessing.text import Tokenizer
from tf_keras.preprocessing.sequence import pad_sequences
from tf_keras.backend import clear_session
from tf_keras.callbacks import EarlyStopping
import joblib
from services.model import CustomLoss
from services.model import create_model # Importamos desde archivo externo
from tf_keras.models import load_model
from functools import partial

early_stopping = EarlyStopping(
    monitor='val_loss',      # Monitor validation loss
    patience=5,              # Stop after 5 epochs with no improvement
    restore_best_weights=True  # Restore weights from the best epoch
)

piece_map = {
    0: 0,  # Vacío
    'I': 1,  # Pieza I
    'L': 2,  # Pieza L
    'J': 3,  # Pieza J
    'O': 4,  # Pieza O
    'S': 5,  # Pieza S
    'Z': 6,  # Pieza Z
    'T': 7   # Pieza T
}

def piece_to_int(piece):
    # Puedes hacer un mapeo de piezas específicas a enteros, por ejemplo:
    return piece_map.get(piece, -1)

def process_board(board):
    # Asegúrate de que `board` es una lista de listas, que representa el tablero
    return np.array([[piece_to_int(piece) for piece in row] for row in json.loads(board)])

def extract_board_features(board_matrix):
    board = np.array(board_matrix)
    height = board.shape[0]
    width = board.shape[1]

    col_heights = []
    holes = 0

    for col in range(width):
        column = board[:, col]
        blocks = np.where(column != 0)[0]
        if len(blocks) == 0:
            col_heights.append(0)
        else:
            first_block = blocks[0]
            col_heights.append(height - first_block)
            holes += np.sum(column[first_block:] == 0)

    max_height = max(col_heights)
    avg_height = np.mean(col_heights)
    bumpiness = sum(abs(col_heights[i] - col_heights[i+1]) for i in range(len(col_heights)-1))

    return np.array([max_height, avg_height, holes, bumpiness])


def load_data():
    conn = sqlite3.connect("tetris.db")
    df = pd.read_sql_query("SELECT * FROM games", conn)
    conn.close()

    print(df['moves'])
    print(df.head())
    print(df.describe())

    print(df.dtypes)

    # Convertir el board a numpy array
    df['board_matrix'] = df['init_board'].apply(lambda x: process_board(x))
    df['board_flat'] = df['board_matrix'].apply(lambda mat: mat.flatten())
    df['board_features'] = df['board_matrix'].apply(lambda mat: extract_board_features(mat))
    df['end_matrix'] = df['end_board'].apply(lambda x: process_board(x))
    df['end_flat'] = df['end_matrix'].apply(lambda mat: mat.flatten())

    # Codificar piezas
    le_piece = LabelEncoder()

    all_pieces = (
        list(df['currentPiece']) +
        list(df['holdPiece'].fillna('none')) +
        df['nextPieces'].apply(lambda x: json.loads(x)[0]).tolist() +
        ['none']
    )
    le_piece.fit(all_pieces)
    df['current_piece_encoded'] = le_piece.transform(df['currentPiece'])
    df['hold_piece_encoded'] = le_piece.transform(df['holdPiece'].fillna('none'))
    df['next_piece_encoded'] = le_piece.transform(df['nextPieces'].apply(lambda x: json.loads(x)[0]))

    df['hold_used'] = df['hold_used'].astype(int)

    # Preparar X
    df['current_piece_encoded'] = df['current_piece_encoded'].astype(int)
    df['next_piece_encoded'] = df['next_piece_encoded'].astype(int)
    df['hold_piece_encoded'] = df['hold_piece_encoded'].astype(int)
    df['hold_used'] = df['hold_used'].astype(int)


    X_board = np.stack(df['board_flat'].values)
    X_piece = df[['current_piece_encoded', 'next_piece_encoded', 'hold_piece_encoded', 'hold_used']].values
    X_features = np.stack(df['board_features'].values)

    X = np.hstack([X_board, X_piece, X_features])
    print("x shape: ", X.shape)
    print("Im trying, X converted")

    # Secuencias de movimientos
    df['move_sequence'] = df['moves'].apply(lambda x: json.loads(x))

    tokenizer = Tokenizer(char_level=False, lower=False)
    tokenizer.word_index['PAD'] = 0
    tokenizer.index_word[0] = 'PAD'
    tokenizer.fit_on_texts(df['move_sequence'])

    sequences = tokenizer.texts_to_sequences(df['move_sequence'])
    max_seq_len = max(len(seq) for seq in sequences)
    y = pad_sequences(sequences, maxlen=max_seq_len, padding='post')
    y = np.expand_dims(y, -1)  # (samples, seq_len, 1)

    return X, y, max_seq_len, tokenizer, le_piece


def main():
    X, y, max_seq_len, tokenizer, le_piece = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model_path = "models/tetris_AI.h5"

    custom_loss_with_classes = partial(CustomLoss, num_classes=6)
        

    if os.path.exists(model_path):
        print("Cargando modelo existente...")
        model = load_model("models/tetris_AI.h5", custom_objects={"CustomLoss": custom_loss_with_classes})
    else:
        print("Creando un nuevo modelo...")
    model = create_model(X.shape[1], output_dim=len(tokenizer.word_index) + 1, max_seq_len=max_seq_len)


    print("X_train.type:", X_train.dtype)  # Debería ser float o int
    print("y_train.type:", y_train.dtype) 

    history = model.fit(X_train, y_train, epochs=50, batch_size=48, validation_split=0.1, callbacks=[early_stopping])

    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=-1)
    y_test_classes = np.argmax(y_test, axis=-1)

    # Guardar las predicciones y los valores reales
    np.save('models/y_test.npy', y_test_classes)
    np.save('models/y_pred.npy', y_pred_classes)

    print("Tokenizer vocab size:", len(tokenizer.word_index))  # How many words?
    print("Tokenizer index to word map:", tokenizer.index_word)
    print("Max class index (y_train):", np.max(y_train))
    print("y_train.shape:", y_train.shape)
    print("Unique classes in y_train:", np.unique(y_train))
    #print(np.unique(y_train))

    model.evaluate(X_test, y_test)

    model.save("models/tetris_AI.h5")
    joblib.dump(tokenizer, "models/tokenizer.pkl")
    joblib.dump(le_piece, "models/label_encoder.pkl")
    joblib.dump(history.history, "models/train_history.pkl")


if __name__ == '__main__':
    #clear_session()
    main()