
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Helper function to load data
def load_data():
    try:
        with open('static/result.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}, 500

# ===== Frontend Routes =====

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/docs')
def api_docs():
    return render_template('api_docs.html')

# Static 폴더의 result.json을 서빙하기 위한 라우트
@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('static', filename)

# ===== API v1 Routes =====

@app.route('/api/v1/all', methods=['GET'])
def api_all():
    """Get all data (Individual + WRS + Market Condition)"""
    data = load_data()
    if isinstance(data, tuple):  # Error case
        return jsonify(data[0]), data[1]
    
    return jsonify({
        "status": "success",
        "data": data,
        "meta": {
            "timestamp": data.get("last_updated"),
            "total_count": data.get("total_count")
        },
        "error": null
    })

@app.route('/api/v1/individual', methods=['GET'])
def api_individual():
    """Get Individual RS data with optional filters"""
    data = load_data()
    if isinstance(data, tuple):
        return jsonify(data[0]), data[1]
    
    stocks = data.get("data", [])
    
    # Query parameters
    ticker = request.args.get('ticker')
    sector = request.args.get('sector')
    rs_min = request.args.get('rs_min', type=float)
    limit = request.args.get('limit', type=int)
    
    # Apply filters
    if ticker:
        stocks = [s for s in stocks if s.get('Ticker', '').upper() == ticker.upper()]
    if sector:
        stocks = [s for s in stocks if s.get('Sector', '').lower() == sector.lower()]
    if rs_min is not None:
        stocks = [s for s in stocks if s.get('RS_6mo', 0) >= rs_min]
    if limit:
        stocks = stocks[:limit]
    
    return jsonify({
        "status": "success",
        "data": stocks,
        "meta": {
            "timestamp": data.get("last_updated"),
            "total_count": len(stocks),
            "filters_applied": {
                "ticker": ticker,
                "sector": sector,
                "rs_min": rs_min,
                "limit": limit
            }
        },
        "error": None
    })

@app.route('/api/v1/wrs', methods=['GET'])
def api_wrs():
    """Get WRS (Weighted Relative Strength) data"""
    data = load_data()
    if isinstance(data, tuple):
        return jsonify(data[0]), data[1]
    
    wrs_data = data.get("wrs_data", [])
    
    # Query parameters
    sector = request.args.get('sector')
    min_count = request.args.get('min_count', type=int)
    
    # Apply filters
    if sector:
        wrs_data = [w for w in wrs_data if w.get('Sector', '').lower() == sector.lower()]
    if min_count:
        wrs_data = [w for w in wrs_data if w.get('Count', 0) >= min_count]
    
    return jsonify({
        "status": "success",
        "data": wrs_data,
        "meta": {
            "timestamp": data.get("last_updated"),
            "total_count": len(wrs_data),
            "filters_applied": {
                "sector": sector,
                "min_count": min_count
            }
        },
        "error": None
    })

@app.route('/api/v1/todays-list', methods=['GET'])
def api_todays_list():
    """Get Today's List (filtered stocks)"""
    data = load_data()
    if isinstance(data, tuple):
        return jsonify(data[0]), data[1]
    
    stocks = data.get("data", [])
    wrs_data = data.get("wrs_data", [])
    
    # Step 1: Find qualified sectors
    qualified_sectors = [
        w for w in wrs_data
        if w.get('Count', 0) >= 2 and
           w.get('WRS_Rank_Pct', 100) <= 30 and
           w.get('WRS_MD_Rank_Pct', 100) <= 40
    ]
    
    qualified_keys = set(f"{w['Sector']}|{w['Industry']}" for w in qualified_sectors)
    
    # Step 2: Filter stocks in qualified sectors with RS rank <= 20%
    filtered_stocks = [
        s for s in stocks
        if f"{s.get('Sector')}|{s.get('Industry')}" in qualified_keys and
           s.get('RS_Rank_Pct') is not None and
           s.get('RS_Rank_Pct') <= 20
    ]
    
    return jsonify({
        "status": "success",
        "data": filtered_stocks,
        "meta": {
            "timestamp": data.get("last_updated"),
            "total_count": len(filtered_stocks),
            "qualified_sectors_count": len(qualified_sectors),
            "filter_criteria": {
                "sector_criteria": "Count >= 2, WRS rank <= 30%, WRS_MD rank <= 40%",
                "stock_criteria": "RS rank <= 20%"
            }
        },
        "error": None
    })

@app.route('/api/v1/market-condition', methods=['GET'])
def api_market_condition():
    """Get Market Condition only"""
    data = load_data()
    if isinstance(data, tuple):
        return jsonify(data[0]), data[1]
    
    return jsonify({
        "status": "success",
        "data": {
            "market_condition": data.get("market_condition", "N/A"),
            "last_updated": data.get("last_updated")
        },
        "meta": {
            "timestamp": data.get("last_updated")
        },
        "error": None
    })

@app.route('/api/v1/ticker/<ticker_symbol>', methods=['GET'])
def api_ticker(ticker_symbol):
    """Get specific ticker details"""
    data = load_data()
    if isinstance(data, tuple):
        return jsonify(data[0]), data[1]
    
    stocks = data.get("data", [])
    ticker_data = next((s for s in stocks if s.get('Ticker', '').upper() == ticker_symbol.upper()), None)
    
    if not ticker_data:
        return jsonify({
            "status": "error",
            "data": None,
            "meta": {
                "timestamp": data.get("last_updated")
            },
            "error": {
                "code": "NOT_FOUND",
                "message": f"Ticker '{ticker_symbol}' not found"
            }
        }), 404
    
    return jsonify({
        "status": "success",
        "data": ticker_data,
        "meta": {
            "timestamp": data.get("last_updated")
        },
        "error": None
    })

if __name__ == '__main__':
    app.run(debug=True, port=8888)

# Export app for Vercel
# Vercel will use this directly
