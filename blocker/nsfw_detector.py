import os

class NSFWDetector:
    def __init__(self):
        self.model = None
        self.model_path = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
        self.threshold = 0.85
        self.tensorflow_available = False
        
        # Try to import TensorFlow
        try:
            import tensorflow as tf
            import tensorflow_hub as hub
            import numpy as np
            from PIL import Image
            self.tf = tf
            self.hub = hub
            self.np = np
            self.Image = Image
            self.tensorflow_available = True
        except ImportError:
            print("TensorFlow not available. NSFW image detection will be disabled.")
    
    def load_model(self):
        """Lazy load the model when needed"""
        if not self.tensorflow_available:
            return False
            
        if self.model is None:
            try:
                self.model = self.hub.load(self.model_path)
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return True

    def preprocess_image(self, image_path):
        """Prepare image for model input"""
        if not self.tensorflow_available:
            return None
            
        try:
            image = self.Image.open(image_path)
            image = image.convert('RGB')
            image = image.resize((224, 224))
            image = self.np.array(image) / 255.0
            image = self.np.expand_dims(image, axis=0)
            return image
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None

    def is_nsfw(self, image_path):
        """Check if an image is NSFW
        Returns:
            tuple: (is_nsfw, confidence_score)
        """
        if not self.tensorflow_available:
            return False, 0.0
            
        if not os.path.exists(image_path):
            return False, 0.0
            
        if not self.load_model():
            return False, 0.0
            
        image = self.preprocess_image(image_path)
        if image is None:
            return False, 0.0
            
        try:
            predictions = self.model(image)
            score = self.tf.nn.sigmoid(predictions[0]).numpy()
            
            # Convert score to NSFW probability
            nsfw_score = float(score[0])
            return nsfw_score > self.threshold, nsfw_score
        except Exception as e:
            print(f"Error during prediction: {e}")
            return False, 0.0

    def set_threshold(self, threshold):
        """Set the confidence threshold for NSFW detection"""
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
            
    def is_available(self):
        """Check if NSFW detection is available"""
        return self.tensorflow_available
