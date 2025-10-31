"""
Notification Handler Module
Handles sending notifications via webhooks or Pushover
"""

import requests
import json
from datetime import datetime


class NotificationHandler:
    """Class to handle sending notifications for disk health alerts"""

    def __init__(self):
        self.last_notifications = {}  # Track last notification time to avoid spam
        self.notification_cooldown = 3600  # 1 hour cooldown between same notifications

    def send_notification(self, config, message, disk_info):
        """
        Send notification based on configured notification type

        Args:
            config (dict): Application configuration
            message (str): Notification message
            disk_info (dict): Disk information dictionary
        """
        notification_type = config.get('notification_type', 'none')

        # Check cooldown to avoid notification spam
        notification_key = f"{disk_info['disk_path']}_{message}"
        if not self._check_cooldown(notification_key):
            return

        if notification_type == 'webhook':
            self._send_webhook(config, message, disk_info)
        elif notification_type == 'pushover':
            self._send_pushover(config, message, disk_info)

    def _check_cooldown(self, notification_key):
        """
        Check if enough time has passed since last notification

        Args:
            notification_key (str): Unique key for this notification

        Returns:
            bool: True if notification should be sent, False if in cooldown
        """
        now = datetime.now().timestamp()

        if notification_key in self.last_notifications:
            last_time = self.last_notifications[notification_key]
            if now - last_time < self.notification_cooldown:
                return False  # Still in cooldown period

        # Update last notification time
        self.last_notifications[notification_key] = now
        return True

    def _send_webhook(self, config, message, disk_info):
        """
        Send notification via webhook

        Args:
            config (dict): Application configuration
            message (str): Notification message
            disk_info (dict): Disk information dictionary
        """
        webhook_config = config.get('notification_config', {})
        webhook_url = webhook_config.get('webhook_url')

        if not webhook_url:
            print("Webhook URL not configured")
            return

        # Prepare webhook payload
        payload = {
            'message': message,
            'disk_path': disk_info['disk_path'],
            'manufacturer': disk_info['manufacturer'],
            'model': disk_info['model'],
            'serial': disk_info['serial'],
            'health_percent': disk_info['health_percent'],
            'temperature': disk_info['temperature'],
            'timestamp': datetime.now().isoformat()
        }

        # Add custom headers if configured
        headers = {'Content-Type': 'application/json'}
        if 'webhook_headers' in webhook_config:
            headers.update(webhook_config['webhook_headers'])

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                print(f"Webhook notification sent: {message}")
            else:
                print(f"Webhook notification failed: {response.status_code}")

        except Exception as e:
            print(f"Error sending webhook: {str(e)}")

    def _send_pushover(self, config, message, disk_info):
        """
        Send notification via Pushover

        Args:
            config (dict): Application configuration
            message (str): Notification message
            disk_info (dict): Disk information dictionary
        """
        pushover_config = config.get('notification_config', {})
        api_token = pushover_config.get('api_token')
        user_key = pushover_config.get('user_key')

        if not api_token or not user_key:
            print("Pushover API token or user key not configured")
            return

        # Prepare Pushover payload
        payload = {
            'token': api_token,
            'user': user_key,
            'message': message,
            'title': 'Disk Health Alert',
            'priority': 1,  # High priority
            'html': 1
        }

        # Add detailed disk info to message
        detailed_message = f"{message}<br><br>"
        detailed_message += f"<b>Disk:</b> {disk_info['disk_path']}<br>"
        detailed_message += f"<b>Model:</b> {disk_info['manufacturer']} {disk_info['model']}<br>"
        detailed_message += f"<b>Serial:</b> {disk_info['serial']}<br>"
        detailed_message += f"<b>Health:</b> {disk_info['health_percent']}%<br>"
        detailed_message += f"<b>Temperature:</b> {disk_info['temperature']}°C"

        payload['message'] = detailed_message

        try:
            response = requests.post(
                'https://api.pushover.net/1/messages.json',
                data=payload,
                timeout=10
            )

            if response.status_code == 200:
                print(f"Pushover notification sent: {message}")
            else:
                print(f"Pushover notification failed: {response.status_code}")

        except Exception as e:
            print(f"Error sending Pushover notification: {str(e)}")
