"""
Train Disengagement Prediction Model

This script:
1. Loads engagement scores from database
2. Engineers ML features
3. Trains Gradient Boosting Classifier
4. Evaluates model performance
5. Generates predictions for all students
6. Saves predictions to database
"""
import sys
import os
from datetime import datetime
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text

# Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    roc_curve, accuracy_score
)

# Database
from app.core.database import SessionLocal
from app.models import EngagementScore, DisengagementPrediction


class DisengagementPredictor:
    """Train and deploy disengagement prediction model"""
    
    AT_RISK_THRESHOLD = 30  # Engagement score below this = at risk
    
    RISK_THRESHOLDS = {
        'high': 0.7,    # Probability >= 0.7 = High risk
        'medium': 0.4,  # 0.4 - 0.69 = Medium risk
        'low': 0.0      # < 0.4 = Low risk
    }
    
    def __init__(self, db):
        self.db = db
        self.model = None
        self.feature_columns = None
        self.feature_importance = None
    
    def load_data(self) -> pd.DataFrame:
        """Load engagement scores from database"""
        print("\n📥 Loading engagement data from database...")
        
        query = text("""
            SELECT 
                student_id,
                date,
                login_score,
                session_score,
                interaction_score,
                forum_score,
                assignment_score,
                engagement_score,
                engagement_level,
                engagement_score_lag_1day,
                engagement_score_lag_7days,
                engagement_change,
                engagement_trend,
                rolling_avg_7days,
                rolling_avg_30days
            FROM engagement_scores
            ORDER BY student_id, date
        """)
        
        df = pd.read_sql(query, self.db.bind)
        
        print(f"✅ Loaded {len(df)} records")
        print(f"   Students: {df['student_id'].nunique()}")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer additional features for ML"""
        print("\n🔧 Engineering features...")
        
        df = df.sort_values(['student_id', 'date'])
        
        # Additional lag features
        df['engagement_score_lag_3days'] = df.groupby('student_id')['engagement_score'].shift(3)
        df['engagement_score_lag_14days'] = df.groupby('student_id')['engagement_score'].shift(14)
        
        # Volatility (standard deviation of recent scores)
        df['engagement_volatility_7days'] = df.groupby('student_id')['engagement_score'].transform(
            lambda x: x.rolling(window=7, min_periods=1).std()
        )
        
        # Cumulative features
        df['days_since_start'] = df.groupby('student_id').cumcount() + 1
        df['cumulative_avg_score'] = df.groupby('student_id')['engagement_score'].expanding().mean().reset_index(level=0, drop=True)
        
        # Trend indicators
        df['is_declining'] = (df['engagement_trend'] == 'Declining').astype(int)
        df['is_improving'] = (df['engagement_trend'] == 'Improving').astype(int)
        df['is_stable'] = (df['engagement_trend'] == 'Stable').astype(int)
        
        # Component score ratios
        df['login_to_session_ratio'] = df['login_score'] / (df['session_score'] + 1)
        df['interaction_to_forum_ratio'] = df['interaction_score'] / (df['forum_score'] + 1)
        
        # Consecutive low engagement days
        df['low_engagement'] = (df['engagement_score'] < 40).astype(int)
        df['consecutive_low_days'] = df.groupby('student_id')['low_engagement'].transform(
            lambda x: x.groupby((x != x.shift()).cumsum()).cumsum()
        )
        
        print(f"✅ Feature engineering complete - {df.shape[1]} total columns")
        
        return df
    
    def prepare_ml_data(self, df: pd.DataFrame):
        """Prepare data for machine learning"""
        print("\n🎯 Preparing ML dataset...")
        
        # Define target variable
        df['at_risk'] = (df['engagement_score'] < self.AT_RISK_THRESHOLD).astype(int)
        
        # Select features
        self.feature_columns = [
            # Component scores
            'login_score', 'session_score', 'interaction_score', 'forum_score', 'assignment_score',
            
            # Engagement metrics
            'engagement_score', 'engagement_score_lag_1day', 'engagement_score_lag_7days',
            'engagement_score_lag_3days', 'engagement_score_lag_14days',
            
            # Rolling averages
            'rolling_avg_7days', 'rolling_avg_30days',
            
            # Volatility & trends
            'engagement_volatility_7days', 'is_declining', 'is_improving',
            
            # Ratios & patterns
            'login_to_session_ratio', 'interaction_to_forum_ratio', 'consecutive_low_days',
            
            # Temporal
            'days_since_start', 'cumulative_avg_score'
        ]
        
        # Remove rows with NaN in critical features
        df_ml = df.dropna(subset=['engagement_score_lag_7days', 'rolling_avg_7days']).copy()
        
        print(f"✅ ML dataset prepared:")
        print(f"   Records: {len(df_ml)}")
        print(f"   Features: {len(self.feature_columns)}")
        print(f"   At-Risk Rate: {df_ml['at_risk'].mean()*100:.2f}%")
        
        # Prepare X and y
        X = df_ml[self.feature_columns].copy()
        y = df_ml['at_risk'].copy()
        
        # Handle any remaining NaN
        X = X.fillna(0)
        
        return X, y, df_ml
    
    def train_model(self, X_train, y_train):
        """Train Gradient Boosting Classifier"""
        print("\n🚀 Training Gradient Boosting Classifier...")
        
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            verbose=0
        )
        
        self.model.fit(X_train, y_train)
        
        # Store feature importance
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("✅ Model trained successfully!")
        
        return self.model
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        print(f"\n{'='*60}")
        print("MODEL EVALUATION")
        print(f"{'='*60}")
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\n✅ Accuracy: {accuracy*100:.2f}%")
        print(f"✅ ROC-AUC Score: {roc_auc:.4f}")
        
        print(f"\n📊 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Not At Risk', 'At Risk']))
        
        print(f"\n📋 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print(f"   True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
        print(f"   False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")
        
        print(f"\n🔍 Top 10 Most Important Features:")
        for i, row in self.feature_importance.head(10).iterrows():
            print(f"   {i+1}. {row['feature']}: {row['importance']:.4f}")
        
        return accuracy, roc_auc
    
    def categorize_risk(self, prob: float) -> str:
        """Categorize risk level based on probability"""
        if prob >= self.RISK_THRESHOLDS['high']:
            return 'High'
        elif prob >= self.RISK_THRESHOLDS['medium']:
            return 'Medium'
        else:
            return 'Low'
    
    def generate_predictions(self, X, df_ml):
        """Generate predictions for all students"""
        print(f"\n{'='*60}")
        print("GENERATING PREDICTIONS")
        print(f"{'='*60}")
        
        # Predict
        df_ml['at_risk_prediction'] = self.model.predict(X)
        df_ml['risk_probability'] = self.model.predict_proba(X)[:, 1]
        df_ml['risk_level'] = df_ml['risk_probability'].apply(self.categorize_risk)
        
        # Add metadata
        df_ml['model_version'] = 'v1.0_GradientBoosting'
        df_ml['model_type'] = 'GradientBoostingClassifier'
        df_ml['confidence_score'] = df_ml['risk_probability'].apply(
            lambda x: max(x, 1-x)
        )
        df_ml['prediction_horizon_days'] = 7
        df_ml['created_at'] = datetime.now()
        
        print(f"\n✅ Generated {len(df_ml)} predictions")
        print(f"\n📊 Risk Level Distribution:")
        for level in ['High', 'Medium', 'Low']:
            count = (df_ml['risk_level'] == level).sum()
            pct = (count / len(df_ml)) * 100
            print(f"   {level}: {count} ({pct:.1f}%)")
        
        # Top at-risk students
        print(f"\n⚠️  Top 10 Most At-Risk Students:")
        top_risk = df_ml.groupby('student_id').agg({
            'risk_probability': 'mean',
            'engagement_score': 'mean'
        }).sort_values('risk_probability', ascending=False).head(10)
        
        for student_id, row in top_risk.iterrows():
            print(f"   {student_id}: Risk={row['risk_probability']:.3f}, Eng={row['engagement_score']:.2f}")
        
        return df_ml
    
    def save_to_database(self, df_ml):
        """Save predictions to database"""
        print(f"\n{'='*60}")
        print("SAVING PREDICTIONS TO DATABASE")
        print(f"{'='*60}")
        
        try:
            # Clear existing predictions
            print("\n🗑️  Clearing existing predictions...")
            self.db.query(DisengagementPrediction).delete()
            self.db.commit()
            
            # Prepare data
            df_predictions = df_ml.copy()
            df_predictions['prediction_date'] = df_predictions['date']
            df_predictions['at_risk'] = df_predictions['at_risk_prediction']
            
            # Add feature importance
            top_features = self.feature_importance.head(5)[['feature', 'importance']].to_dict('records')
            df_predictions['feature_importance'] = [top_features] * len(df_predictions)
            
            # Contributing factors
            df_predictions['contributing_factors'] = df_predictions.apply(
                lambda row: {
                    'low_engagement_score': bool(row['engagement_score'] < 40),
                    'declining_trend': bool(row['is_declining'] == 1),
                    'low_session_activity': bool(row['session_score'] < 30),
                    'consecutive_low_days': int(row['consecutive_low_days'])
                }, axis=1
            )
            
            # Select columns for database
            db_columns = [
                'student_id', 'prediction_date', 'at_risk', 'risk_probability', 'risk_level',
                'contributing_factors', 'feature_importance', 'model_version', 'model_type',
                'confidence_score', 'prediction_horizon_days', 'created_at'
            ]
            
            df_to_save = df_predictions[db_columns].copy()
            
            # Convert to database records
            print(f"\n📝 Inserting {len(df_to_save)} prediction records...")
            
            records = []
            for _, row in df_to_save.iterrows():
                record = DisengagementPrediction(**row.to_dict())
                records.append(record)
            
            # Bulk insert
            self.db.bulk_save_objects(records)
            self.db.commit()
            
            # Verify
            count = self.db.query(DisengagementPrediction).count()
            high_risk_count = self.db.query(DisengagementPrediction).filter(
                DisengagementPrediction.risk_level == 'High'
            ).count()
            
            print(f"✅ Successfully saved {count} predictions")
            print(f"⚠️  High risk predictions: {high_risk_count}")
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error saving to database: {str(e)}")
            raise


def main():
    """Main execution"""
    print("\n" + "🎯" * 30)
    print("    DISENGAGEMENT PREDICTION MODEL TRAINING")
    print("🎯" * 30)
    
    db = SessionLocal()
    try:
        predictor = DisengagementPredictor(db)
        
        # Step 1: Load data
        df = predictor.load_data()
        
        # Step 2: Engineer features
        df = predictor.engineer_features(df)
        
        # Step 3: Prepare ML data
        X, y, df_ml = predictor.prepare_ml_data(df)
        
        # Step 4: Train-test split
        print("\n📊 Splitting data (80/20)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"   Training: {len(X_train)} samples")
        print(f"   Test: {len(X_test)} samples")
        
        # Step 5: Train model
        predictor.train_model(X_train, y_train)
        
        # Step 6: Evaluate model
        accuracy, roc_auc = predictor.evaluate_model(X_test, y_test)
        
        # Step 7: Generate predictions
        df_ml = predictor.generate_predictions(X, df_ml)
        
        # Step 8: Save to database
        predictor.save_to_database(df_ml)
        
        # Summary
        print(f"\n{'='*60}")
        print("✅ DISENGAGEMENT PREDICTION MODEL - COMPLETE!")
        print(f"{'='*60}")
        print(f"\n📊 Model Performance:")
        print(f"   - Accuracy: {accuracy*100:.2f}%")
        print(f"   - ROC-AUC: {roc_auc:.4f}")
        print(f"\n📈 Predictions Saved: {len(df_ml)}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

