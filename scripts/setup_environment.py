#!/usr/bin/env python3
"""Setup script to prepare the environment"""

import os
import sys
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    base_dir = Path(__file__).parent.parent
    
    directories = [
        "data/naics",
        "data/outputs/analysis_results", 
        "data/temp",
        "logs"
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'selenium', 'beautifulsoup4', 'requests', 
        'pandas', 'transformers', 'torch'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nPlease install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def download_models():
    """Download required transformer models"""
    try:
        from transformers import pipeline
        print("📥 Downloading classification model...")
        classifier = pipeline("zero-shot-classification", 
                             model="facebook/bart-large-mnli")
        print("✓ Model download completed!")
        return True
    except Exception as e:
        print(f"✗ Model download failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up automated-web-design environment...\n")
    
    setup_directories()
    
    if check_dependencies():
        download_models()
        print("\n✅ Environment setup completed!")
        print("\nNext steps:")
        print("1. Copy the main Python implementation files")
        print("2. Run: python scripts/run_analysis.py https://example.com")
    else:
        print("\n❌ Setup incomplete. Please install missing dependencies.")
