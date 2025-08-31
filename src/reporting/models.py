from pydantic import BaseModel
from typing import List, Optional

class ExecutiveSummary(BaseModel):
    industry_classification_confidence: float
    key_design_opportunities: List[str]
    trend_alignment_score: float

class IndustryAnalysis(BaseModel):
    naics_code: str
    description: str
    industry_specific_design_patterns: List[str]
    competitive_landscape_overview: str

class CompetitorAnalysis(BaseModel):
    name: str
    design_summary: str
    competitor_url: str
    screenshot_url: str
    design_pattern_analysis: str
    strengths: List[str]
    improvement_opportunities: List[str]

class TrendIntegration(BaseModel):
    trend_name: str
    industry_application_examples: List[str]
    implementation_difficulty_score: int

class CustomRecommendation(BaseModel):
    suggestion: str
    priority_ranking: int
    rationale: str
    implementation_complexity: str

class ActionPlan(BaseModel):
    quick_wins: List[str]
    medium_term_improvements: List[str]
    long_term_strategic_changes: List[str]

class DesignReport(BaseModel):
    executive_summary: ExecutiveSummary
    industry_analysis: IndustryAnalysis
    competitor_design_analysis: List[CompetitorAnalysis]
    trend_integration: List[TrendIntegration]
    custom_recommendations: List[CustomRecommendation]
    action_plan: ActionPlan
