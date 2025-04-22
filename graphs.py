import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import confusion_matrix
import seaborn as sns
import numpy as np

history = joblib.load("models/train_history.pkl")

plt.figure(figsize=(10, 5))
plt.plot(history['loss'], label='Training Loss')
plt.plot(history['val_loss'], label='Validation Loss')
plt.title('Model Loss During Training')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)
plt.savefig("models/loss_plot.png")
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(history['accuracy'], label='Training presition')
plt.plot(history.get('val_accuracy', []), label='Validation presition')
plt.title('Model Accuracy During Training')
plt.xlabel('Epoch')
plt.ylabel('Presition')
plt.legend()
plt.grid(True)
plt.savefig("models/accuracy_plot.png")
plt.show()

def graph_matrix(y_true, y_pred, tokenizer):
    y_pred_classes = np.argmax(y_pred, axis=-1)
    y_true_classes = np.argmax(y_true, axis=-1)

    cm = confusion_matrix(y_true_classes.flatten(), y_pred_classes.flatten())

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=tokenizer.word_index.keys(), yticklabels=tokenizer.word_index.keys())
    plt.xlabel('Predictions')
    plt.ylabel('True Values')
    plt.title('Confusion Matrix')
    plt.savefig("models/confusion_matrix.png")
    plt.show()

tokenizer = joblib.load("models/tokenizer.pkl")
y_test_classes = np.load('models/y_test.npy')
y_pred_classes = np.load('models/y_pred.npy')

graph_matrix(y_test_classes, y_pred_classes, tokenizer)
