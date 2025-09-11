"""
Main API routes for NAICS classification
"""
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from src.processors.main_processor import MainProcessor
from src.classifiers.naics_classifier import NAICSClassifier
from src.extractors.content_extractor import WebContentExtractor
from src.utils.validation import ValidationUtils
from src.search.vector_search import find_similar_designs
from src.analytics.metrics import AnalyticsMetrics
from src.reporting.generator import ReportGenerator
from src.database.models import User, db
from src.api.auth import generate_token
from werkzeug.security import generate_password_hash, check_password_hash
from config.database import DatabaseConfig
from src.database.manager import db_manager
import logging
import traceback

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize components
processor = MainProcessor()
classifier = NAICSClassifier()
extractor = WebContentExtractor()
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
    """Classify business based on URL"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'url' not in data:
            return jsonify({
                'error': 'Missing required field: url'
            }), 400
        
        url = data['url']
        
        # 1. Processing
        analysis_result = processor.process_url(url)

        if not analysis_result:
            return jsonify({'error': 'Failed to process the URL.'}), 400

        # 2. Analytics
        metrics_calculator = AnalyticsMetrics(analysis_result)
        key_metrics = metrics_calculator.calculate_key_metrics()

        # 3. Reporting
        report_generator = ReportGenerator(analysis_result, key_metrics)
        report = report_generator.generate_comprehensive_report()
        
        return jsonify(report)
        
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

@app.route('/api/v1/designs/search', methods=['POST'])
def search_designs():
    """
    Searches for similar designs based on a business description.
    """
    try:
        data = request.get_json()
        if not data or 'business_description' not in data:
            return jsonify({'error': 'Missing business_description'}), 400

        results = find_similar_designs(
            business_description=data['business_description'],
            naics_category=data.get('naics_category'),
            top_k=data.get('top_k', 10)
        )
        return jsonify(results)
    except Exception as e:
        logging.error(f"Design search error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password_hash, auth.password):
        token = generate_token(user.id)
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/sessions', methods=['GET'])
def get_sessions():
    userId = request.args.get('userId')
    if not userId:
        return jsonify({'error': 'Missing userId parameter'}), 400

    sessions = db_manager.get_analysis_sessions(user_id=userId)
    return jsonify([session.to_dict() for session in sessions])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
