from flask import Blueprint, render_template, request, jsonify
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.cxo_service import search_cxo
from models.database import get_history, get_db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    company = data.get('company', '').strip()
    if not company:
        return jsonify({'error': 'Company name is required', 'results': []})
    if len(company) < 2:
        return jsonify({'error': 'Please enter at least 2 characters', 'results': []})
    results = search_cxo(company)
    return jsonify({
        'company': company,
        'results': results,
        'count': len(results),
        'message': f'Found {len(results)} CXO contact(s) for "{company}"'
    })

@main.route('/history')
def history():
    return render_template('history.html', history=get_history(50))

@main.route('/api/history')
def api_history():
    return jsonify(get_history(50))

@main.route('/dashboard')
def dashboard():
    conn = get_db()
    stats = {
        'total_cxos': conn.execute('SELECT COUNT(*) FROM cxo_contacts').fetchone()[0],
        'total_companies': conn.execute('SELECT COUNT(DISTINCT company) FROM cxo_contacts').fetchone()[0],
        'total_searches': conn.execute('SELECT COUNT(*) FROM search_history').fetchone()[0],
        'web_found': conn.execute("SELECT COUNT(*) FROM cxo_contacts WHERE source='web'").fetchone()[0],
    }
    title_dist = [dict(r) for r in conn.execute(
        'SELECT title, COUNT(*) as cnt FROM cxo_contacts GROUP BY title ORDER BY cnt DESC LIMIT 8'
    ).fetchall()]
    top_companies = [dict(r) for r in conn.execute(
        'SELECT company, COUNT(*) as cnt FROM cxo_contacts GROUP BY company ORDER BY cnt DESC LIMIT 10'
    ).fetchall()]
    recent_searches = get_history(10)
    recent_cxos = [dict(r) for r in conn.execute(
        'SELECT * FROM cxo_contacts ORDER BY id DESC LIMIT 12'
    ).fetchall()]
    conn.close()
    return render_template('dashboard.html',
        stats=stats,
        title_dist=title_dist,
        top_companies=top_companies,
        recent_searches=recent_searches,
        recent_cxos=recent_cxos
    )

@main.route('/api/dashboard')
def api_dashboard():
    conn = get_db()
    title_dist = [dict(r) for r in conn.execute(
        'SELECT title, COUNT(*) as cnt FROM cxo_contacts GROUP BY title ORDER BY cnt DESC'
    ).fetchall()]
    top_companies = [dict(r) for r in conn.execute(
        'SELECT company, COUNT(*) as cnt FROM cxo_contacts GROUP BY company ORDER BY cnt DESC LIMIT 10'
    ).fetchall()]
    recent_searches = get_history(7)
    conn.close()
    return jsonify({
        'title_dist': title_dist,
        'top_companies': top_companies,
        'recent_searches': recent_searches
    })
