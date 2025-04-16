from tf_keras.models import Sequential
from tf_keras.layers import Dense, LSTM, RepeatVector

def create_model(input_shape, output_dim, max_seq_len):
    model = Sequential([
        Dense(128, activation='relu', input_shape=(input_shape,)),
        Dense(64, activation='relu'),
        RepeatVector(max_seq_len),
        LSTM(64, return_sequences=True),
        Dense(output_dim, activation='softmax')
    ])

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model