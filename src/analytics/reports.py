"""
Report generation utilities for NAICS classification analytics.
"""
import os
import json
from datetime import datetime
from pathlib import Path

from src.analytics.dashboard import dashboard_analytics  # Use our existing dashboard analytics


class ReportGenerator:
    def __init__(self, output_dir: str = "data/reports"):
        self.output_path = Path(output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def generate_overview_report(self, filename: str = None) -> str:
        """
        Generate and save a JSON overview analytics report.
        Returns the filepath.
        """
        overview = dashboard_analytics.get_overview_stats()
        trends = dashboard_analytics.get_classification_trends()
        confidence_dist = dashboard_analytics.get_confidence_distribution()

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "overview": overview,
            "trends": trends,
            "confidence_distribution": confidence_dist
        }

        if not filename:
            filename = f"naics_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.output_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return str(filepath)

    def generate_sector_report(self, filename: str = None) -> str:
        """
        Generate & save more detailed sector/industry analysis.
        """
        sector_analysis = dashboard_analytics.get_industry_analysis()
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "sector_analysis": sector_analysis
        }
        if not filename:
            filename = f"naics_sector_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        return str(filepath)
