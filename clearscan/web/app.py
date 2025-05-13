"""
Simple web interface for ClearScan
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from ..models import Network, ScanResult, User

app = Flask(__name__)
auth = HTTPBasicAuth()
engine = create_engine('sqlite:///clearscan.db')
Session = sessionmaker(bind=engine)

@auth.verify_password
def verify_password(username, password):
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    if user and check_password_hash(user.password_hash, password):
        return username
    return None

@app.route('/')
@auth.login_required
def index():
    session = Session()
    networks = session.query(Network).all()
    session.close()
    return render_template('index.html', networks=networks)

@app.route('/network/<int:network_id>')
@auth.login_required
def network_details(network_id):
    session = Session()
    network = session.query(Network).get(network_id)
    results = session.query(ScanResult).filter_by(network_id=network_id).order_by(ScanResult.timestamp.desc()).limit(10).all()
    session.close()
    return render_template('network.html', network=network, results=results)

@app.route('/network/add', methods=['GET', 'POST'])
@auth.login_required
def add_network():
    if request.method == 'POST':
        session = Session()
        network = Network(
            name=request.form['name'],
            ip_range=request.form['ip_range'],
            description=request.form.get('description', ''),
            scan_interval=int(request.form.get('scan_interval', 3600))
        )
        session.add(network)
        session.commit()
        session.close()
        flash('Network added successfully')
        return redirect(url_for('index'))
    return render_template('add_network.html')

@app.route('/api/networks')
@auth.login_required
def api_networks():
    session = Session()
    networks = session.query(Network).all()
    result = [{
        'id': n.id,
        'name': n.name,
        'ip_range': n.ip_range,
        'is_active': n.is_active,
        'scan_interval': n.scan_interval
    } for n in networks]
    session.close()
    return jsonify(result)

def run_web(host="127.0.0.1", port=5000, debug=False):
    """Run the web interface."""
    app.run(host=host, port=port, debug=debug) 