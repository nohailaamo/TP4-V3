"""
Voice recognition service using librosa for MFCC extraction.
"""
import librosa
import numpy as np
from typing import Optional, Tuple
import io
import soundfile as sf
from scipy.spatial.distance import cosine

from config.settings import settings


class VoiceRecognitionService:
    """Service for voice recognition operations using MFCC features."""
    
    def __init__(self, n_mfcc: int = None):
        """
        Initialize voice recognition service.
        
        Args:
            n_mfcc: Number of MFCC coefficients to extract
        """
        self.n_mfcc = n_mfcc or settings.voice_mfcc_n_mfcc
    
    def extract_voice_features(self, audio_data: bytes) -> Optional[np.ndarray]:
        """
        Extract MFCC features from audio data.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            MFCC feature vector as numpy array, or None if extraction fails
        """
        try:
            # Load audio from bytes
            audio_io = io.BytesIO(audio_data)
            y, sr = sf.read(audio_io)
            
            # If stereo, convert to mono
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            
            # Calculate statistics across time (mean and std)
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            
            # Combine mean and std into a single feature vector
            features = np.concatenate([mfcc_mean, mfcc_std])
            
            return features
            
        except Exception as e:
            print(f"Error extracting voice features: {e}")
            return None
    
    def compare_voices(self, known_features: np.ndarray, unknown_features: np.ndarray) -> Tuple[bool, float]:
        """
        Compare two voice feature vectors.
        
        Args:
            known_features: Reference voice features
            unknown_features: Voice features to compare
            
        Returns:
            Tuple of (is_match, similarity_score)
        """
        try:
            # Calculate cosine similarity
            cos_distance = cosine(known_features, unknown_features)
            
            # Convert to similarity score (0-1, higher is more similar)
            similarity_score = 1.0 - cos_distance
            
            # Check if voices match (using similarity threshold)
            is_match = similarity_score >= settings.similarity_threshold
            
            return is_match, similarity_score
            
        except Exception as e:
            print(f"Error comparing voices: {e}")
            return False, 0.0
    
    def calculate_quality_score(self, audio_data: bytes) -> float:
        """
        Calculate quality score for an audio sample.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Quality score (0-1, higher is better)
        """
        try:
            # Load audio from bytes
            audio_io = io.BytesIO(audio_data)
            y, sr = sf.read(audio_io)
            
            # If stereo, convert to mono
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)
            
            # Calculate quality metrics
            
            # 1. Signal-to-noise ratio (simplified)
            signal_power = np.mean(y ** 2)
            
            # 2. Duration (optimal is 2-10 seconds)
            duration = len(y) / sr
            if duration < 1.0:
                duration_score = duration
            elif duration > 10.0:
                duration_score = 10.0 / duration
            else:
                duration_score = 1.0
            
            # 3. Dynamic range
            dynamic_range = np.max(np.abs(y)) - np.min(np.abs(y))
            dynamic_score = min(dynamic_range * 2, 1.0)
            
            # Combine scores
            quality_score = (duration_score * 0.5 + dynamic_score * 0.5)
            
            return min(max(quality_score, 0.0), 1.0)
            
        except Exception as e:
            print(f"Error calculating quality score: {e}")
            return 0.0
    
    def calculate_metrics(self, known_features: np.ndarray, test_features_list: list) -> dict:
        """
        Calculate FAR, FRR, and EER metrics.
        
        Args:
            known_features: Reference features
            test_features_list: List of tuples (features, is_genuine)
            
        Returns:
            Dictionary with FAR, FRR, EER values
        """
        try:
            thresholds = np.linspace(0, 1, 100)
            far_list = []
            frr_list = []
            
            for threshold in thresholds:
                false_accepts = 0
                false_rejects = 0
                total_imposters = 0
                total_genuine = 0
                
                for features, is_genuine in test_features_list:
                    _, similarity = self.compare_voices(known_features, features)
                    
                    if is_genuine:
                        total_genuine += 1
                        if similarity < threshold:
                            false_rejects += 1
                    else:
                        total_imposters += 1
                        if similarity >= threshold:
                            false_accepts += 1
                
                far = false_accepts / total_imposters if total_imposters > 0 else 0
                frr = false_rejects / total_genuine if total_genuine > 0 else 0
                
                far_list.append(far)
                frr_list.append(frr)
            
            # Find EER (Equal Error Rate)
            far_array = np.array(far_list)
            frr_array = np.array(frr_list)
            eer_idx = np.argmin(np.abs(far_array - frr_array))
            eer = (far_array[eer_idx] + frr_array[eer_idx]) / 2
            
            return {
                "FAR": float(far_array[eer_idx]),
                "FRR": float(frr_array[eer_idx]),
                "EER": float(eer)
            }
            
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {"FAR": 0.0, "FRR": 0.0, "EER": 0.0}


# Global instance
voice_recognition_service = VoiceRecognitionService()
