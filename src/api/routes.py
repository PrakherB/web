"""
Main API routes for NAICS classification
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.processors.main_processor import MainProcessor
from src.classifiers.naics_classifier import NAICSClassifier
from src.extractors.content_extractor import ContentExtractor
from src.utils.validation import ValidationUtils
import logging
import traceback

app = Flask(__name__)
CORS(app)

# Initialize components
processor = MainProcessor()
classifier = NAICSClassifier()
extractor = ContentExtractor()
validator = ValidationUtils()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': processor.get_timestamp()
    })

@app.route('/classify', methods=['POST'])
def classify_business():
    """Classify business based on URL or text"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not any(key in data for key in ['url', 'text']):
            return jsonify({
                'error': 'Missing required field: url or text'
            }), 400
        
        result = {}
        
        if 'url' in data:
            # Extract content from URL
            content = extractor.extract_from_url(data['url'])
            if not content:
                return jsonify({
                    'error': 'Failed to extract content from URL'
                }), 400
                
            # Classify content
            classification = classifier.classify(content)
            result = {
                'url': data['url'],
                'content_preview': content[:200] + '...' if len(content) > 200 else content,
                'classification': classification,
                'confidence': classification.get('confidence', 0),
                'primary_naics': classification.get('primary_naics'),
                'secondary_naics': classification.get('secondary_naics', [])
            }
        
        elif 'text' in data:
            # Classify provided text
            classification = classifier.classify(data['text'])
            result = {
                'text_preview': data['text'][:200] + '...' if len(data['text']) > 200 else data['text'],
                'classification': classification,
                'confidence': classification.get('confidence', 0),
                'primary_naics': classification.get('primary_naics'),
                'secondary_naics': classification.get('secondary_naics', [])
            }
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Classification error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/batch_classify', methods=['POST'])
def batch_classify():
    """Batch classification endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({
                'error': 'Missing required field: items'
            }), 400
        
        items = data['items']
        if len(items) > 100:  # Limit batch size
            return jsonify({
                'error': 'Batch size too large. Maximum 100 items.'
            }), 400
        
        results = []
        for i, item in enumerate(items):
            try:
                if 'url' in item:
                    content = extractor.extract_from_url(item['url'])
                    classification = classifier.classify(content) if content else None
                elif 'text' in item:
                    classification = classifier.classify(item['text'])
                else:
                    classification = None
                
                results.append({
                    'index': i,
                    'classification': classification,
                    'status': 'success' if classification else 'failed'
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e),
                    'status': 'error'
                })
        
        return jsonify({
            'results': results,
            'total': len(items),
            'successful': len([r for r in results if r['status'] == 'success'])
        })
        
    except Exception as e:
        logging.error(f"Batch classification error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/naics/<code>', methods=['GET'])
def get_naics_info(code):
    """Get NAICS code information"""
    try:
        naics_info = classifier.get_naics_info(code)
        if not naics_info:
            return jsonify({
                'error': 'NAICS code not found'
            }), 404
            
        return jsonify(naics_info)
        
    except Exception as e:
        logging.error(f"NAICS info error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
