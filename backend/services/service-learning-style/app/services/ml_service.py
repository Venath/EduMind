"""
Machine Learning Service for Learning Style Prediction

This service provides real-time learning style classification for students
using a trained Random Forest model.

PRODUCTION ML CONCEPTS:
- Model Loading: Load pre-trained model from disk
- Feature Engineering: Apply same transformations as training
- Prediction: Classify new students
- Confidence Scoring: Probability-based confidence
- Error Handling: Graceful degradation when insufficient data

Author: Subasinghe S A V R (IT22325846)
"""

import joblib
import sys
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

# Add ml directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from ml.feature_engineering import LearningStyleFeatureEngineer
from app.models.learning_style import StudentLearningProfile, StudentBehaviorTracking


class LearningStyleMLService:
    """
    Production ML service for learning style classification.
    
    This class handles:
    - Loading trained models
    - Feature engineering for new data
    - Making predictions
    - Updating student profiles
    - Batch processing
    """
    
    def __init__(self, model_dir: str = "ml_models"):
        """
        Initialize ML service.
        
        Args:
            model_dir: Directory containing trained model files
        """
        self.model_dir = Path(model_dir)
        self.model = None
        self.feature_names = None
        self.metadata = None
        self.feature_engineer = LearningStyleFeatureEngineer()
        
        # Load model on initialization
        self._load_model()
    
    def _load_model(self):
        """
        Load trained model and metadata from disk.
        
        EXPLANATION:
        Models are saved as .pkl files using joblib.
        We load:
        1. The trained model (RandomForestClassifier)
        2. Feature names (to ensure correct order)
        3. Metadata (training info, accuracy, etc.)
        """
        try:
            # Find latest model version
            model_files = list(self.model_dir.glob("learning_style_classifier_v*.pkl"))
            if not model_files:
                raise FileNotFoundError(f"No trained model found in {self.model_dir}")
            
            # Use most recent model
            model_path = sorted(model_files)[-1]
            print(f"[ML Service] Loading model: {model_path.name}")
            
            # Load model
            self.model = joblib.load(model_path)
            
            # Load feature names
            features_path = self.model_dir / "feature_names.pkl"
            if features_path.exists():
                self.feature_names = joblib.load(features_path)
            else:
                # Fallback to default feature names
                self.feature_names = self.feature_engineer.get_feature_columns()
            
            # Load metadata
            metadata_path = self.model_dir / "model_metadata.json"
            if metadata_path.exists():
                import json
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            
            print(f"[ML Service] Model loaded successfully!")
            print(f"[ML Service]   Type: {type(self.model).__name__}")
            print(f"[ML Service]   Features: {len(self.feature_names)}")
            if self.metadata:
                print(f"[ML Service]   Accuracy: {self.metadata.get('accuracy', 'N/A'):.4f}")
            
        except Exception as e:
            print(f"[ML Service] ERROR loading model: {str(e)}")
            print(f"[ML Service] Predictions will not be available until model is trained.")
            self.model = None
    
    def check_data_sufficiency(self, student_id: str, db: Session, min_days: int = 7) -> Dict:
        """
        Check if student has sufficient data for classification.
        
        REQUIREMENT:
        Students need at least 7 days of behavior tracking for reliable classification.
        
        Args:
            student_id: Student ID
            db: Database session
            min_days: Minimum days required
            
        Returns:
            Dict with 'sufficient' (bool) and 'days_tracked' (int)
        """
        # Count days of tracking data
        days_tracked = db.query(StudentBehaviorTracking).filter(
            StudentBehaviorTracking.student_id == student_id
        ).count()
        
        return {
            'sufficient': days_tracked >= min_days,
            'days_tracked': days_tracked,
            'min_required': min_days
        }
    
    def get_student_behavior_data(self, student_id: str, db: Session, days: int = 14) -> List[Dict]:
        """
        Retrieve behavior data for a student.
        
        Args:
            student_id: Student ID
            db: Database session
            days: Number of recent days to retrieve
            
        Returns:
            List of behavior records as dicts
        """
        # Get recent behavior data
        cutoff_date = datetime.now() - timedelta(days=days)
        
        records = db.query(StudentBehaviorTracking).filter(
            StudentBehaviorTracking.student_id == student_id,
            StudentBehaviorTracking.tracking_date >= cutoff_date
        ).all()
        
        # Convert to list of dicts
        behavior_data = []
        for record in records:
            behavior_data.append({
                'student_id': record.student_id,
                'tracking_date': record.tracking_date,
                'video_watch_time': record.video_watch_time or 0,
                'video_completion_rate': record.video_completion_rate or 0,
                'video_interactions': record.video_interactions or 0,
                'text_read_time': record.text_read_time or 0,
                'articles_read': record.articles_read or 0,
                'note_taking_count': record.note_taking_count or 0,
                'audio_playback_time': record.audio_playback_time or 0,
                'podcast_completions': record.podcast_completions or 0,
                'simulation_time': record.simulation_time or 0,
                'interactive_exercises': record.interactive_exercises or 0,
                'hands_on_activities': record.hands_on_activities or 0,
                'forum_posts': record.forum_posts or 0,
                'discussion_participation': record.discussion_participation or 0,
                'peer_interactions': record.peer_interactions or 0,
                'diagram_views': record.diagram_views or 0,
                'image_interactions': record.image_interactions or 0,
                'visual_aid_usage': record.visual_aid_usage or 0,
                'total_session_time': record.total_session_time or 0,
                'login_count': record.login_count or 0
            })
        
        return behavior_data

    def _blend_with_behavior(self, aggregated: pd.DataFrame, ml_probs: Dict) -> Dict:
        """
        Blend ML probabilities with a distribution derived from raw behavior
        so that recent activity (video, reading, etc.) visibly shifts the result.
        VARK mapping: Visual ~ diagram/image, Auditory ~ video/audio, Reading ~ text/articles, Kinesthetic ~ interactive/hands-on.
        """
        style_keys = ['Visual', 'Auditory', 'Reading', 'Kinesthetic', 'Mixed']
        if aggregated.empty:
            return ml_probs
        row = aggregated.iloc[0]
        # Raw sums (avoid 0 to get a valid distribution)
        visual_s = max(0, float(row.get('diagram_views', 0) or 0) + float(row.get('image_interactions', 0) or 0) + float(row.get('visual_aid_usage', 0) or 0)) + 1e-6
        auditory_s = max(0, float(row.get('video_watch_time', 0) or 0) / 60.0 + float(row.get('audio_playback_time', 0) or 0) / 60.0 + float(row.get('video_interactions', 0) or 0)) + 1e-6
        reading_s = max(0, float(row.get('text_read_time', 0) or 0) / 60.0 + float(row.get('articles_read', 0) or 0)) + 1e-6
        kinesthetic_s = max(0, float(row.get('interactive_exercises', 0) or 0) + float(row.get('hands_on_activities', 0) or 0) + float(row.get('simulation_time', 0) or 0) / 60.0) + 1e-6
        total = visual_s + auditory_s + reading_s + kinesthetic_s
        behavior_probs = {
            'Visual': visual_s / total,
            'Auditory': auditory_s / total,
            'Reading': reading_s / total,
            'Kinesthetic': kinesthetic_s / total,
            'Mixed': 0.0,
        }
        # Blend: 45% ML, 55% behavior so recent activity clearly affects the distribution
        blend = 0.45
        out = {}
        for k in style_keys:
            out[k] = blend * float(ml_probs.get(k, 0.0)) + (1.0 - blend) * float(behavior_probs.get(k, 0.0))
        s = sum(out.values())
        if s > 0:
            out = {k: v / s for k, v in out.items()}
        return out
    
    def predict_learning_style(self, student_id: str, db: Session) -> Dict:
        """
        Predict learning style for a student.
        
        PREDICTION PIPELINE:
        1. Check data sufficiency (min 7 days)
        2. Load behavior data
        3. Aggregate and engineer features
        4. Make prediction with model
        5. Calculate confidence score
        6. Return results
        
        Args:
            student_id: Student ID
            db: Database session
            
        Returns:
            Dict with prediction results or error
        """
        # Check if model is loaded
        if self.model is None:
            return {
                'error': 'Model not available',
                'message': 'ML model not trained yet. Please train model first.'
            }
        
        # Check data sufficiency
        data_check = self.check_data_sufficiency(student_id, db)
        if not data_check['sufficient']:
            return {
                'error': 'Insufficient data',
                'message': f"Need {data_check['min_required']} days of data, student has {data_check['days_tracked']} days",
                'days_tracked': data_check['days_tracked'],
                'min_required': data_check['min_required']
            }
        
        try:
            # Get behavior data
            behavior_data = self.get_student_behavior_data(student_id, db)
            
            if not behavior_data:
                return {
                    'error': 'No behavior data',
                    'message': 'No behavior tracking data found for student'
                }
            
            # Aggregate behavior
            aggregated = self.feature_engineer.aggregate_behavior_data(behavior_data)
            
            # Engineer features
            features_df = self.feature_engineer.engineer_features(aggregated)
            
            # Select feature columns in correct order
            X = features_df[self.feature_names]
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            # Map probabilities to class names
            classes = self.model.classes_
            prob_dict = {
                str(cls): float(prob)
                for cls, prob in zip(classes, probabilities)
            }
            
            # Blend with behavior-based distribution so recent activity (video, reading, etc.) visibly shifts the result
            prob_dict = self._blend_with_behavior(aggregated, prob_dict)
            
            # Recompute predicted_style and confidence from blended distribution
            predicted_style = max(prob_dict, key=prob_dict.get)
            confidence = float(prob_dict.get(predicted_style, 0.0))
            
            if confidence >= 0.8:
                confidence_level = 'High'
            elif confidence >= 0.6:
                confidence_level = 'Medium'
            else:
                confidence_level = 'Low'
            
            return {
                'student_id': student_id,
                'predicted_style': predicted_style,
                'confidence': confidence,
                'confidence_level': confidence_level,
                'probabilities': prob_dict,
                'days_tracked': data_check['days_tracked'],
                'model_version': (self.metadata.get('version', '1.0') if self.metadata else '1.0') + '+behavior',
                'predicted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': 'Prediction failed',
                'message': str(e)
            }
    
    def update_student_profile(self, student_id: str, prediction: Dict, db: Session) -> bool:
        """
        Update student's learning profile with ML prediction.
        
        Args:
            student_id: Student ID
            prediction: Prediction result dict
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get student profile
            profile = db.query(StudentLearningProfile).filter(
                StudentLearningProfile.student_id == student_id
            ).first()
            
            if not profile:
                return False
            
            # Update with prediction
            profile.learning_style = prediction['predicted_style']
            profile.style_confidence = prediction['confidence']
            probs = prediction.get('probabilities')
            if isinstance(probs, dict):
                profile.style_probabilities = probs
            profile.updated_at = datetime.now()
            
            db.commit()
            
            print(f"[ML Service] Updated profile for {student_id}: {prediction['predicted_style']} ({prediction['confidence']:.2f})")
            
            return True
            
        except Exception as e:
            print(f"[ML Service] Error updating profile: {str(e)}")
            db.rollback()
            return False
    
    def classify_and_update(self, student_id: str, db: Session) -> Dict:
        """
        Predict learning style and update student profile in one call.
        
        Args:
            student_id: Student ID
            db: Database session
            
        Returns:
            Prediction result dict
        """
        # Make prediction
        prediction = self.predict_learning_style(student_id, db)
        
        # If successful, update profile
        if 'error' not in prediction:
            self.update_student_profile(student_id, prediction, db)
        
        return prediction
    
    def batch_classify(self, db: Session, min_days: int = 7) -> Dict:
        """
        Classify all students with sufficient data.
        
        BATCH PROCESSING:
        - Useful for nightly jobs
        - Classifies all eligible students
        - Updates their profiles
        - Returns summary statistics
        
        Args:
            db: Database session
            min_days: Minimum days of data required
            
        Returns:
            Dict with batch processing results
        """
        print(f"\n[ML Service] Starting batch classification...")
        
        # Get all students with profiles
        profiles = db.query(StudentLearningProfile).all()
        
        results = {
            'total_students': len(profiles),
            'classified': 0,
            'insufficient_data': 0,
            'errors': 0,
            'predictions': []
        }
        
        for profile in profiles:
            student_id = profile.student_id
            
            # Check data sufficiency
            data_check = self.check_data_sufficiency(student_id, db, min_days)
            
            if not data_check['sufficient']:
                results['insufficient_data'] += 1
                continue
            
            # Predict and update
            prediction = self.classify_and_update(student_id, db)
            
            if 'error' in prediction:
                results['errors'] += 1
            else:
                results['classified'] += 1
                results['predictions'].append({
                    'student_id': student_id,
                    'style': prediction['predicted_style'],
                    'confidence': prediction['confidence']
                })
        
        print(f"[ML Service] Batch classification complete:")
        print(f"[ML Service]   Total: {results['total_students']}")
        print(f"[ML Service]   Classified: {results['classified']}")
        print(f"[ML Service]   Insufficient data: {results['insufficient_data']}")
        print(f"[ML Service]   Errors: {results['errors']}")
        
        return results
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dict with model metadata
        """
        if self.model is None:
            return {
                'status': 'not_loaded',
                'message': 'No model available'
            }
        
        info = {
            'status': 'loaded',
            'model_type': type(self.model).__name__,
            'num_features': len(self.feature_names),
            'classes': self.model.classes_.tolist() if hasattr(self.model, 'classes_') else []
        }
        
        # Add metadata if available
        if self.metadata:
            info.update({
                'version': self.metadata.get('version'),
                'training_date': self.metadata.get('training_date'),
                'accuracy': self.metadata.get('accuracy'),
                'num_training_samples': self.metadata.get('num_training_samples')
            })
        
        return info


# ============================================================
# SINGLETON INSTANCE
# ============================================================

# Create a single instance to be used across the application
_ml_service_instance = None

def get_ml_service() -> LearningStyleMLService:
    """
    Get singleton instance of ML service.
    
    This ensures we only load the model once, not on every request.
    """
    global _ml_service_instance
    
    if _ml_service_instance is None:
        _ml_service_instance = LearningStyleMLService()
    
    return _ml_service_instance






