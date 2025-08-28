import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from src.extractors.content_extractor import WebContentExtractor
from src.classifiers.naics_classifier import NAICSClassifier
from src.extractors.scraping_api_backup import ScrapingAPIBackup

class WebsiteAnalysisProcessor:
    def __init__(self, use_api_backup: bool = False, api_key: str = None):
        """Initialize the website analysis processor"""
        self.content_extractor = WebContentExtractor()
        self.naics_classifier = NAICSClassifier()
        
        if use_api_backup and api_key:
            self.api_backup = ScrapingAPIBackup(api_key)
        else:
            self.api_backup = None
    
    def process_website(self, url: str) -> Dict:
        """Complete processing pipeline for a website"""
        print(f"Processing website: {url}")
        
        # Step 1: Extract content
        print("Extracting website content...")
        content_data = self.content_extractor.extract_website_content(url)
        
        # Debug: Check if content extraction succeeded
        if not content_data:
            print("❌ Primary content extraction failed")
            if self.api_backup:
                print("🔄 Trying API backup...")
                content_data = self.api_backup.extract_with_api(url)
        
        if not content_data:
            return {
                'error': 'Failed to extract website content',
                'url': url,
                'status': 'failed'
            }
        
        print(f"✅ Content extracted successfully: {len(str(content_data))} characters")
        
        # Step 2: Classify industry
        print("Classifying industry...")
        try:
            classification_result = self.naics_classifier.classify_business(content_data)
            print(f"✅ Classification completed")
        except Exception as e:
            print(f"❌ Classification failed: {e}")
            # Create fallback classification
            classification_result = {
                'predicted_naics_code': '000000',
                'predicted_industry': 'Unknown Industry',
                'confidence_score': 0.0,
                'classification_method': 'failed_classification',
                'fallback_category': 'General Business Services'
            }
        
        # Step 3: Combine results
        final_result = {
            'url': url,
            'status': 'completed',
            'content_data': content_data,
            'classification': classification_result,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        return final_result
    
    def generate_output_format(self, result: Dict) -> Dict:
        """Generate output with safe key access and fallback values"""
        
        # Handle failed status
        if result.get('status') != 'completed':
            return {
                'url': result.get('url', 'Unknown URL'),
                'status': 'failed',
                'error': result.get('error', 'Unknown error occurred'),
                'title': 'Content extraction failed',
                'meta_description': 'None',
                'classification': {
                    'industry': 'Unknown',
                    'naics_code': '000000',
                    'confidence': 0.0,
                    'method': 'extraction_failed'
                }
            }
        
        # Safe extraction with fallbacks - HANDLE None classification
        classification = result.get('classification') or {}  # Handle None case
        content = result.get('content_data', {})
        
        formatted_output = {
        'url': result.get('url', 'Unknown URL'),
        'title': content.get('title', 'No title found'),
        'meta_description': content.get('meta_description') or 'None',
        'classification': {
            'industry': classification.get('predicted_industry', 'Unknown Industry'),
            'naics_code': classification.get('predicted_naics_code', '000000'),
            'confidence': round(classification.get('confidence_score', 0.0), 3),
            'method': classification.get('classification_method', 'unknown_method'),
            'fallback_category': classification.get('fallback_category'),
            'total_industries_considered': classification.get('total_industries_considered', 0)  # NEW
        },
        'key_business_phrases': content.get('key_phrases', []),
        'business_keywords': content.get('business_keywords', {}),
        'content_statistics': {
            'headers_found': sum(len(v) for v in content.get('headers', {}).values()),
            'navigation_items': len(content.get('navigation', [])),
            'content_length': len(content.get('main_content', '')) + len(content.get('about_content', ''))
        }
    }
        
        return formatted_output
    
    def save_result(self, result: Dict, filename: str):
        """Save result to JSON file"""
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'content_extractor'):
                self.content_extractor.close()
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")

def main():
    """Main function for testing the processor"""
    processor = WebsiteAnalysisProcessor()
    
    try:
        # Process the Planet Fitness example
        url = "https://planetfitness.com"
        result = processor.process_website(url)
        formatted_result = processor.generate_output_format(result)
        
        print("="*60)
        print("WEBSITE ANALYSIS RESULTS")
        print("="*60)
        print(f"URL: {formatted_result['url']}")
        print(f"Status: {formatted_result.get('status', 'completed')}")
        
        # Safe access to avoid KeyError
        if 'error' in formatted_result:
            print(f"Error: {formatted_result['error']}")
        else:
            print(f"Title: {formatted_result['title']}")
            print(f"Meta Description: {formatted_result['meta_description']}")
            print()
            print("Classification:")
            print(f"  Industry: {formatted_result['classification']['industry']}")
            print(f"  NAICS Code: {formatted_result['classification']['naics_code']}")  
            print(f"  Confidence: {formatted_result['classification']['confidence']}")
            print(f"  Method: {formatted_result['classification']['method']}")
            if formatted_result['classification']['fallback_category']:
                print(f"  Fallback Category: {formatted_result['classification']['fallback_category']}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'data/outputs/analysis_result_{timestamp}.json'
        processor.save_result(formatted_result, output_file)
        print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        processor.cleanup()

def main():
    """Main function with command line arguments support"""
    
    # Get URL from command line arguments
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"🔗 URL provided via command line: {url}")
    else:
        # Fallback to interactive input if no argument provided
        print("🎯 Automated Web Design Analysis Tool")
        print("=" * 50)
        print("💡 Tip: You can also run: python main_processor.py <website_url>")
        print("-" * 50)
        url = input("🔗 Enter website URL to analyze: ").strip()
    
    # Validate URL input
    if not url:
        print("❌ No URL provided. Exiting.")
        print("💡 Usage: python main_processor.py https://example.com")
        return
    
    # Auto-format URL (add https:// if missing)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"🔧 Auto-formatted URL: {url}")
    
    # Initialize processor
    processor = WebsiteAnalysisProcessor()
    
    try:
        print(f"\n🚀 Starting analysis of: {url}")
        print("⏱️  This may take 1-3 minutes...")
        print("-" * 50)
        
        # Process the website
        result = processor.process_website(url)
        formatted_result = processor.generate_output_format(result)
        
        # Display results
        print("=" * 60)
        print("📋 WEBSITE ANALYSIS RESULTS")
        print("=" * 60)
        print(f"📌 URL: {formatted_result['url']}")
        print(f"📊 Status: {formatted_result.get('status', 'completed')}")
        
        if 'error' in formatted_result:
            print(f"❌ Error: {formatted_result['error']}")
        else:
            print(f"📝 Title: {formatted_result['title']}")
            print(f"📄 Meta Description: {formatted_result['meta_description']}")
            print()
            print("🏢 Industry Classification:")
            print(f"   • Industry: {formatted_result['classification']['industry']}")
            print(f"   • NAICS Code: {formatted_result['classification']['naics_code']}")  
            print(f"   • Confidence: {formatted_result['classification']['confidence']}")
            print(f"   • Method: {formatted_result['classification']['method']}")
            
            if formatted_result['classification']['fallback_category']:
                print(f"   • Fallback Category: {formatted_result['classification']['fallback_category']}")
            
            print(f"\n📊 Content Statistics:")
            stats = formatted_result['content_statistics']
            print(f"   • Headers Found: {stats['headers_found']}")
            print(f"   • Navigation Items: {stats['navigation_items']}")
            print(f"   • Content Length: {stats['content_length']} characters")
            
            if formatted_result.get('key_business_phrases'):
                print(f"\n🔑 Key Business Phrases:")
                for phrase in formatted_result['key_business_phrases'][:3]:
                    print(f"   • {phrase}")
        
        # Save results with better naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        output_file = f'data/outputs/analysis_{domain.replace(".", "_")}_{timestamp}.json'
        
        processor.save_result(formatted_result, output_file)
        print(f"\n💾 Detailed results saved to: {output_file}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   • Check if the website URL is accessible")
        print("   • Ensure your internet connection is stable")
        print("   • Try with a different website")
        import traceback
        traceback.print_exc()
    
    finally:
        processor.cleanup()

if __name__ == "__main__":
    main()

