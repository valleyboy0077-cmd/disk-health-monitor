"""
Disk Health Monitor Application
Main Flask application entry point
Provides web GUI for monitoring disk health using HD Sentinel
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
from datetime import datetime
from disk_monitor import DiskMonitor
from notification_handler import NotificationHandler

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for API endpoints

# Configuration file path
CONFIG_FILE = '/app/data/config.json'
DISK_DATA_FILE = '/app/data/disk_data.json'

# Initialize disk monitor and notification handler
disk_monitor = DiskMonitor()
notification_handler = NotificationHandler()

# Background scheduler for periodic disk checks
scheduler = BackgroundScheduler()


def load_config():
    """Load configuration from JSON file or create default config"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default configuration
        default_config = {
            'disks': [],  # List of disk paths to monitor
            'disk_thresholds': {},  # Individual disk thresholds {disk_path: {warning: 90, critical: 75}}
            'temp_warning': 48,  # Default temperature warning threshold (°C)
            'temp_critical': 60,  # Default temperature critical threshold (°C)
            'notification_type': 'none',  # 'webhook', 'pushover', or 'none'
            'notification_config': {}  # Notification service specific config
        }
        save_config(default_config)
        return default_config


def save_config(config):
    """Save configuration to JSON file"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_disk_data():
    """Load cached disk data from file"""
    if os.path.exists(DISK_DATA_FILE):
        with open(DISK_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_disk_data(data):
    """Save disk data to file"""
    os.makedirs(os.path.dirname(DISK_DATA_FILE), exist_ok=True)
    with open(DISK_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def check_disks_and_notify():
    """
    Background task to check all configured disks
    Sends notifications if thresholds are exceeded
    """
    config = load_config()
    disk_data = {}

    for disk_path in config['disks']:
        # Get disk health information from HD Sentinel
        health_info = disk_monitor.get_disk_health(disk_path)

        if health_info:
            disk_data[disk_path] = health_info

            # Get thresholds for this specific disk or use defaults
            thresholds = config['disk_thresholds'].get(disk_path, {
                'warning': 90,
                'critical': 75
            })

            # Check health thresholds
            health_percent = health_info.get('health_percent', 100)
            temp = health_info.get('temperature', 0)

            # Determine health status
            if health_percent <= thresholds['critical']:
                notification_handler.send_notification(
                    config,
                    f"CRITICAL: Disk {disk_path} health at {health_percent}%",
                    health_info
                )
            elif health_percent <= thresholds['warning']:
                notification_handler.send_notification(
                    config,
                    f"WARNING: Disk {disk_path} health at {health_percent}%",
                    health_info
                )

            # Check temperature thresholds
            if temp >= config['temp_critical']:
                notification_handler.send_notification(
                    config,
                    f"CRITICAL: Disk {disk_path} temperature at {temp}°C",
                    health_info
                )
            elif temp >= config['temp_warning']:
                notification_handler.send_notification(
                    config,
                    f"WARNING: Disk {disk_path} temperature at {temp}°C",
                    health_info
                )

    # Save disk data for web interface
    save_disk_data(disk_data)


# ==================== WEB ROUTES ====================

@app.route('/')
def index():
    """Serve main dashboard page"""
    return render_template('index.html')


@app.route('/api/disks', methods=['GET'])
def get_disks():
    """API endpoint to get current disk health data"""
    config = load_config()
    disk_data = load_disk_data()

    return jsonify({
        'disks': disk_data,
        'config': config
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """API endpoint to get current configuration"""
    config = load_config()
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """API endpoint to update configuration"""
    new_config = request.json
    save_config(new_config)
    return jsonify({'status': 'success'})


@app.route('/api/disks/add', methods=['POST'])
def add_disk():
    """API endpoint to add a disk to monitoring"""
    disk_path = request.json.get('disk_path')

    if not disk_path:
        return jsonify({'status': 'error', 'message': 'Disk path required'}), 400

    config = load_config()

    if disk_path not in config['disks']:
        config['disks'].append(disk_path)

        # Set default thresholds for new disk
        config['disk_thresholds'][disk_path] = {
            'warning': 90,
            'critical': 75
        }

        save_config(config)

        # Immediately check the new disk
        health_info = disk_monitor.get_disk_health(disk_path)
        if health_info:
            disk_data = load_disk_data()
            disk_data[disk_path] = health_info
            save_disk_data(disk_data)
            return jsonify({'status': 'success', 'disk_info': health_info})
        else:
            return jsonify({'status': 'error', 'message': 'Could not read disk information'}), 400

    return jsonify({'status': 'error', 'message': 'Disk already exists'}), 400


@app.route('/api/disks/remove', methods=['POST'])
def remove_disk():
    """API endpoint to remove a disk from monitoring"""
    disk_path = request.json.get('disk_path')

    config = load_config()

    if disk_path in config['disks']:
        config['disks'].remove(disk_path)

        # Remove disk-specific thresholds
        if disk_path in config['disk_thresholds']:
            del config['disk_thresholds'][disk_path]

        save_config(config)

        # Remove from cached data
        disk_data = load_disk_data()
        if disk_path in disk_data:
            del disk_data[disk_path]
            save_disk_data(disk_data)

        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Disk not found'}), 404


@app.route('/api/disks/refresh', methods=['POST'])
def refresh_disks():
    """API endpoint to manually refresh disk data"""
    check_disks_and_notify()
    disk_data = load_disk_data()
    return jsonify({'status': 'success', 'disks': disk_data})


@app.route('/api/available-disks', methods=['GET'])
def get_available_disks():
    """API endpoint to scan for available disks on the system"""
    available_disks = disk_monitor.scan_available_disks()
    return jsonify({'disks': available_disks})


if __name__ == '__main__':
    # Start background scheduler to check disks every 5 minutes
    scheduler.add_job(
        func=check_disks_and_notify,
        trigger="interval",
        minutes=5,
        id='disk_check',
        name='Check disk health every 5 minutes',
        replace_existing=True
    )
    scheduler.start()

    # Initial disk check on startup
    check_disks_and_notify()

    # Start Flask web server
    app.run(host='0.0.0.0', port=30969, debug=False)
