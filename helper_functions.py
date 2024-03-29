import tensorflow as tf

# This funcion import an image and resize it to be able to be used with the model that we are going to use

def load_and_prep_image(filename, img_shape=224, scale = True):
    """
    Reads in an image from filename, turns it into a tensor and reshapes into
    (224,224,3).

    Parameters
    ----------
    filename (str): string filename of target image
    img_shape (int): size to resize target image to, default 224
    scale (bool): whether to scale pixel values to range(0,1), default True
    """
    # Read in the image
    img = tf.io.read_file(filename)
    # Decode it into a tensor
    img = tf.image.decode_jpeg(img)
    # Resize the image
    img = tf.image.resize(img, [img_shape, img_shape])
    if scale:
      return img/255.0
    else:
      return img

# Plot a confusion matrix
import itertools
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix

def make_confusion_matrix(y_true, y_pred, classes=None, figsize=(10,10), text_size=15, norm=False, savefig=False):
  """
  Makes a labelled confusion matrix to compare predictions and ground truth labels.

  Parameters
  ----------
  y_true: Array of truth labels (must be same shape as y_pred).
  y_pred: Array of predicted labels (must be same shape as y_true).
  classes: Array of class labels. If 'None', integer labels are gonna be used.
  figsize: Size of output figure, defalult (10, 10).
  text_size: Size of output figure, default=15.
  norm: normalize values or not, default=False.
  savefig: save confusion matrix to file, default=False.
  
  Returns
  -------
  A labelled confusion matrix plot comparing y_true and y_pred.
  
  """
  # Create the confusion matrix
  cm = confusion_matrix(y_true, y_pred)
  cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
  n_classes = cm.shape[0]

  # Plot the figure
  fig, ax = plt.subplots(figsize=figsize)
  cax = ax.matshop(cm, cmap=plt.cm.Blues)
  fig.colorbar(cax)

  # If we have the clases
  if classes:
    labels = classes
  else:
    labels = np.arange(cm.shape[0])

  # Lable the axes
  ax.set(title="Confusion Matrix",
         xlabel="Predicted label",
         ylabel="True lable",
         xticks= np.arange(n_classes),
         yticks= np.arange(n_classes),
         xticklabels=labels,
         yticklabels=labels)
  
  # Make x-axis labels appear on bottom
  ax.xaxis.set_label_postion("bottom")
  ax.xaxis.tick_bottom()

  # Set the threshold for different colors
  threshold = (cm.max() + cm.min()) / 2.0

  # Plot the text on each cell
  for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    if norm:
      plt.text(j, i, f"{cm[i, j]} ({cm_norm[i, j]*100:.1f}%)",
              horizontalalignment="center",
              color="white" if cm[i, j] > threshold else "black",
              size=text_size)
    else:
      plt.text(j, i, f"{cm[i, j]}",
              horizontalalignment="center",
              color="white" if cm[i, j] > threshold else "black",
              size=text_size)
      
    # Save the figure to the current working directory
    if savefig:
      fig.savefig("confusion_matrix.png")

# Function to predict on images and plot them
def pred_and_plot(model, filename, class_names):
  """
  Imports an Image located at filename, makes a prediction on it with
  a trained model and plots the image with the predicted class as the title.
  """
  # Import the target image and preprocess it
  img = load_and_prep_image(filename)

  # Make a prediction
  pred = model.predict(tf.expand_dims(img, axis=0))

  # Get the predicted class
  if len(pred[0]) > 1:
    pred_class = class_names[pred.argmax()]
  else:
    pred_class = class_names[int(tf.rounf(pred)[0][0])]
  
  # Plot the image and predicted class
  plt.imshow(img)
  plt.title(f"Prediction: {pred_class}")
  plt.axis(False);

# Function to create a tensorboard callback
import datetime

def create_tensorboard_callback(dir_name, experiment_name):
  """
  Creates a TensorBoard callback instand to store log files.

  Stores log files with the filepath:
    "dir_name/experiment_name/current_datatime/"
  
  Parameters
  ----------
  dir_name: target directory to store TensorBoard log files
  experiment_name: name of experiment directory
  """

  log_dir = dir_name + "/" + experiment_name + "/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
  tensorboard_callback = tf.keras.callbacks.TensorBoard(
      log_dir=log_dir
  )
  print(f"Saving TensorBoard log files to: {log_dir}")
  return tensorboard_callback

# Plot the validation an training data separately
import matplotlib.pyplot as plt

def plot_loss_curves(history):
  """
  Returns separate loss curves for training and validation metrics.

  Parameters
  ----------
  history: Tensorflow model History object
  """
  loss = history.history['loss']
  val_loss = history.history['val_loss']

  accuracy = history.history['accuracy']
  val_accuracy = history.history['val_accuracy']

  epochs = range(len(history.history['loss']))

  # Plot loss
  plt.plot(epochs, loss, label='training_loss')
  plt.plot(epochs, val_loss, label='val_loss')
  plt.title('Loss')
  plt.xlabel('Epochs')
  plt.legend()

  # Plot accuracy
  plt.figure()
  plt.plot(epochs, accuracy, label='training_accuracy')
  plt.plot(epochs, val_accuracy, label='val_accuracy')
  plt.title('Accuracy')
  plt.xlabel('Epochs')
  plt.legend();

# Function to compare histories
def compare_historys(original_history, new_history, initial_epochs=5):
  """
  Compares two TensorFlow model History objects.

  Parameters
  ----------
    orginal_history: History object from original model (before new_history)
    new_history: History object from continued model training (after original_history)
    initial_epochs: Number of epochs in original_history (new_history plot starts from here)
  """

  # Get original history measurements
  acc = original_history.history['accuracy']
  loss = original_history.history['loss']

  val_acc = original_history.history['val_accuracy']
  val_loss = original_history.history['val_loss']

  # Combine original history with new history
  total_acc = acc + new_history.history["accuracy"]
  total_loss = loss + new_history.history["loss"]

  total_val_acc = val_acc + new_history.history["val_accuracy"]
  total_val_loss = val_loss + new_history.history["val_loss"]

  # Make plots
  plt.figure(figsize=(8, 8))
  plt.subplot(2, 1, 1)
  plt.plot(total_acc, label='Training Accuracy')
  plt.plot(total_val_acc, label='Validation Accuracy')
  plt.plot([initial_epochs-1, initial_epochs-1],
           plt.ylim(), label='Start Fine Tuning')
  plt.legend(loc='lower right')
  plt.title('Training and Validation Accuracy')

  plt.subplot(2, 1, 2)
  plt.plot(total_loss, label='Training Loss')
  plt.plot(total_val_loss, label='Validation Loss')
  plt.plot([initial_epochs-1, initial_epochs-1],
           plt.ylim(), label='Start Fine Tuning')
  plt.legend(loc='upper right')
  plt.title('Training and Validation Loss')
  plt.xlabel('epoch')
  plt.show()

# Function to unzip a zipfile into current working directory
import zipfile

def unzip_data(filename):
  """
  Unzips filename into the current working directory.

  Parameters
  ----------
    filename: a filepath to a target zip folder to be unzipped.
  """
  zip_ref = zipfile.ZipFile(filename, "r")
  zip_ref.extractall()
  zip_ref.close()

# Walk through an image classificacion directory and find out how many files (images)
# are in each subdirectory.
import os

def walk_through_dir(dir_path):
  """
  Walkd through dir_path returning its contents.

  Parameters
  ----------
    dir_path: target directory

  Returns
  -------
    A print out of:
      number of subdirectories in dir_path
      number of images in each subdirectory
      name of each subdirectory
  """
  for dirpath, dirnames, filenames in os.walk(dir_path):
    print(f"There are {len(dirnames)} directories and {len(filenames)} images in '{dir_path}'.")

# Function to evaluate: accuracy, precision, recall, f1-score
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def calculate_results(y_true, y_pred):
  """
  Calculates model accuracy, precision, recall and f1 score of a binary classification model.

  Parameters
  ----------
    y_true: true labels in the form of a 1D array
    y_pred: predicted labels in the form of a 1D array

  Returns
  -------
  A dictionary of accuracy, precision, recall, f1-score.
  """

  # Calculate model accuracy
  model_accuracy = accuracy_score(y_true, y_pred) * 100
  # Calculate model precision, recall and f1 score using "weighted average"
  model_precision, model_recall, model_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted")
  model_results = {"accuracy": model_accuracy,
                   "precision": model_precision,
                   "recall": model_recall,
                   "f1": model_f1}
  return model_results
