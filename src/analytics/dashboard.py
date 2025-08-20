"""
Dashboard analytics for NAICS classification system
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
from collections import Counter

from src.database.manager import db_manager
from src.database.models import ClassificationResult, CompanyProfile, AnalysisSession

class DashboardAnalytics:
    def __init__(self):
        self.db = db_manager
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """Get overview statistics for dashboard"""
        try:
            # Total counts
            total_companies = CompanyProfile.query.count()
            total_classifications = ClassificationResult.query.count()
            total_sessions = AnalysisSession.query.count()
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_classifications = ClassificationResult.query.filter(
                ClassificationResult.created_at >= thirty_days_ago
            ).count()
            
            # Average confidence score
            from sqlalchemy import func
            avg_confidence = self.db.db.session.query(
                func.avg(ClassificationResult.confidence_score)
            ).scalar() or 0.0
            
            # Top NAICS codes
            top_naics = self.get_top_naics_codes(limit=5)
            
            return {
                'total_companies': total_companies,
                'total_classifications': total_classifications,
                'total_sessions': total_sessions,
                'recent_classifications': recent_classifications,
                'average_confidence': round(avg_confidence, 3),
                'top_naics_codes': top_naics,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_classification_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get classification trends over time"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            daily_stats = self.db.get_daily_activity(days)
            
            # Format data for charts
            dates = []
            classifications = []
            avg_confidence = []
            
            for stat in daily_stats:
                dates.append(stat.date.isoformat())
                classifications.append(stat.classifications)
                avg_confidence.append(round(stat.avg_confidence or 0.0, 3))
            
            return {
                'period': f'{days} days',
                'dates': dates,
                'daily_classifications': classifications,
                'daily_avg_confidence': avg_confidence,
                'total_period_classifications': sum(classifications),
                'period_avg_confidence': round(sum(avg_confidence) / len(avg_confidence) if avg_confidence else 0, 3)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_top_naics_codes(self, limit: int = 20, days: int = None) -> List[Dict]:
        """Get top NAICS codes by classification count"""
        try:
            query = self.db.db.session.query(
                ClassificationResult.primary_naics,
                self.db.db.func.count(ClassificationResult.id).label('count'),
                self.db.db.func.avg(ClassificationResult.confidence_score).label('avg_confidence')
            )
            
            if days:
                start_date = datetime.utcnow() - timedelta(days=days)
                query = query.filter(ClassificationResult.created_at >= start_date)
            
            results = query.group_by(ClassificationResult.primary_naics)\
                          .order_by(self.db.db.func.count(ClassificationResult.id).desc())\
                          .limit(limit).all()
            
            # Get NAICS code details
            naics_data = []
            for result in results:
                naics_info = self.db.get_naics_code(result.primary_naics)
                naics_data.append({
                    'code': result.primary_naics,
                    'title': naics_info.title if naics_info else 'Unknown',
                    'count': result.count,
                    'avg_confidence': round(result.avg_confidence or 0.0, 3),
                    'percentage': 0  # Will be calculated below
                })
            
            # Calculate percentages
            total_count = sum(item['count'] for item in naics_data)
            for item in naics_data:
                item['percentage'] = round((item['count'] / total_count * 100) if total_count > 0 else 0, 1)
            
            return naics_data
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_confidence_distribution(self) -> Dict[str, Any]:
        """Get confidence score distribution"""
        try:
            confidence_scores = self.db.db.session.query(
                ClassificationResult.confidence_score
            ).all()
            
            scores = [score[0] for score in confidence_scores if score is not None]
            
            # Create distribution buckets
            buckets = {
                '0.0-0.2': 0,
                '0.2-0.4': 0,
                '0.4-0.6': 0,
                '0.6-0.8': 0,
                '0.8-1.0': 0
            }
            
            for score in scores:
                if score < 0.2:
                    buckets['0.0-0.2'] += 1
                elif score < 0.4:
                    buckets['0.2-0.4'] += 1
                elif score < 0.6:
                    buckets['0.4-0.6'] += 1
                elif score < 0.8:
                    buckets['0.6-0.8'] += 1
                else:
                    buckets['0.8-1.0'] += 1
            
            total = len(scores)
            distribution = []
            for bucket, count in buckets.items():
                distribution.append({
                    'range': bucket,
                    'count': count,
                    'percentage': round((count / total * 100) if total > 0 else 0, 1)
                })
            
            return {
                'distribution': distribution,
                'total_classifications': total,
                'average_confidence': round(sum(scores) / len(scores) if scores else 0, 3),
                'median_confidence': round(sorted(scores)[len(scores)//2] if scores else 0, 3)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_session_analytics(self, limit: int = 10) -> Dict[str, Any]:
        """Get analytics for analysis sessions"""
        try:
            # Recent sessions
            recent_sessions = AnalysisSession.query\
                .order_by(AnalysisSession.started_at.desc())\
                .limit(limit).all()
            
            sessions_data = []
            for session in recent_sessions:
                session_dict = session.to_dict()
                
                # Add success rate
                if session.classification_results:
                    successful = len([r for r in session.classification_results 
                                    if r.confidence_score >= 0.5])  # Assuming 0.5 as success threshold
                    session_dict['success_rate'] = round(
                        (successful / len(session.classification_results) * 100), 1
                    )
                else:
                    session_dict['success_rate'] = 0.0
                
                sessions_data.append(session_dict)
            
            # Session statistics
            total_sessions = AnalysisSession.query.count()
            completed_sessions = AnalysisSession.query.filter_by(status='completed').count()
            failed_sessions = AnalysisSession.query.filter_by(status='failed').count()
            
            return {
                'recent_sessions': sessions_data,
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'failed_sessions': failed_sessions,
                'completion_rate': round((completed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 1)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_industry_analysis(self) -> Dict[str, Any]:
        """Get industry sector analysis"""
        try:
            # Get all classifications with NAICS info
            results = self.db.db.session.query(
                ClassificationResult.primary_naics,
                self.db.db.func.count(ClassificationResult.id).label('count'),
                self.db.db.func.avg(ClassificationResult.confidence_score).label('avg_confidence')
            ).group_by(ClassificationResult.primary_naics).all()
            
            # Group by sector (first 2 digits of NAICS code)
            sectors = {}
            for result in results:
                if result.primary_naics and len(result.primary_naics) >= 2:
                    sector_code = result.primary_naics[:2]
                    if sector_code not in sectors:
                        sectors[sector_code] = {
                            'code': sector_code,
                            'count': 0,
                            'confidence_sum': 0,
                            'industries': []
                        }
                    
                    sectors[sector_code]['count'] += result.count
                    sectors[sector_code]['confidence_sum'] += (result.avg_confidence or 0) * result.count
                    sectors[sector_code]['industries'].append({
                        'naics': result.primary_naics,
                        'count': result.count,
                        'confidence': round(result.avg_confidence or 0, 3)
                    })
            
            # Calculate sector averages and get names
            sector_analysis = []
            for sector_code, data in sectors.items():
                avg_confidence = data['confidence_sum'] / data['count'] if data['count'] > 0 else 0
                
                # Get sector name from NAICS data (you might want to create a mapping)
                sector_name = self._get_sector_name(sector_code)
                
                sector_analysis.append({
                    'sector_code': sector_code,
                    'sector_name': sector_name,
                    'total_classifications': data['count'],
                    'avg_confidence': round(avg_confidence, 3),
                    'top_industries': sorted(data['industries'], 
                                           key=lambda x: x['count'], reverse=True)[:5]
                })
            
            # Sort by classification count
            sector_analysis.sort(key=lambda x: x['total_classifications'], reverse=True)
            
            return {
                'sectors': sector_analysis[:20],  # Top 20 sectors
                'total_sectors': len(sector_analysis)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_sector_name(self, sector_code: str) -> str:
        """Get sector name from code"""
        # This is a simplified mapping - you should use your NAICS data
        sector_names = {
            '11': 'Agriculture, Forestry, Fishing and Hunting',
            '21': 'Mining, Quarrying, and Oil and Gas Extraction',
            '22': 'Utilities',
            '23': 'Construction',
            '31': 'Manufacturing',
            '32': 'Manufacturing',
            '33': 'Manufacturing',
            '42': 'Wholesale Trade',
            '44': 'Retail Trade',
            '45': 'Retail Trade',
            '48': 'Transportation and Warehousing',
            '49': 'Transportation and Warehousing',
            '51': 'Information',
            '52': 'Finance and Insurance',
            '53': 'Real Estate and Rental and Leasing',
            '54': 'Professional, Scientific, and Technical Services',
            '55': 'Management of Companies and Enterprises',
            '56': 'Administrative and Support and Waste Management',
            '61': 'Educational Services',
            '62': 'Health Care and Social Assistance',
            '71': 'Arts, Entertainment, and Recreation',
            '72': 'Accommodation and Food Services',
            '81': 'Other Services',
            '92': 'Public Administration'
        }
        
        return sector_names.get(sector_code, f'Sector {sector_code}')

# Global instance
dashboard_analytics = DashboardAnalytics()
