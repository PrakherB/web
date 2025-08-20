#!/usr/bin/env python3
"""
Enhanced website analysis script with command line support
Usage: 
  python scripts/run_analysis.py https://example.com
  python scripts/run_analysis.py starbucks.com
  python scripts/run_analysis.py  # Will prompt for input
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    print("🎯 Website Analysis Tool")
    print("=" * 40)
    
    # Get URL from command line or prompt user
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"🔗 Analyzing URL: {url}")
    else:
        print("💡 Tip: Run 'python scripts/run_analysis.py <url>' for direct analysis")
        print("-" * 40)
        url = input("🔗 Enter website URL: ").strip()
    
    if not url:
        print("❌ No URL provided")
        print("💡 Usage: python scripts/run_analysis.py https://example.com")
        return
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"🔧 Auto-formatted to: {url}")
    
    # Import and run analysis
    # Adjust import to work relative to the script location
    from src.processors.main_processor import WebsiteAnalysisProcessor
    
    processor = WebsiteAnalysisProcessor()
    
    try:
        print(f"\n🚀 Starting analysis...")
        print("⏱️  Please wait...")
        
        result = processor.process_website(url)
        formatted_result = processor.generate_output_format(result)
        
        # Quick summary display
        print(f"\n✅ Analysis Complete!")
        if formatted_result.get('status') != 'failed':
            print(f"🏢 Industry: {formatted_result['classification']['industry']}")
            print(f"🔢 NAICS Code: {formatted_result['classification']['naics_code']}")
            print(f"🎯 Confidence: {formatted_result['classification']['confidence']}")
        else:
            print(f"❌ Failed: {formatted_result.get('error', 'Unknown error')}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        output_file = f'data/outputs/analysis_{domain.replace(".", "_")}_{timestamp}.json'
        processor.save_result(formatted_result, output_file)
        print(f"💾 Full report saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        processor.cleanup()

if __name__ == "__main__":
    main()
