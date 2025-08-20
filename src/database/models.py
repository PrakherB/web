"""
Database models for NAICS classification system
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    industry_keywords = db.Column(db.Text)  # JSON string
    primary_naics = db.Column(db.String(10))
    confidence_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classification_results = db.relationship('ClassificationResult', backref='company', lazy=True)
    
    def __repr__(self):
        return f'<CompanyProfile {self.company_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'domain': self.domain,
            'url': self.url,
            'description': self.description,
            'industry_keywords': json.loads(self.industry_keywords) if self.industry_keywords else [],
            'primary_naics': self.primary_naics,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ClassificationResult(db.Model):
    __tablename__ = 'classification_results'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('analysis_sessions.id'))
    primary_naics = db.Column(db.String(10), nullable=False)
    secondary_naics = db.Column(db.Text)  # JSON string
    confidence_score = db.Column(db.Float, nullable=False)
    classification_method = db.Column(db.String(50), default='ml_classifier')
    extracted_keywords = db.Column(db.Text)  # JSON string
    content_analysis = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClassificationResult {self.primary_naics}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'session_id': self.session_id,
            'primary_naics': self.primary_naics,
            'secondary_naics': json.loads(self.secondary_naics) if self.secondary_naics else [],
            'confidence_score': self.confidence_score,
            'classification_method': self.classification_method,
            'extracted_keywords': json.loads(self.extracted_keywords) if self.extracted_keywords else [],
            'content_analysis': json.loads(self.content_analysis) if self.content_analysis else {},
            'created_at': self.created_at.isoformat()
        }

class AnalysisSession(db.Model):
    __tablename__ = 'analysis_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(255))
    user_id = db.Column(db.String(100))
    batch_size = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    results_summary = db.Column(db.Text)  # JSON string
    
    # Relationships
    classification_results = db.relationship('ClassificationResult', backref='session', lazy=True)
    
    def __repr__(self):
        return f'<AnalysisSession {self.session_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_name': self.session_name,
            'user_id': self.user_id,
            'batch_size': self.batch_size,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'results_summary': json.loads(self.results_summary) if self.results_summary else {},
            'results_count': len(self.classification_results)
        }

class NAICSCode(db.Model):
    __tablename__ = 'naics_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.Integer, nullable=False)  # 2, 3, 4, 5, 6 digit levels
    parent_code = db.Column(db.String(10))
    sector = db.Column(db.String(100))
    subsector = db.Column(db.String(100))
    industry_group = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    keywords = db.Column(db.Text)  # JSON string of related keywords
    
    def __repr__(self):
        return f'<NAICSCode {self.code}: {self.title}>'
    
    def to_dict(self):
        return {
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'level': self.level,
            'parent_code': self.parent_code,
            'sector': self.sector,
            'subsector': self.subsector,
            'industry_group': self.industry_group,
            'industry': self.industry,
            'keywords': json.loads(self.keywords) if self.keywords else []
        }

class DesignSample(db.Model):
    __tablename__ = 'design_samples'

    id = db.Column(db.Integer, primary_key=True)
    website_url = db.Column(db.String(255), nullable=False)
    naics_code = db.Column(db.String(10))
    industry_name = db.Column(db.String(255))
    screenshot_url = db.Column(db.String(255))
    design_features = db.Column(db.JSON)
    color_palette = db.Column(db.JSON)
    typography_info = db.Column(db.JSON)
    layout_type = db.Column(db.String(100))
    mobile_responsive = db.Column(db.Boolean)
    performance_score = db.Column(db.Integer)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DesignSample {self.website_url}>'

    def to_dict(self):
        return {
            'id': self.id,
            'website_url': self.website_url,
            'naics_code': self.naics_code,
            'industry_name': self.industry_name,
            'screenshot_url': self.screenshot_url,
            'design_features': self.design_features,
            'color_palette': self.color_palette,
            'typography_info': self.typography_info,
            'layout_type': self.layout_type,
            'mobile_responsive': self.mobile_responsive,
            'performance_score': self.performance_score,
            'created_date': self.created_date.isoformat() if self.created_date else None,
        }
