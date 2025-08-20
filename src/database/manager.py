"""
Database manager for NAICS classification system
"""
from .models import db, CompanyProfile, ClassificationResult, AnalysisSession, NAICSCode
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import json

class DatabaseManager:
    def __init__(self, app=None):
        self.db = db
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize database with Flask app"""
        self.db.init_app(app)
        with app.app_context():
            self.db.create_all()
    
    # Company Profile methods
    def create_company_profile(self, company_data):
        """Create a new company profile"""
        profile = CompanyProfile(
            company_name=company_data.get('company_name'),
            domain=company_data.get('domain'),
            url=company_data.get('url'),
            description=company_data.get('description'),
            industry_keywords=json.dumps(company_data.get('industry_keywords', [])),
            primary_naics=company_data.get('primary_naics'),
            confidence_score=company_data.get('confidence_score', 0.0)
        )
        self.db.session.add(profile)
        self.db.session.commit()
        return profile
    
    def get_company_profile(self, company_id=None, domain=None):
        """Get company profile by ID or domain"""
        if company_id:
            return CompanyProfile.query.get(company_id)
        elif domain:
            return CompanyProfile.query.filter_by(domain=domain).first()
        return None
    
    def update_company_profile(self, company_id, update_data):
        """Update company profile"""
        profile = CompanyProfile.query.get(company_id)
        if profile:
            for key, value in update_data.items():
                if hasattr(profile, key):
                    if key == 'industry_keywords' and isinstance(value, list):
                        setattr(profile, key, json.dumps(value))
                    else:
                        setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()
            self.db.session.commit()
        return profile
    
    def search_companies(self, query, limit=50):
        """Search companies by name or domain"""
        return CompanyProfile.query.filter(
            or_(
                CompanyProfile.company_name.contains(query),
                CompanyProfile.domain.contains(query)
            )
        ).limit(limit).all()
    
    # Classification Result methods
    def save_classification_result(self, result_data):
        """Save classification result"""
        result = ClassificationResult(
            company_id=result_data.get('company_id'),
            session_id=result_data.get('session_id'),
            primary_naics=result_data.get('primary_naics'),
            secondary_naics=json.dumps(result_data.get('secondary_naics', [])),
            confidence_score=result_data.get('confidence_score', 0.0),
            classification_method=result_data.get('classification_method', 'ml_classifier'),
            extracted_keywords=json.dumps(result_data.get('extracted_keywords', [])),
            content_analysis=json.dumps(result_data.get('content_analysis', {}))
        )
        self.db.session.add(result)
        self.db.session.commit()
        return result
    
    def get_classification_results(self, company_id=None, session_id=None, limit=100):
        """Get classification results"""
        query = ClassificationResult.query
        
        if company_id:
            query = query.filter_by(company_id=company_id)
        if session_id:
            query = query.filter_by(session_id=session_id)
            
        return query.order_by(ClassificationResult.created_at.desc()).limit(limit).all()
    
    # Analysis Session methods
    def create_analysis_session(self, session_data):
        """Create analysis session"""
        session = AnalysisSession(
            session_name=session_data.get('session_name'),
            user_id=session_data.get('user_id'),
            batch_size=session_data.get('batch_size', 1),
            status=session_data.get('status', 'pending')
        )
        self.db.session.add(session)
        self.db.session.commit()
        return session
    
    def update_session_status(self, session_id, status, results_summary=None):
        """Update session status"""
        session = AnalysisSession.query.get(session_id)
        if session:
            session.status = status
            if status == 'completed':
                session.completed_at = datetime.utcnow()
            if results_summary:
                session.results_summary = json.dumps(results_summary)
            self.db.session.commit()
        return session
    
    def get_analysis_sessions(self, user_id=None, limit=50):
        """Get analysis sessions"""
        query = AnalysisSession.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.order_by(AnalysisSession.started_at.desc()).limit(limit).all()
    
    # NAICS Code methods
    def load_naics_codes(self, naics_data):
        """Load NAICS codes from data"""
        for code_data in naics_data:
            existing = NAICSCode.query.filter_by(code=code_data['code']).first()
            if not existing:
                naics_code = NAICSCode(
                    code=code_data['code'],
                    title=code_data['title'],
                    description=code_data.get('description'),
                    level=len(code_data['code']),
                    parent_code=code_data.get('parent_code'),
                    sector=code_data.get('sector'),
                    subsector=code_data.get('subsector'),
                    industry_group=code_data.get('industry_group'),
                    industry=code_data.get('industry'),
                    keywords=json.dumps(code_data.get('keywords', []))
                )
                self.db.session.add(naics_code)
        
        self.db.session.commit()
    
    def get_naics_code(self, code):
        """Get NAICS code by code"""
        return NAICSCode.query.filter_by(code=code).first()
    
    def search_naics_codes(self, query, limit=20):
        """Search NAICS codes"""
        return NAICSCode.query.filter(
            or_(
                NAICSCode.code.contains(query),
                NAICSCode.title.contains(query),
                NAICSCode.description.contains(query)
            )
        ).limit(limit).all()
    
    # Analytics methods
    def get_classification_stats(self, start_date=None, end_date=None):
        """Get classification statistics"""
        query = self.db.session.query(
            ClassificationResult.primary_naics,
            func.count(ClassificationResult.id).label('count'),
            func.avg(ClassificationResult.confidence_score).label('avg_confidence')
        )
        
        if start_date:
            query = query.filter(ClassificationResult.created_at >= start_date)
        if end_date:
            query = query.filter(ClassificationResult.created_at <= end_date)
        
        return query.group_by(ClassificationResult.primary_naics)\
                   .order_by(func.count(ClassificationResult.id).desc())\
                   .limit(20).all()
    
    def get_daily_activity(self, days=30):
        """Get daily classification activity"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.session.query(
            func.date(ClassificationResult.created_at).label('date'),
            func.count(ClassificationResult.id).label('classifications'),
            func.avg(ClassificationResult.confidence_score).label('avg_confidence')
        ).filter(
            ClassificationResult.created_at >= start_date
        ).group_by(
            func.date(ClassificationResult.created_at)
        ).order_by('date').all()

# Global instance
db_manager = DatabaseManager()
