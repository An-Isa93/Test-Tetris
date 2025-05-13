import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import confusion_matrix
import seaborn as sns
import numpy as np

history = joblib.load("models/train_history.pkl")

#Model loss graph
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

#Model Accuracy graph
plt.figure(figsize=(10, 5))
plt.plot(history['accuracy'], label='Training presition')
plt.plot(history.get('val_accuracy', []), label='Validation precision')
plt.title('Model Accuracy During Training')
plt.xlabel('Epoch')
plt.ylabel('Precision')
plt.legend()
plt.grid(True)
plt.savefig("models/accuracy_plot.png")
plt.show()

#Confusion Matrix
label_names = ['R', 'L', 'r', 'd', 'D', 'C']
label_to_index = {label: i for i, label in enumerate(label_names)}
index_to_label = {i: label for label, i in label_to_index.items()}
def graph_matrix(y_true, y_pred):
    y_pred_classes = np.argmax(y_pred, axis=-1).flatten()
    y_true_classes = np.argmax(y_true, axis=-1).flatten()
    labels = list(index_to_label.keys())
    label_names = [index_to_label[i] for i in labels]
    cm = confusion_matrix(y_true_classes, y_pred_classes, labels=labels)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=label_names, yticklabels=label_names)
    plt.xlabel('Predictions')
    plt.ylabel('True Values')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig("models/confusion_matrix.png")
    plt.show()


tokenizer = joblib.load("models/tokenizer.pkl")
y_test_classes = np.load('models/y_test.npy')
y_pred_classes = np.load('models/y_pred.npy')
graph_matrix(y_test_classes, y_pred_classes)