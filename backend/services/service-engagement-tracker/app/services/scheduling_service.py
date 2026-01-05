"""
Personalized Study Scheduling Service

Uses engagement features to generate adaptive study schedules:
1. Session length personalization
2. Time-of-day scheduling
3. Course effort rebalancing
4. Decline-aware load reduction
"""
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, datetime, timedelta
import math
import json

from app.models import EngagementScore, StudySchedule


class SchedulingService:
    """
    Generates personalized study schedules based on engagement features
    """
    
    # Session length ranges (in minutes)
    MIN_SESSION_LENGTH = 15
    MAX_SESSION_LENGTH = 90
    DEFAULT_SESSION_LENGTH = 45
    
    # Sessions per day ranges
    MIN_SESSIONS_PER_DAY = 1
    MAX_SESSIONS_PER_DAY = 5
    DEFAULT_SESSIONS_PER_DAY = 2
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_engagement_features(self, student_id: str) -> Dict:
        """
        Extract all engagement features needed for scheduling
        
        Returns:
            Dict with all feature values
        """
        # Get latest engagement score
        latest_score = self.db.query(EngagementScore).filter(
            EngagementScore.student_id == student_id
        ).order_by(desc(EngagementScore.date)).first()
        
        if not latest_score:
            raise ValueError(f"No engagement data found for student {student_id}")
        
        # Get last 7 days for volatility calculation
        seven_days_ago = latest_score.date - timedelta(days=7)
        recent_scores = self.db.query(EngagementScore).filter(
            EngagementScore.student_id == student_id,
            EngagementScore.date >= seven_days_ago,
            EngagementScore.date <= latest_score.date
        ).order_by(EngagementScore.date).all()
        
        # Calculate engagement volatility (standard deviation)
        if len(recent_scores) >= 2:
            scores_list = [s.engagement_score for s in recent_scores]
            mean_score = sum(scores_list) / len(scores_list)
            variance = sum((x - mean_score) ** 2 for x in scores_list) / len(scores_list)
            engagement_volatility_7days = math.sqrt(variance)
        else:
            engagement_volatility_7days = 0.0
        
        # Calculate consecutive low engagement days
        consecutive_low_days = 0
        for score in reversed(recent_scores):
            if score.engagement_score < 40:
                consecutive_low_days += 1
            else:
                break
        
        # Get 30-day rolling average if available
        rolling_avg_30days = latest_score.rolling_avg_30days
        
        # Determine if declining
        is_declining = latest_score.engagement_trend == 'Declining'
        
        return {
            'session_score': latest_score.session_score,
            'engagement_volatility_7days': engagement_volatility_7days,
            'consecutive_low_days': consecutive_low_days,
            'engagement_score_lag_1day': latest_score.engagement_score_lag_1day,
            'engagement_score_lag_7days': latest_score.engagement_score_lag_7days,
            'rolling_avg_7days': latest_score.rolling_avg_7days,
            'rolling_avg_30days': rolling_avg_30days,
            'is_declining': is_declining,
            'assignment_score': latest_score.assignment_score,
            'interaction_score': latest_score.interaction_score,
            'forum_score': latest_score.forum_score,
            'login_score': latest_score.login_score,
            'engagement_score': latest_score.engagement_score,
            'engagement_level': latest_score.engagement_level
        }
    
    def calculate_session_length(
        self,
        session_score: float,
        volatility: float,
        consecutive_low_days: int
    ) -> int:
        """
        Algorithm 1: Session Length Personalization
        
        Logic:
        - High volatility + low session score → short, frequent blocks (20 min × 3)
        - Low volatility + high session score → longer deep-focus blocks (45 min × 1)
        
        Returns:
            Session length in minutes
        """
        # Base session length from session score
        # Higher session score = can handle longer sessions
        base_length = self.MIN_SESSION_LENGTH + (
            (session_score / 100.0) * (self.MAX_SESSION_LENGTH - self.MIN_SESSION_LENGTH)
        )
        
        # Adjust for volatility
        # High volatility = shorter sessions (student can't maintain focus)
        volatility_factor = 1.0 - (min(volatility / 30.0, 0.4))  # Max 40% reduction
        
        # Adjust for consecutive low days
        # Many low days = reduce session length (burnout prevention)
        if consecutive_low_days >= 3:
            consecutive_factor = 0.7  # 30% reduction
        elif consecutive_low_days >= 2:
            consecutive_factor = 0.85  # 15% reduction
        else:
            consecutive_factor = 1.0
        
        # Calculate final session length
        final_length = base_length * volatility_factor * consecutive_factor
        
        # Round to nearest 5 minutes and clamp to valid range
        final_length = round(final_length / 5) * 5
        final_length = max(self.MIN_SESSION_LENGTH, min(self.MAX_SESSION_LENGTH, final_length))
        
        return int(final_length)
    
    def calculate_sessions_per_day(
        self,
        session_length: int,
        session_score: float,
        volatility: float
    ) -> int:
        """
        Calculate number of sessions per day based on session length and engagement
        
        Logic:
        - Shorter sessions → more sessions per day
        - Longer sessions → fewer sessions per day
        - High volatility → more frequent, shorter sessions
        """
        # Target daily study time (in minutes)
        if volatility > 20:  # High volatility
            target_daily_minutes = 60  # 1 hour total
        elif session_score > 70:  # High session score
            target_daily_minutes = 90  # 1.5 hours total
        else:
            target_daily_minutes = 75  # 1.25 hours total
        
        # Calculate sessions needed
        sessions = max(1, round(target_daily_minutes / session_length))
        
        # Clamp to valid range
        sessions = max(self.MIN_SESSIONS_PER_DAY, min(self.MAX_SESSIONS_PER_DAY, sessions))
        
        return sessions
    
    def predict_low_engagement_days(
        self,
        engagement_score_lag_1day: Optional[float],
        rolling_avg_7days: Optional[float],
        is_declining: bool
    ) -> List[bool]:
        """
        Algorithm 2: Time-of-Day Scheduling (Implicit)
        
        Predicts which days in the next week will have low engagement
        
        Returns:
            List of 7 booleans (True = low engagement day)
        """
        predictions = []
        
        # If engagement dropped after previous day → predict low engagement tomorrow
        if engagement_score_lag_1day and rolling_avg_7days:
            if engagement_score_lag_1day < rolling_avg_7days - 5:  # Drop of 5+ points
                # Predict low engagement for next 2-3 days
                predictions = [True, True, False, False, False, False, False]
            elif is_declining:
                # Declining trend → predict low engagement later in week
                predictions = [False, False, False, True, True, False, False]
            else:
                # Stable or improving
                predictions = [False] * 7
        else:
            # Default: no low engagement days predicted
            predictions = [False] * 7
        
        return predictions
    
    def calculate_course_effort_rebalancing(
        self,
        assignment_score: float,
        interaction_score: float,
        forum_score: float,
        login_score: float
    ) -> Dict[str, int]:
        """
        Algorithm 3: Course Effort Rebalancing
        
        Logic:
        - Low assignment + high login → avoidance behavior
        - Schedule assignment micro-slots earlier in the week
        
        Returns:
            Dict with task distribution across week
        """
        # Detect avoidance behavior
        is_avoiding_assignments = (
            assignment_score < 40 and 
            login_score > 50  # Logs in but doesn't do assignments
        )
        
        # Detect low interaction
        needs_more_interaction = interaction_score < 30
        
        # Detect low forum participation
        needs_forum_engagement = forum_score < 25
        
        # Calculate task distribution
        # Days: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
        task_distribution = {
            'assignment_prep_minutes': [0] * 7,
            'quiz_interaction_minutes': [0] * 7,
            'forum_engagement_minutes': [0] * 7
        }
        
        if is_avoiding_assignments:
            # Schedule assignment prep early in week (Mon-Wed)
            task_distribution['assignment_prep_minutes'][0] = 15  # Monday
            task_distribution['assignment_prep_minutes'][1] = 15  # Tuesday
            task_distribution['assignment_prep_minutes'][2] = 10  # Wednesday
        
        if needs_more_interaction:
            # Schedule quizzes/interactions later in week (Thu-Fri)
            task_distribution['quiz_interaction_minutes'][3] = 20  # Thursday
            task_distribution['quiz_interaction_minutes'][4] = 20  # Friday
        
        if needs_forum_engagement:
            # Schedule forum engagement mid-week
            task_distribution['forum_engagement_minutes'][2] = 15  # Wednesday
            task_distribution['forum_engagement_minutes'][3] = 10  # Thursday
        
        return task_distribution
    
    def calculate_load_reduction(
        self,
        is_declining: bool,
        engagement_score_lag_7days: Optional[float],
        rolling_avg_30days: Optional[float]
    ) -> float:
        """
        Algorithm 4: Decline-Aware Load Reduction
        
        Logic:
        - If short-term decline but long-term average is okay → burnout risk
        - Reduce study load without stopping learning
        
        Returns:
            Load reduction factor (0.3 to 1.0)
        """
        if not is_declining:
            return 1.0  # No reduction needed
        
        # Check if it's a temporary decline or long-term issue
        if engagement_score_lag_7days and rolling_avg_30days:
            # If 7-day score is much lower than 30-day average → temporary burnout
            decline_magnitude = rolling_avg_30days - engagement_score_lag_7days
            
            if decline_magnitude > 20:  # Significant decline
                return 0.5  # 50% reduction
            elif decline_magnitude > 10:  # Moderate decline
                return 0.7  # 30% reduction
            else:
                return 0.85  # 15% reduction
        
        # Default reduction for declining trend
        return 0.75  # 25% reduction
    
    def generate_weekly_schedule(
        self,
        student_id: str,
        week_start_date: Optional[date] = None
    ) -> StudySchedule:
        """
        Generate a complete weekly study schedule
        
        Args:
            student_id: Student ID
            week_start_date: Start date of the week (defaults to next Monday)
        
        Returns:
            StudySchedule object
        """
        # Get engagement features
        features = self.get_engagement_features(student_id)
        
        # Calculate session length (Algorithm 1)
        session_length = self.calculate_session_length(
            features['session_score'],
            features['engagement_volatility_7days'],
            features['consecutive_low_days']
        )
        
        # Calculate sessions per day
        sessions_per_day = self.calculate_sessions_per_day(
            session_length,
            features['session_score'],
            features['engagement_volatility_7days']
        )
        
        # Calculate load reduction (Algorithm 4)
        load_reduction = self.calculate_load_reduction(
            features['is_declining'],
            features['engagement_score_lag_7days'],
            features['rolling_avg_30days']
        )
        
        # Predict low engagement days (Algorithm 2)
        low_engagement_days = self.predict_low_engagement_days(
            features['engagement_score_lag_1day'],
            features['rolling_avg_7days'],
            features['is_declining']
        )
        
        # Calculate course effort rebalancing (Algorithm 3)
        task_distribution = self.calculate_course_effort_rebalancing(
            features['assignment_score'],
            features['interaction_score'],
            features['forum_score'],
            features['login_score']
        )
        
        # Determine week dates
        if week_start_date is None:
            # Default to next Monday
            today = date.today()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7  # If today is Monday, use next Monday
            week_start_date = today + timedelta(days=days_until_monday)
        
        week_end_date = week_start_date + timedelta(days=6)
        
        # Generate daily schedules
        daily_schedules = []
        for day_offset in range(7):
            day_date = week_start_date + timedelta(days=day_offset)
            is_light_day = low_engagement_days[day_offset]
            
            # Calculate daily study time (with load reduction if declining)
            base_daily_minutes = session_length * sessions_per_day
            if is_light_day:
                daily_minutes = int(base_daily_minutes * 0.7)  # 30% reduction for light days
            else:
                daily_minutes = int(base_daily_minutes * load_reduction)
            
            # Get task-specific minutes for this day
            day_index = day_offset
            assignment_minutes = task_distribution['assignment_prep_minutes'][day_index]
            quiz_minutes = task_distribution['quiz_interaction_minutes'][day_index]
            forum_minutes = task_distribution['forum_engagement_minutes'][day_index]
            
            # Remaining time for general study
            general_study_minutes = max(0, daily_minutes - assignment_minutes - quiz_minutes - forum_minutes)
            
            # Calculate actual session duration for this day (may be reduced due to load reduction)
            # Distribute daily_minutes across sessions, handling remainder
            base_session_duration = daily_minutes // sessions_per_day if sessions_per_day > 0 else daily_minutes
            remainder = daily_minutes % sessions_per_day if sessions_per_day > 0 else 0
            
            # Create sessions with distributed durations (add remainder to first sessions)
            sessions = []
            for i in range(sessions_per_day):
                # Add 1 minute to first 'remainder' sessions to account for rounding
                session_duration = base_session_duration + (1 if i < remainder else 0)
                sessions.append({
                    'session_number': i + 1,
                    'duration_minutes': session_duration,
                    'task_type': self._determine_task_type(
                        day_index, assignment_minutes, quiz_minutes, forum_minutes, i
                    ),
                    'suggested_time': self._suggest_time_of_day(i, sessions_per_day)
                })
            
            # Create daily schedule
            daily_schedule = {
                'date': day_date.isoformat(),
                'day_name': day_date.strftime('%A'),
                'is_light_day': is_light_day,
                'total_minutes': daily_minutes,
                'sessions': sessions,
                'task_breakdown': {
                    'assignment_prep_minutes': assignment_minutes,
                    'quiz_interaction_minutes': quiz_minutes,
                    'forum_engagement_minutes': forum_minutes,
                    'general_study_minutes': general_study_minutes
                }
            }
            daily_schedules.append(daily_schedule)
        
        # Calculate total study minutes per day (average)
        total_study_minutes_per_day = int(sum(d['total_minutes'] for d in daily_schedules) / 7)
        
        # Create schedule object
        schedule = StudySchedule(
            student_id=student_id,
            week_start_date=week_start_date,
            week_end_date=week_end_date,
            session_length_minutes=session_length,
            sessions_per_day=sessions_per_day,
            total_study_minutes_per_day=total_study_minutes_per_day,
            load_reduction_factor=load_reduction,
            is_light_day=any(low_engagement_days),
            features_used=features,
            daily_schedules=daily_schedules,
            generation_method='engagement_based',
            version='v1.0'
        )
        
        return schedule
    
    def _determine_task_type(
        self,
        day_index: int,
        assignment_minutes: int,
        quiz_minutes: int,
        forum_minutes: int,
        session_index: int
    ) -> str:
        """Determine the task type for a session"""
        # Prioritize assignment prep in early sessions
        if assignment_minutes > 0 and session_index == 0:
            return 'assignment_prep'
        elif quiz_minutes > 0 and session_index >= 1:
            return 'quiz_interaction'
        elif forum_minutes > 0 and session_index >= 1:
            return 'forum_engagement'
        else:
            return 'general_study'
    
    def _suggest_time_of_day(self, session_index: int, total_sessions: int) -> str:
        """Suggest time of day for a session"""
        if total_sessions == 1:
            return 'Morning (9:00 AM - 11:00 AM)'
        elif total_sessions == 2:
            if session_index == 0:
                return 'Morning (9:00 AM - 11:00 AM)'
            else:
                return 'Afternoon (2:00 PM - 4:00 PM)'
        elif total_sessions == 3:
            if session_index == 0:
                return 'Morning (9:00 AM - 11:00 AM)'
            elif session_index == 1:
                return 'Afternoon (2:00 PM - 4:00 PM)'
            else:
                return 'Evening (7:00 PM - 9:00 PM)'
        else:
            # 4+ sessions: distribute evenly
            times = [
                'Early Morning (7:00 AM - 9:00 AM)',
                'Morning (9:00 AM - 11:00 AM)',
                'Afternoon (2:00 PM - 4:00 PM)',
                'Evening (7:00 PM - 9:00 PM)'
            ]
            return times[min(session_index, len(times) - 1)]
    
    def save_schedule(self, schedule: StudySchedule) -> StudySchedule:
        """Save schedule to database"""
        # Check if schedule already exists for this week
        existing = self.db.query(StudySchedule).filter(
            StudySchedule.student_id == schedule.student_id,
            StudySchedule.week_start_date == schedule.week_start_date
        ).first()
        
        if existing:
            # Update existing schedule
            existing.session_length_minutes = schedule.session_length_minutes
            existing.sessions_per_day = schedule.sessions_per_day
            existing.total_study_minutes_per_day = schedule.total_study_minutes_per_day
            existing.load_reduction_factor = schedule.load_reduction_factor
            existing.is_light_day = schedule.is_light_day
            existing.features_used = schedule.features_used
            existing.daily_schedules = schedule.daily_schedules
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new schedule
            self.db.add(schedule)
            self.db.commit()
            self.db.refresh(schedule)
            return schedule
    
    def get_student_schedule(
        self,
        student_id: str,
        week_start_date: Optional[date] = None
    ) -> Optional[StudySchedule]:
        """Get existing schedule for a student"""
        if week_start_date is None:
            # If no specific week provided, get the most recent schedule
            schedule = self.db.query(StudySchedule).filter(
                StudySchedule.student_id == student_id
            ).order_by(desc(StudySchedule.week_start_date)).first()
        else:
            # Get schedule for specific week
            schedule = self.db.query(StudySchedule).filter(
                StudySchedule.student_id == student_id,
                StudySchedule.week_start_date == week_start_date
            ).first()
        
        return schedule

