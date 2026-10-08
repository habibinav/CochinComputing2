import os
import cv2
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

# SETTINGS
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 20  # Increased for better learning
DATA_DIR = "/Users/abhinavk/CochinComputing2/output/aadhaar"  # Only Aadhaar directory
BACKGROUND_DIR = "/path/to/random_images"  # Directory of diverse non-Aadhaar images

def load_training_data(aadhaar_dir, background_dir, img_size):
    # Load Aadhaar cards (positive class)
    aadhaar_images = []
    for img_name in os.listdir(aadhaar_dir):
        img_path = os.path.join(aadhaar_dir, img_name)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (img_size, img_size))
        aadhaar_images.append(img)
    
    # Generate synthetic negatives (more effective than random images)
    synthetic_negatives = []
    for img in aadhaar_images:
        # Create variations that break Aadhaar patterns
        synthetic_negatives.append(np.rot90(img))  # Rotated
        synthetic_negatives.append(img[::-1])  # Flipped
        synthetic_negatives.append(cv2.blur(img, (10,10)))  # Blurred
    
    X = np.array(aadhaar_images + synthetic_negatives)
    y = np.array([1]*len(aadhaar_images) + [0]*len(synthetic_negatives))  # 1=Aadhaar, 0=Non
    
    return X / 255.0, y  # Normalized

# Load data
print("Loading and generating training data...")
X, y = load_training_data(DATA_DIR, BACKGROUND_DIR, IMG_SIZE)

# Split data
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Data augmentation
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomContrast(0.1)
])

# Model with pretrained weights for better feature extraction
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg'
)

model = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    data_augmentation,
    base_model,
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Freeze base model layers
base_model.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Train with early stopping
early_stopping = tf.keras.callbacks.EarlyStopping(
    patience=5,
    restore_best_weights=True
)

print("Training model...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    callbacks=[early_stopping]
)

# Save model
model.save("aadhaar_model_tf.keras")
print("Model saved successfully")

# Prediction function
def predict_aadhaar(image_path, model, threshold=0.9):  # Higher threshold for strict checks
    img = cv2.imread(image_path)
    if img is None:
        return "invalid_image", 0.0
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = np.expand_dims(img/255.0, axis=0)
    
    confidence = model.predict(img, verbose=0)[0][0]
    return ("aadhaar" if confidence >= threshold else "non", confidence)