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
            {"name": "Starbucks", "design_summary": "Standardized, corporate design with a focus on efficiency."},
            {"name": "Blue Bottle Coffee", "design_summary": "Minimalist, clean design with a focus on the coffee-making process."},
            {"name": "Peet's Coffee", "design_summary": "Traditional, dark wood design with a classic coffeehouse feel."}
        ],
        "trends": [
            {"name": "Minimalism", "summary": "Using simple, clean layouts with a lot of white space."},
            {"name": "Sustainable Design", "summary": "Using eco-friendly materials and themes."},
            {"name": "Hyper-local Aesthetics", "summary": "Incorporating design elements that reflect the local neighborhood and culture."}
        ]
    }
