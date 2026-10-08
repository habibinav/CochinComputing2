import tensorflow as tf
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def classify_aadhaar(image_path, model_path='aadhaar_model_tf.keras', threshold=0.8):
    try:
        # Load model with validation
        model = tf.keras.models.load_model(model_path)
        
        # Preprocess image
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Get prediction
        confidence = float(model.predict(img_array, verbose=0)[0][0])
        is_aadhaar = confidence > threshold
        
        return is_aadhaar, confidence
        
    except Exception as e:
        print(f"⚠️ Classification error: {str(e)}")
        return False, 0.0

def verify_model(model_path='aadhaar_model_tf.keras'):
    """Proper model verification"""
    try:
        model = tf.keras.models.load_model(model_path)
        print("\n✅ Model loaded successfully")
        print(f"ℹ️ Input shape expected: {model.input_shape[1:3]} (height, width)")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    # Model verification
    if not verify_model():
        sys.exit(1)
    
    # Image path handling
    filepath = sys.argv[1] if len(sys.argv) > 1 else input("Enter image path: ").strip()
    
    # Classification
    is_aadhaar, confidence = classify_aadhaar(filepath)
    
    # Results with color coding
    result_color = '\033[92m' if is_aadhaar else '\033[91m'
    print(f"\n📊 Result: {result_color}{'AADHAAR' if is_aadhaar else 'NOT AADHAAR'}\033[0m")
    print(f"🔐 Confidence: {confidence:.2%}")
    print(f"⚖️ Threshold: {80}%")
    
    # Confidence interpretation
    if confidence > 0.9:
        print("💡 Very high confidence")
    elif confidence > 0.7:
        print("💡 High confidence")
    elif confidence > 0.5:
        print("⚠️ Moderate confidence - verify manually")
    else:
        print("❌ Low confidence - likely not Aadhaar")