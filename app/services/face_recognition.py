"""
Facial recognition service using face_recognition library.
"""
import face_recognition
import numpy as np
from typing import Optional, Tuple
import io
from PIL import Image

from config.settings import settings


class FaceRecognitionService:
    """Service for facial recognition operations."""
    
    def __init__(self, tolerance: float = None):
        """
        Initialize facial recognition service.
        
        Args:
            tolerance: Face comparison tolerance (lower is more strict)
        """
        self.tolerance = tolerance or settings.face_recognition_tolerance
    
    def extract_face_encoding(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Extract face encoding from an image.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Face encoding as numpy array, or None if no face found
        """
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert to RGB if needed
            if len(image_array.shape) == 2:  # Grayscale
                image_array = np.stack([image_array] * 3, axis=-1)
            elif image_array.shape[2] == 4:  # RGBA
                image_array = image_array[:, :, :3]
            
            # Detect faces and get encodings
            face_encodings = face_recognition.face_encodings(image_array)
            
            if len(face_encodings) == 0:
                return None
            
            # Return the first face encoding
            return face_encodings[0]
            
        except Exception as e:
            print(f"Error extracting face encoding: {e}")
            return None
    
    def compare_faces(self, known_encoding: np.ndarray, unknown_encoding: np.ndarray) -> Tuple[bool, float]:
        """
        Compare two face encodings.
        
        Args:
            known_encoding: Reference face encoding
            unknown_encoding: Face encoding to compare
            
        Returns:
            Tuple of (is_match, similarity_score)
        """
        try:
            # Calculate face distance (lower is more similar)
            face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            
            # Convert distance to similarity score (0-1, higher is more similar)
            similarity_score = 1.0 - face_distance
            
            # Check if faces match
            is_match = face_distance <= self.tolerance
            
            return is_match, similarity_score
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return False, 0.0
    
    def calculate_quality_score(self, image_data: bytes) -> float:
        """
        Calculate quality score for a face image.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Quality score (0-1, higher is better)
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert to RGB if needed
            if len(image_array.shape) == 2:
                image_array = np.stack([image_array] * 3, axis=-1)
            elif image_array.shape[2] == 4:
                image_array = image_array[:, :, :3]
            
            # Detect face landmarks
            face_landmarks_list = face_recognition.face_landmarks(image_array)
            
            if not face_landmarks_list:
                return 0.0
            
            # Basic quality metrics
            face_locations = face_recognition.face_locations(image_array)
            
            if not face_locations:
                return 0.0
            
            # Calculate face size (larger is generally better)
            top, right, bottom, left = face_locations[0]
            face_width = right - left
            face_height = bottom - top
            face_area = face_width * face_height
            
            # Normalize by image size
            image_area = image_array.shape[0] * image_array.shape[1]
            face_ratio = face_area / image_area
            
            # Quality score based on face size (optimal is 20-60% of image)
            if face_ratio < 0.1:
                quality = face_ratio * 5  # Too small
            elif face_ratio > 0.6:
                quality = (1.0 - face_ratio) * 2.5  # Too large
            else:
                quality = 1.0  # Good size
            
            return min(max(quality, 0.0), 1.0)
            
        except Exception as e:
            print(f"Error calculating quality score: {e}")
            return 0.0


# Global instance
face_recognition_service = FaceRecognitionService()
