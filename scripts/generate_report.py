import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reporting.generator import ReportBuilder, get_sample_data_for_prompt

def main():
    """
    Generates and prints a sample design report.
    """
    print("🚀 Generating a sample design report...")

    # Get sample data
    sample_data = get_sample_data_for_prompt()

    # Initialize the report builder
    report_builder = ReportBuilder()

    # Build the report
    report = report_builder.build(sample_data)

    # Print the report as a JSON object
    print("\n" + "="*50)
    print("Generated Report:")
    print("="*50)
    # The .model_dump_json() method is from Pydantic
    print(report.model_dump_json(indent=2))
    print("="*50)

if __name__ == "__main__":
    main()
