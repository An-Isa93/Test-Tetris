from tf_keras.models import Sequential
from tf_keras.layers import Dense, LSTM, Attention, RepeatVector, Input, TimeDistributed, Dropout, Bidirectional
from tf_keras.optimizers import Adam
import tensorflow as tf
import numpy as np



class CustomLoss(tf.keras.losses.Loss):
    def __init__(self,num_classes, penalty_factor=1.0, reward_factor=1.0 ,reduction=tf.keras.losses.Reduction.SUM_OVER_BATCH_SIZE, name="custom_loss"):
        super().__init__(reduction=reduction, name=name)
        self.penalty_factor = penalty_factor
        self.num_classes = num_classes 
        self.reward_factor = reward_factor

    def call(self, y_true, y_pred):
        y_true = tf.squeeze(y_true, axis=-1)
        # Pérdida base
        base_loss = tf.keras.losses.sparse_categorical_crossentropy(y_true, y_pred)

        # Aplanar y_true para obtener solo las clases (tensor 1D)
        y_true_flat = tf.reshape(y_true, [-1])  # Aplanar a 1D

        # Obtener las clases únicas en y_true (solo las clases presentes)
        class_counts = tf.math.bincount(y_true_flat, minlength=self.num_classes, maxlength=self.num_classes)

        # Calcular la distribución de clases
        class_distribution = tf.cast(class_counts, tf.float32)
        class_distribution = tf.math.divide_no_nan(class_distribution, tf.reduce_sum(class_distribution))

        # Penalización por desequilibrio en las clases
        imbalance_penalty = tf.reduce_max(class_distribution)
        penalty = imbalance_penalty * self.penalty_factor

       # Penalización por huecos (valores 0 en y_true)
        #zeros_mask = tf.cast(tf.equal(y_true, 0), tf.float32)  # 1 si es 0 (hueco), 0 en otro caso
        #num_zeros_per_row = tf.reduce_sum(zeros_mask, axis=1)  # suma de huecos por fila
        #gap_penalty = tf.reduce_mean(num_zeros_per_row) * self.penalty_factor

         # Reward por fila completa 
        is_row_full = tf.reduce_all(tf.not_equal(y_true, 0), axis=1)  
        num_full_rows = tf.reduce_sum(tf.cast(is_row_full, tf.float32))
        reward = num_full_rows * self.reward_factor

        return tf.reduce_mean(base_loss) + penalty - reward#+ gap_penalty 


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

    model.compile(loss=CustomLoss(num_classes=output_dim,reward_factor=0.5), optimizer=Optimizer, metrics=['accuracy'])
    return model