import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reporting.generator import ReportPromptGenerator, get_sample_data_for_prompt

def main():
    """
    Generates and prints a sample report prompt.
    """
    print("🚀 Generating a sample report prompt...")

    # Get sample data
    sample_data = get_sample_data_for_prompt()

    # Initialize the prompt generator
    prompt_generator = ReportPromptGenerator()

    # Generate the prompt
    prompt = prompt_generator.generate_prompt(**sample_data)

    # Print the prompt
    print("\n" + "="*50)
    print("Generated Prompt:")
    print("="*50)
    print(prompt)
    print("="*50)

if __name__ == "__main__":
    main()
