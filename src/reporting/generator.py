from .models import (
    ExecutiveSummary,
    IndustryAnalysis,
    CompetitorAnalysis,
    TrendIntegration,
    CustomRecommendation,
    ActionPlan,
    DesignReport,
)

class ReportBuilder:
    """
    Assembles the final design report from various data components.
    """
    def build(self, data: dict) -> DesignReport:
        """
        Builds the report from a dictionary of data.
        """
        # For now, we use placeholder data for many sections
        executive_summary = ExecutiveSummary(
            industry_classification_confidence=data.get('classification_confidence', 0.95),
            key_design_opportunities=["Opportunity 1", "Opportunity 2"],
            trend_alignment_score=0.8
        )

        industry_analysis = IndustryAnalysis(
            naics_code=data.get('naics_code', '000000'),
            description=data.get('industry_description', 'N/A'),
            industry_specific_design_patterns=["Pattern 1", "Pattern 2"],
            competitive_landscape_overview="A competitive market with several key players."
        )

        competitor_analysis = [
            CompetitorAnalysis(**comp) for comp in data.get('competitors', [])
        ]

        trend_integration = [
            TrendIntegration(
                trend_name=trend['name'],
                industry_application_examples=["Example 1"],
                implementation_difficulty_score=3
            ) for trend in data.get('trends', [])
        ]

        custom_recommendations = [
            CustomRecommendation(**rec) for rec in data.get('custom_recommendations', [])
        ]

        action_plan = ActionPlan(
            quick_wins=["Update hero image"],
            medium_term_improvements=["Redesign services page"],
            long_term_strategic_changes=["Implement a full design system"]
        )

        return DesignReport(
            executive_summary=executive_summary,
            industry_analysis=industry_analysis,
            competitor_design_analysis=competitor_analysis,
            trend_integration=trend_integration,
            custom_recommendations=custom_recommendations,
            action_plan=action_plan
        )

class ReportPromptGenerator:
    """
    Generates a detailed prompt for the AI content synthesis engine.
    """
    def __init__(self, template: str = None):
        if template:
            self.template = template
        else:
            self.template = self._get_default_template()

    def _get_default_template(self) -> str:
        """
        Returns the default prompt template.
        """
        return """
You are a senior web design consultant specializing in {INDUSTRY}.

Context:
- Business: {BUSINESS_DESCRIPTION}
- Industry: {NAICS_CODE} - {INDUSTRY_NAME}
- Competitors:
{COMPETITOR_DESIGNS}
- Current Trends:
{RELEVANT_TRENDS}

Task: Generate 5 specific, actionable design recommendations that:
1. Align with current 2025 design trends
2. Are appropriate for the {INDUSTRY} sector
3. Differentiate from direct competitors
4. Consider the business's unique value proposition

Output Format: {STRUCTURED_JSON_SCHEMA}
"""

    def _format_competitors(self, competitors: list) -> str:
        """
        Formats the list of competitor designs.
        """
        if not competitors:
            return "No competitor data available."

        formatted_list = []
        for i, competitor in enumerate(competitors, 1):
            formatted_list.append(f"  {i}. {competitor['name']}: {competitor['design_summary']}")
        return "\n".join(formatted_list)

    def _format_trends(self, trends: list) -> str:
        """
        Formats the list of relevant trends.
        """
        if not trends:
            return "No trend data available."

        formatted_list = []
        for i, trend in enumerate(trends, 1):
            formatted_list.append(f"  {i}. {trend['name']}: {trend['summary']}")
        return "\n".join(formatted_list)

    def generate_prompt(
        self,
        industry_name: str,
        business_description: str,
        naics_code: str,
        competitors: list,
        trends: list,
        output_format: str = "A JSON object with a single key 'recommendations' which contains a list of strings."
    ) -> str:
        """
        Generates a prompt from structured data.
        """

        competitor_str = self._format_competitors(competitors)
        trends_str = self._format_trends(trends)

        return self.template.format(
            INDUSTRY=industry_name,
            BUSINESS_DESCRIPTION=business_description,
            NAICS_CODE=naics_code,
            INDUSTRY_NAME=industry_name,
            COMPETITOR_DESIGNS=competitor_str,
            RELEVANT_TRENDS=trends_str,
            STRUCTURED_JSON_SCHEMA=output_format
        )

def get_sample_data_for_prompt():
    """
    Returns a sample dictionary of data for generating a prompt.
    """
    return {
        "industry_name": "Coffee Shops",
        "business_description": "A local coffee shop focused on high-quality, ethically sourced beans and a cozy atmosphere.",
        "naics_code": "722515",
        "competitors": [
            {
                "name": "Starbucks",
                "design_summary": "Standardized, corporate design with a focus on efficiency.",
                "competitor_url": "https://starbucks.com",
                "screenshot_url": "https://example.com/screenshot_starbucks.jpg",
                "design_pattern_analysis": "Grid-based layout with clear calls to action.",
                "strengths": ["Strong brand recognition", "Efficient ordering process"],
                "improvement_opportunities": ["Lacks unique personality", "Can feel impersonal"]
            },
            {
                "name": "Blue Bottle Coffee",
                "design_summary": "Minimalist, clean design with a focus on the coffee-making process.",
                "competitor_url": "https://bluebottlecoffee.com",
                "screenshot_url": "https://example.com/screenshot_bluebottle.jpg",
                "design_pattern_analysis": "Asymmetrical layout with high-quality photography.",
                "strengths": ["Aesthetic appeal", "Focus on quality"],
                "improvement_opportunities": ["Navigation could be clearer", "Less content density"]
            }
        ],
        "trends": [
            {"name": "Minimalism", "summary": "Using simple, clean layouts with a lot of white space."},
            {"name": "Sustainable Design", "summary": "Using eco-friendly materials and themes."},
            {"name": "Hyper-local Aesthetics", "summary": "Incorporating design elements that reflect the local neighborhood and culture."}
        ]
    }
