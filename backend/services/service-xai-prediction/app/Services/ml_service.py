import joblib
import numpy as np
import shap
from typing import Dict, List, Tuple
from uuid import UUID, uuid4
import logging
from pathlib import Path

from app.core.config import settings
from app.models.XaiModels import (
    PredictionRequest,
    PredictionResult,
    Explanation,
    FeatureImportance,
    RiskLevel
)

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.metadata = None
        self.explainer = None
        self._load_models()
    
    def _load_models(self):
        """Load all trained models and artifacts"""
        try:
            # Convert relative paths to absolute paths
            base_path = Path(__file__).parent.parent.parent.parent.parent.parent / "ml" / "models" / "xai_predictor"
            
            logger.info(f"Loading models from: {base_path}")
            
            # Load trained model
            model_path = base_path / "student_model_best.joblib"
            self.model = joblib.load(model_path)
            logger.info("Loaded trained model")
            
            # Load scaler
            scaler_path = base_path / "scaler_best.joblib"
            self.scaler = joblib.load(scaler_path)
            logger.info("Loaded scaler")
            
            # Load label encoder
            encoder_path = base_path / "label_encoder_best.joblib"
            self.label_encoder = joblib.load(encoder_path)
            logger.info("Loaded label encoder")
            
            # Load feature names
            features_path = base_path / "model_features_best.joblib"
            self.feature_names = joblib.load(features_path)
            logger.info(f"Loaded {len(self.feature_names)} features")
            
            # Load metadata
            metadata_path = base_path / "model_metadata_best.joblib"
            self.metadata = joblib.load(metadata_path)
            logger.info("Loaded metadata")
            
            # Initialize SHAP explainer
            self._initialize_explainer()
            
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer for model interpretability"""
        try:
            # Use TreeExplainer for tree-based models (XGBoost, CatBoost, etc.)
            self.explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP explainer initialized")
        except Exception as e:
            logger.warning(f"Could not initialize SHAP explainer: {str(e)}")
            self.explainer = None
    
    def _prepare_features(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare and validate features for prediction"""
        # Create feature array in correct order
        feature_array = np.array([features.get(f, 0.0) for f in self.feature_names])
        
        # Reshape for single prediction
        feature_array = feature_array.reshape(1, -1)
        
        # Scale features
        scaled_features = self.scaler.transform(feature_array)
        
        return scaled_features
    
    def _calculate_risk_level(self, predicted_class: str, probability: float) -> RiskLevel:
        """Calculate risk level based on prediction and confidence"""
        if predicted_class == "Distinction" or predicted_class == "Pass":
            if probability >= 0.8:
                return RiskLevel.LOW
            elif probability >= 0.6:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.HIGH
        elif predicted_class == "Fail":
            if probability >= 0.7:
                return RiskLevel.CRITICAL
            elif probability >= 0.5:
                return RiskLevel.HIGH
            else:
                return RiskLevel.MEDIUM
        elif predicted_class == "Withdrawn":
            return RiskLevel.CRITICAL
        else:
            return RiskLevel.MEDIUM
    
    def _generate_explanation(
        self,
        shap_values: np.ndarray,
        features: Dict[str, float],
        predicted_class: str,
        probability: float
    ) -> Tuple[List[FeatureImportance], str, List[str], List[str]]:
        """Generate human-readable explanation from SHAP values"""
        
        # Get top features by absolute SHAP value
        feature_impacts = []
        for i, feature_name in enumerate(self.feature_names):
            shap_val = float(shap_values[i])
            feature_impacts.append({
                "name": feature_name,
                "value": features.get(feature_name, 0.0),
                "shap_value": shap_val,
                "abs_shap": abs(shap_val)
            })
        
        # Sort by absolute impact
        feature_impacts.sort(key=lambda x: x["abs_shap"], reverse=True)
        
        # Top 5 features
        top_features = []
        confidence_factors = []
        risk_factors = []
        
        for impact in feature_impacts[:5]:
            contribution = "positive" if impact["shap_value"] > 0 else "negative"
            
            feature_importance = FeatureImportance(
                feature_name=impact["name"],
                importance=impact["abs_shap"],
                shap_value=impact["shap_value"],
                contribution=contribution
            )
            top_features.append(feature_importance)
            
            # Build confidence and risk factors
            if contribution == "positive":
                confidence_factors.append(
                    f"{impact['name'].replace('_', ' ').title()}: {impact['value']}"
                )
            else:
                risk_factors.append(
                    f"{impact['name'].replace('_', ' ').title()}: {impact['value']}"
                )
        
        # Generate natural language explanation
        explanation_text = self._build_natural_language_explanation(
            predicted_class,
            probability,
            top_features
        )
        
        return top_features, explanation_text, confidence_factors, risk_factors
    
    def _build_natural_language_explanation(
        self,
        predicted_class: str,
        probability: float,
        top_features: List[FeatureImportance]
    ) -> str:
        """Build human-readable explanation"""
        
        confidence = "high" if probability >= 0.8 else "moderate" if probability >= 0.6 else "low"
        
        explanation = f"The student is predicted to {predicted_class} with {confidence} confidence ({probability:.1%} probability). "
        
        # Add top contributing factors
        positive_features = [f for f in top_features if f.contribution == "positive"]
        negative_features = [f for f in top_features if f.contribution == "negative"]
        
        if positive_features:
            explanation += f"Key positive factors: {', '.join([f.feature_name.replace('_', ' ') for f in positive_features[:3]])}. "
        
        if negative_features:
            explanation += f"Areas of concern: {', '.join([f.feature_name.replace('_', ' ') for f in negative_features[:3]])}."
        
        return explanation
    
    async def predict(self, request: PredictionRequest) -> Tuple[PredictionResult, Explanation]:
        """Make prediction and generate explanation"""
        try:
            request_id = uuid4()
            
            # Prepare features
            scaled_features = self._prepare_features(request.features)
            
            # Make prediction
            prediction_proba = self.model.predict_proba(scaled_features)[0]
            predicted_class_idx = np.argmax(prediction_proba)
            predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
            probability = float(prediction_proba[predicted_class_idx])
            
            # Get all class probabilities
            all_probabilities = {
                self.label_encoder.inverse_transform([i])[0]: float(prob)
                for i, prob in enumerate(prediction_proba)
            }
            
            # Calculate risk level
            risk_level = self._calculate_risk_level(predicted_class, probability)
            
            # Generate SHAP explanation
            shap_values_dict = {}
            top_features = []
            natural_language_explanation = f"Predicted outcome: {predicted_class} ({probability:.1%})"
            confidence_factors = []
            risk_factors = []
            
            if self.explainer:
                try:
                    shap_values = self.explainer.shap_values(scaled_features)
                    
                    # Handle multi-class SHAP values
                    if isinstance(shap_values, list):
                        shap_values = shap_values[predicted_class_idx]
                    
                    shap_values = shap_values[0]
                    
                    # Create SHAP values dictionary
                    shap_values_dict = {
                        feature: float(val) 
                        for feature, val in zip(self.feature_names, shap_values)
                    }
                    
                    # Generate detailed explanation
                    top_features, natural_language_explanation, confidence_factors, risk_factors = \
                        self._generate_explanation(
                            shap_values,
                            request.features,
                            predicted_class,
                            probability
                        )
                        
                except Exception as e:
                    logger.warning(f"Could not generate SHAP explanation: {str(e)}")
            
            # Create prediction result
            prediction_result = PredictionResult(
                request_id=request_id,
                student_id=request.student_id,
                predicted_class=predicted_class,
                probability=probability,
                probabilities=all_probabilities,
                risk_level=risk_level
            )
            
            # Create explanation
            explanation = Explanation(
                prediction_result_id=prediction_result.id,
                shap_values=shap_values_dict,
                top_features=top_features,
                natural_language_explanation=natural_language_explanation,
                confidence_factors=confidence_factors,
                risk_factors=risk_factors
            )
            
            return prediction_result, explanation
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise

# Initialize ML service (singleton)
ml_service = MLService()