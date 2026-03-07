"""Pydantic schemas package"""
from app.schemas.learning_style import (
    # Student Profile
    StudentLearningProfileCreate,
    StudentLearningProfileUpdate,
    StudentLearningProfileResponse,
    LearningStylePrediction,
    
    # Resources
    LearningResourceCreate,
    LearningResourceUpdate,
    LearningResourceResponse,
    LearningResourceList,
    
    # Struggles
    StudentStruggleCreate,
    StudentStruggleResponse,
    StudentStruggleList,
    
    # Recommendations
    ResourceRecommendationCreate,
    ResourceRecommendationResponse,
    RecommendationRequest,
    GenerateRecommendationsResponse,
    RecommendationList,
    RecommendationFeedback,
    RecommendationEngagement,
    
    # Behavior Tracking
    StudentBehaviorCreate,
    StudentBehaviorResponse,
    
    # Analytics
    StudentAnalytics,
    ResourceEffectiveness,
    SystemStats
)

__all__ = [
    # Student Profile
    "StudentLearningProfileCreate",
    "StudentLearningProfileUpdate",
    "StudentLearningProfileResponse",
    "LearningStylePrediction",
    
    # Resources
    "LearningResourceCreate",
    "LearningResourceUpdate",
    "LearningResourceResponse",
    "LearningResourceList",
    
    # Struggles
    "StudentStruggleCreate",
    "StudentStruggleResponse",
    "StudentStruggleList",
    
    # Recommendations
    "ResourceRecommendationCreate",
    "ResourceRecommendationResponse",
    "RecommendationRequest",
    "GenerateRecommendationsResponse",
    "RecommendationList",
    "RecommendationFeedback",
    "RecommendationEngagement",
    
    # Behavior Tracking
    "StudentBehaviorCreate",
    "StudentBehaviorResponse",
    
    # Analytics
    "StudentAnalytics",
    "ResourceEffectiveness",
    "SystemStats"
]

