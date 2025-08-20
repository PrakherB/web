#!/usr/bin/env python3
"""
Enhanced NAICS database builder that works with locally downloaded Excel file
"""

import pandas as pd
import json
from pathlib import Path
import re
from typing import Dict, List

class NAICSDatabaseBuilder:
    def __init__(self, local_excel_file=None):
        # Use local file if provided, otherwise try to download
        self.local_excel_file = local_excel_file or "naics_2022_structure.xlsx"
        self.output_dir = Path("data/naics")
        self.output_file = self.output_dir / "comprehensive_naics_codes.json"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def check_local_file(self) -> bool:
        """Check if local Excel file exists"""
        if Path(self.local_excel_file).exists():
            print(f"✅ Found local NAICS file: {self.local_excel_file}")
            return True
        else:
            print(f"❌ Local file not found: {self.local_excel_file}")
            print("📥 Please download the file manually from:")
            print("   https://www.census.gov/naics/2022NAICS/2022_NAICS_Structure.xlsx")
            print(f"   and save it as: {self.local_excel_file}")
            return False
    
    def download_with_retry(self) -> str:
        """Enhanced download with retry mechanism"""
        import requests
        import time
        
        url = "https://www.census.gov/naics/2022NAICS/2022_NAICS_Structure.xlsx"
        max_retries = 3
        timeout_values = [60, 90, 120]  # Progressive timeout increase
        
        for attempt in range(max_retries):
            try:
                print(f"📥 Download attempt {attempt + 1}/{max_retries}")
                print(f"   Timeout: {timeout_values[attempt]} seconds")
                
                # Use session for better connection handling
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                
                response = session.get(url, timeout=timeout_values[attempt], stream=True)
                response.raise_for_status()
                
                # Download in chunks to handle large files better
                with open(self.local_excel_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"✅ Download successful: {self.local_excel_file}")
                return self.local_excel_file
                
            except Exception as e:
                print(f"❌ Download attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"⏱️  Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print("❌ All download attempts failed")
                    raise
    
    def parse_excel_file(self, excel_file: str) -> Dict[str, Dict]:
        """Parse the Excel file to extract all 6-digit NAICS codes"""
        
        print("📊 Parsing NAICS Excel file...")
        
        try:
            # Read the Excel file with better error handling
            print(f"   Loading: {excel_file}")
            df = pd.read_excel(
                excel_file, 
                sheet_name="2022 NAICS Structure",
                header=2,  # Data starts from row 3
                dtype={'2022 NAICS Code': str}  # Force string type
            )
            
            print(f"✅ Loaded Excel file with {len(df)} rows")
            
            # Clean and filter the data
            df = df.dropna(subset=['2022 NAICS Code', '2022 NAICS Title'])
            df['2022 NAICS Code'] = df['2022 NAICS Code'].astype(str).str.strip()
            
            # Filter for 6-digit codes only
            six_digit_df = df[df['2022 NAICS Code'].str.len() == 6].copy()
            
            print(f"✅ Found {len(six_digit_df)} six-digit NAICS codes")
            
            # Build comprehensive database
            naics_database = {}
            
            for _, row in six_digit_df.iterrows():
                code = row['2022 NAICS Code']
                title = str(row['2022 NAICS Title']).strip()
                
                # Generate enhanced description
                description = self._generate_industry_description(code, title)
                
                naics_database[code] = {
                    "code": code,
                    "title": title,
                    "description": description
                }
            
            return naics_database
            
        except Exception as e:
            print(f"❌ Excel parsing failed: {e}")
            print("💡 Troubleshooting suggestions:")
            print("   • Ensure the Excel file is not corrupted")
            print("   • Check that the file has 'Sheet1' or '2022 NAICS Structure' sheet")
            print("   • Verify the file format is .xlsx")
            raise
    
    def _generate_industry_description(self, code: str, title: str) -> str:
        """Generate comprehensive industry descriptions"""
        
        # Enhanced descriptions for common business types
        enhanced_patterns = {
            # Professional Services
            'lawyer|attorney|legal': "This industry comprises establishments of legal practitioners primarily engaged in the practice of law, including legal advice, representation, and document preparation.",
            'accountant|accounting|cpa': "This industry comprises establishments primarily engaged in providing accounting, auditing, bookkeeping, and related financial services.",
            'consulting|consultant': "This industry comprises establishments primarily engaged in providing professional consulting services and expert advice to businesses and organizations.",
            
            # Healthcare
            'physician|doctor|medical': "This industry comprises establishments of health practitioners primarily engaged in the practice of medicine, providing medical diagnosis, treatment, and healthcare services.",
            'dental|dentist': "This industry comprises establishments of dental practitioners primarily engaged in the practice of dentistry and oral healthcare.",
            
            # Food Services
            'restaurant|food service': "This industry comprises establishments primarily engaged in preparing and serving food and beverages to customers.",
            'coffee|cafe': "This industry comprises establishments primarily engaged in preparing and serving coffee, beverages, and light food items.",
            
            # Technology
            'software|programming|computer': "This industry comprises establishments primarily engaged in computer programming, software development, and related technical services.",
            'internet|web|digital': "This industry comprises establishments primarily engaged in providing internet-based services and digital solutions.",
        }
        
        title_lower = title.lower()
        
        # Check for enhanced patterns
        for pattern, enhanced_desc in enhanced_patterns.items():
            if re.search(pattern, title_lower):
                return enhanced_desc
        
        # Default description
        return f"This industry comprises establishments primarily engaged in {title.lower()}."
    
    def save_database(self, naics_database: Dict) -> None:
        """Save the comprehensive NAICS database to JSON"""
        
        print(f"💾 Saving comprehensive NAICS database...")
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(naics_database, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(naics_database)} industries to {self.output_file}")
        
        # Generate summary
        self._generate_summary_stats(naics_database)
    
    def _generate_summary_stats(self, naics_database: Dict) -> None:
        """Generate and display summary statistics"""
        
        # Count by sector (first 2 digits)
        sector_counts = {}
        for code in naics_database.keys():
            sector = code[:2]
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        # Top sectors by count
        top_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"\n📊 NAICS Database Summary:")
        print(f"   Total 6-digit Industries: {len(naics_database)}")
        print(f"   Total Sectors: {len(sector_counts)}")
        print(f"\n🔝 Top Sectors by Industry Count:")
        
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
            '56': 'Administrative and Support Services',
            '61': 'Educational Services',
            '62': 'Health Care and Social Assistance',
            '71': 'Arts, Entertainment, and Recreation',
            '72': 'Accommodation and Food Services',
            '81': 'Other Services',
            '92': 'Public Administration'
        }
        
        for sector, count in top_sectors:
            sector_name = sector_names.get(sector, f'Sector {sector}')
            print(f"      {sector}: {count:3d} industries - {sector_name}")
        
        # Save sector summary
        summary_file = self.output_dir / "naics_sector_summary.json"
        with open(summary_file, 'w') as f:
            json.dump({
                "total_industries": len(naics_database),
                "total_sectors": len(sector_counts),
                "sector_counts": sector_counts,
                "sector_names": sector_names,
                "generation_date": pd.Timestamp.now().isoformat()
            }, f, indent=2)
        
        print(f"📋 Sector summary saved to: {summary_file}")
    
    def build_database(self) -> str:
        """Complete workflow to build comprehensive NAICS database"""
        
        print("🚀 Building Comprehensive NAICS Database")
        print("=" * 60)
        
        try:
            # Step 1: Check for local file or attempt download
            if not self.check_local_file():
                print("📥 Attempting to download NAICS file...")
                excel_file = self.download_with_retry()
            else:
                excel_file = self.local_excel_file
            
            # Step 2: Parse Excel file
            naics_database = self.parse_excel_file(excel_file)
            
            # Step 3: Save database
            self.save_database(naics_database)
            
            print(f"\n🎉 SUCCESS! Comprehensive NAICS database built with {len(naics_database)} industries")
            print(f"📁 Database location: {self.output_file}")
            
            return str(self.output_file)
            
        except Exception as e:
            print(f"❌ Database building failed: {e}")
            print("\n💡 Alternative solutions:")
            print("   1. Download the file manually from the Census Bureau website")
            print("   2. Check your internet connection")
            print("   3. Try running the script again later")
            raise

def main():
    """Main execution function"""
    
    # Check if user provided a local file
    import sys
    local_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    builder = NAICSDatabaseBuilder(local_file)
    database_file = builder.build_database()
    
    # Test the database
    print("\n🧪 Testing the database...")
    with open(database_file, 'r') as f:
        db = json.load(f)
    
    # Show sample entries
    sample_codes = ['541110', '541511', '621111', '722513', '713940']
    print("\n📋 Sample Database Entries:")
    for code in sample_codes:
        if code in db:
            print(f"   {code}: {db[code]['title']}")
        else:
            print(f"   {code}: Not found")
    
    print(f"\n✅ Database ready for use with {len(db)} industries!")

if __name__ == "__main__":
    main()
