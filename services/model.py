from tf_keras.models import Sequential
from tf_keras.layers import Dense, LSTM, Attention, RepeatVector, Input, TimeDistributed, Dropout, Bidirectional
from tf_keras.optimizers import Adam

def create_model(input_shape, output_dim, max_seq_len):
    model = Sequential([
        Input(shape=(input_shape,)),
        
        # Dense Layer
        Dense(128, activation='relu'),
        Dropout(0.3),
        
        # RepeatVector to create the sequence output
        RepeatVector(max_seq_len),
        
        # Bidirectional LSTM to capture forward and backward dependencies
        Bidirectional(LSTM(128, return_sequences=True)),
        Dropout(0.3),
        
        # Optional: Second LSTM layer for deeper sequence modeling
        LSTM(128, return_sequences=True),
        Dropout(0.3),
        
        # TimeDistributed Dense for output at each time step
        TimeDistributed(Dense(output_dim, activation='softmax'))
    ])
    
    # model = Sequential([
    #     Input(shape=(input_shape,)),
    #     Dense(128, activation='relu'),
    #     RepeatVector(max_seq_len),
    #     LSTM(128, return_sequences=True),
    #     TimeDistributed(Dense(output_dim, activation='softmax'))
    # ])
    
    # model = Sequential([
    #     Dense(128, activation='relu', input_shape=(input_shape,)),
    #     Dense(64, activation='relu'),
    #     RepeatVector(max_seq_len),
    #     LSTM(64, return_sequences=True),
    #     Dense(output_dim, activation='softmax')
    # ])
    Optimizer = Adam(learning_rate=0.001, clipvalue=1.0)

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model