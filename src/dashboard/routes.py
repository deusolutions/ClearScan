from flask import Blueprint, jsonify, request
from .auth import requires_auth
from ..db import fetch_scan_history

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/status', methods=['GET'])
@requires_auth
def status():
    scan_history = fetch_scan_history()
    return jsonify(scan_history)

@dashboard_bp.route('/scan', methods=['POST'])
@requires_auth
def scan():
    # This route can be used to trigger a new scan
    # Implementation for triggering a scan will go here
    return jsonify({"message": "Scan initiated"}), 202