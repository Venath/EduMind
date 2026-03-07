"""Recommendation Service - 6-Factor Weighted Scoring Algorithm"""
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
import math

from app.models import (
    StudentLearningProfile,
    LearningResource,
    StudentStruggle,
    ResourceRecommendation
)
from app.core.config import settings


class RecommendationService:
    """
    Implements the 6-factor weighted scoring algorithm for resource recommendations
    
    Factors:
    1. Learning Style Match (30%)
    2. Topic Relevance (25%)
    3. Difficulty Alignment (20%)
    4. Resource Effectiveness (15%)
    5. Recency & Freshness (5%)
    6. Diversity Bonus (5%)
    """
    
    # Weights for scoring factors
    WEIGHTS = {
        "learning_style_match": 0.30,
        "topic_relevance": 0.25,
        "difficulty_alignment": 0.20,
        "resource_effectiveness": 0.15,
        "recency_freshness": 0.05,
        "diversity_bonus": 0.05
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_recommendations(
        self,
        student_id: str,
        topic: Optional[str] = None,
        struggle_id: Optional[int] = None,
        max_recommendations: int = 5
    ) -> List[Tuple[LearningResource, float, Dict[str, float]]]:
        """
        Generate personalized recommendations for a student
        
        Returns:
            List of tuples: (resource, total_score, score_breakdown)
        """
        # Get student profile
        student = self.db.query(StudentLearningProfile).filter(
            StudentLearningProfile.student_id == student_id
        ).first()
        
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Get struggle context if provided
        struggle = None
        if struggle_id:
            struggle = self.db.query(StudentStruggle).filter(
                StudentStruggle.struggle_id == struggle_id
            ).first()
            if struggle:
                topic = struggle.topic  # Override topic with struggle topic
        
        # Get candidate resources
        resources = self._get_candidate_resources(topic, student)
        
        # Get recently recommended resources for diversity
        recent_recommendations = self._get_recent_recommendations(student_id, days=7)
        recent_resource_ids = [r.resource_id for r in recent_recommendations]
        recent_resource_types = [r.resource.resource_type for r in recent_recommendations if r.resource]
        
        # Score each resource
        scored_resources = []
        for resource in resources:
            score_breakdown = self._calculate_scores(
                resource, student, topic, recent_resource_types
            )
            total_score = sum(
                score_breakdown[factor] * self.WEIGHTS[factor]
                for factor in self.WEIGHTS.keys()
            )
            # Slightly down-rank if recommended recently (diversity), but still include to avoid empty list
            if resource.resource_id in recent_resource_ids:
                total_score *= 0.7
            scored_resources.append((resource, total_score, score_breakdown))

        # Sort by score and return top N
        scored_resources.sort(key=lambda x: x[1], reverse=True)
        return scored_resources[:max_recommendations]
    
    def _get_candidate_resources(
        self,
        topic: Optional[str],
        student: StudentLearningProfile
    ) -> List[LearningResource]:
        """Get candidate resources for recommendation"""
        query = self.db.query(LearningResource).filter(
            LearningResource.is_active == True
        )
        
        # Filter by topic if provided
        if topic:
            query = query.filter(LearningResource.topic.ilike(f"%{topic}%"))
        
        # Prefer resources matching student's learning style
        # But include others too for diversity
        return query.order_by(
            desc(LearningResource.effectiveness_rating),
            desc(LearningResource.popularity_score)
        ).limit(50).all()
    
    def _get_recent_recommendations(
        self,
        student_id: str,
        days: int = 7
    ) -> List[ResourceRecommendation]:
        """Get recent recommendations for diversity check"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.db.query(ResourceRecommendation).filter(
            and_(
                ResourceRecommendation.student_id == student_id,
                ResourceRecommendation.recommended_at >= cutoff_date
            )
        ).all()
    
    def _calculate_scores(
        self,
        resource: LearningResource,
        student: StudentLearningProfile,
        topic: Optional[str],
        recent_types: List[str]
    ) -> Dict[str, float]:
        """Calculate all 6 scoring factors"""
        return {
            "learning_style_match": self._score_learning_style_match(resource, student),
            "topic_relevance": self._score_topic_relevance(resource, topic, student),
            "difficulty_alignment": self._score_difficulty_alignment(resource, student),
            "resource_effectiveness": self._score_resource_effectiveness(resource),
            "recency_freshness": self._score_recency_freshness(resource),
            "diversity_bonus": self._score_diversity_bonus(resource, recent_types)
        }
    
    def _score_learning_style_match(
        self,
        resource: LearningResource,
        student: StudentLearningProfile
    ) -> float:
        """
        Factor 1: Learning Style Match (30%)
        
        Score based on how well resource matches student's learning style
        """
        student_style = student.learning_style
        style_confidence = student.style_confidence
        
        # Check if resource supports student's learning style
        if not resource.learning_styles or len(resource.learning_styles) == 0:
            return 0.5  # Neutral if no style specified
        
        # Perfect match
        if student_style in resource.learning_styles:
            return 0.8 + (0.2 * style_confidence)  # 0.8-1.0 based on confidence
        
        # Partial match for "Mixed" students
        if student_style == "Mixed":
            # Check secondary preferences from probabilities
            style_probs = student.style_probabilities or {}
            match_score = 0.0
            for style, prob in style_probs.items():
                if style in resource.learning_styles:
                    match_score = max(match_score, prob)
            return match_score
        
        # No match
        return 0.3  # Still usable, but not ideal
    
    def _score_topic_relevance(
        self,
        resource: LearningResource,
        topic: Optional[str],
        student: StudentLearningProfile
    ) -> float:
        """
        Factor 2: Topic Relevance (25%)
        
        How relevant is the resource to the struggle topic?
        """
        if not topic:
            # No specific topic - check if it's in student's struggle topics
            if student.struggle_topics and resource.topic in student.struggle_topics:
                return 0.9
            return 0.5  # Neutral
        
        topic_lower = topic.lower()
        resource_topic_lower = resource.topic.lower()
        
        # Exact match
        if topic_lower == resource_topic_lower:
            return 1.0
        
        # Partial match
        if topic_lower in resource_topic_lower or resource_topic_lower in topic_lower:
            return 0.8
        
        # Check subtopic
        if resource.subtopic and topic_lower in resource.subtopic.lower():
            return 0.7
        
        # Check tags
        if resource.tags:
            for tag in resource.tags:
                if topic_lower in tag.lower():
                    return 0.6
        
        return 0.2  # Not relevant
    
    def _score_difficulty_alignment(
        self,
        resource: LearningResource,
        student: StudentLearningProfile
    ) -> float:
        """
        Factor 3: Difficulty Alignment (20%)
        
        Match difficulty to student's preference and performance
        """
        preferred = student.preferred_difficulty
        resource_diff = resource.difficulty_level
        
        # Perfect match
        if preferred == resource_diff:
            return 1.0
        
        # Student prefers Medium
        if preferred == "Medium":
            if resource_diff in ["Easy", "Hard"]:
                return 0.7
        
        # Student prefers Easy but resource is Medium
        elif preferred == "Easy":
            if resource_diff == "Medium":
                return 0.6
            elif resource_diff == "Hard":
                return 0.3
        
        # Student prefers Hard but resource is Medium
        elif preferred == "Hard":
            if resource_diff == "Medium":
                return 0.8
            elif resource_diff == "Easy":
                return 0.4
        
        return 0.5
    
    def _score_resource_effectiveness(
        self,
        resource: LearningResource
    ) -> float:
        """
        Factor 4: Resource Effectiveness (15%)
        
        Historical performance of the resource
        """
        # Normalize effectiveness rating (0-5 scale to 0-1)
        effectiveness = resource.effectiveness_rating / 5.0
        
        # Normalize helpfulness rating (0-5 scale to 0-1)
        helpfulness = resource.avg_helpfulness_rating / 5.0
        
        # Calculate completion rate
        completion_rate = 0.5
        if resource.total_views > 0:
            completion_rate = resource.total_completions / resource.total_views
        
        # Weighted combination
        score = (
            effectiveness * 0.4 +
            helpfulness * 0.3 +
            completion_rate * 0.3
        )
        
        # Boost for verified resources
        if resource.verified:
            score = min(1.0, score * 1.1)
        
        return score
    
    def _score_recency_freshness(
        self,
        resource: LearningResource
    ) -> float:
        """
        Factor 5: Recency & Freshness (5%)
        
        Prefer newer resources
        """
        if not resource.created_at:
            return 0.5
        
        # Calculate age in days
        age_days = (datetime.now() - resource.created_at).days
        
        # Score decay over time (exponential)
        # New (0-30 days): 1.0
        # Recent (31-90 days): 0.8
        # Older (91-180 days): 0.6
        # Old (181+ days): 0.4
        
        if age_days <= 30:
            return 1.0
        elif age_days <= 90:
            return 0.8
        elif age_days <= 180:
            return 0.6
        else:
            return 0.4
    
    def _score_diversity_bonus(
        self,
        resource: LearningResource,
        recent_types: List[str]
    ) -> float:
        """
        Factor 6: Diversity Bonus (5%)
        
        Encourage variety in resource types
        """
        resource_type = resource.resource_type
        
        # Count occurrences of this type in recent recommendations
        type_count = recent_types.count(resource_type)
        
        # Higher score for underrepresented types
        if type_count == 0:
            return 1.0  # New type - great diversity!
        elif type_count == 1:
            return 0.7
        elif type_count == 2:
            return 0.4
        else:
            return 0.2  # Over-represented type
    
    def save_recommendations(
        self,
        student_id: str,
        scored_resources: List[Tuple[LearningResource, float, Dict[str, float]]],
        struggle_id: Optional[int] = None
    ) -> List[ResourceRecommendation]:
        """Save recommendations to database. Skips creating duplicate rows for same student+resource (reuses existing for response)."""
        recommendations = []
        cutoff = datetime.now() - timedelta(days=7)

        for rank, (resource, score, breakdown) in enumerate(scored_resources, start=1):
            existing = self.db.query(ResourceRecommendation).filter(
                ResourceRecommendation.student_id == student_id,
                ResourceRecommendation.resource_id == resource.resource_id,
                ResourceRecommendation.recommended_at >= cutoff,
            ).order_by(desc(ResourceRecommendation.recommended_at)).first()

            if existing:
                recommendations.append(existing)
                continue

            if score >= settings.HIGH_PRIORITY_THRESHOLD:
                priority = "High"
            elif score >= settings.MEDIUM_PRIORITY_THRESHOLD:
                priority = "Medium"
            else:
                priority = "Low"

            reason = self._generate_reason(resource, breakdown, struggle_id)
            recommendation = ResourceRecommendation(
                student_id=student_id,
                resource_id=resource.resource_id,
                struggle_id=struggle_id,
                reason=reason,
                relevance_score=round(score, 3),
                score_breakdown=breakdown,
                rank_position=rank,
                priority=priority,
                recommended_at=datetime.now()
            )
            self.db.add(recommendation)
            recommendations.append(recommendation)

        self.db.commit()
        return recommendations
    
    def _generate_reason(
        self,
        resource: LearningResource,
        breakdown: Dict[str, float],
        struggle_id: Optional[int]
    ) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        # Learning style match
        if breakdown["learning_style_match"] >= 0.8:
            reasons.append(f"Matches your {resource.learning_styles[0]} learning style")
        
        # Topic relevance
        if breakdown["topic_relevance"] >= 0.8:
            reasons.append(f"Highly relevant to {resource.topic}")
        
        # Struggle context
        if struggle_id:
            reasons.append("Recommended to help with your recent struggle")
        
        # Effectiveness
        if breakdown["resource_effectiveness"] >= 0.8:
            reasons.append(f"Highly rated ({resource.effectiveness_rating:.1f}/5.0)")
        
        # Difficulty
        reasons.append(f"{resource.difficulty_level} difficulty level")
        
        return " • ".join(reasons)











