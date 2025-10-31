"""
Disk Monitor Module
Handles interaction with HD Sentinel CLI to retrieve disk health information
"""

import subprocess
import re
import os


class DiskMonitor:
    """Class to monitor disk health using HD Sentinel Linux CLI"""

    def __init__(self):
        self.hdsentinel_path = '/usr/local/bin/HDSentinel'

    def get_disk_health(self, disk_path):
        """
        Get disk health information from HD Sentinel

        Args:
            disk_path (str): Path to disk device (e.g., /dev/sda)

        Returns:
            dict: Disk health information including health %, temperature, model, etc.
        """
        try:
            # Run HD Sentinel with the specified disk
            # -solid flag for SSD detection, -r for report
            result = subprocess.run(
                [self.hdsentinel_path, '-dev', disk_path, '-r'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"Error reading disk {disk_path}: {result.stderr}")
                return None

            output = result.stdout

            # Parse HD Sentinel output
            disk_info = self._parse_hdsentinel_output(output, disk_path)

            return disk_info

        except subprocess.TimeoutExpired:
            print(f"Timeout reading disk {disk_path}")
            return None
        except Exception as e:
            print(f"Exception reading disk {disk_path}: {str(e)}")
            return None

    def _parse_hdsentinel_output(self, output, disk_path):
        """
        Parse HD Sentinel CLI output to extract disk information

        Args:
            output (str): Raw output from HD Sentinel
            disk_path (str): Path to disk device

        Returns:
            dict: Parsed disk information
        """
        disk_info = {
            'disk_path': disk_path,
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'serial': 'Unknown',
            'size': 'Unknown',
            'disk_type': 'Unknown',
            'health_percent': 100,
            'temperature': 0,
            'last_updated': None
        }

        # Extract information using regex patterns
        # Health percentage
        health_match = re.search(r'Health[:\s]+(\d+)\s*%', output, re.IGNORECASE)
        if health_match:
            disk_info['health_percent'] = int(health_match.group(1))

        # Temperature
        temp_match = re.search(r'Temperature[:\s]+(\d+)\s*°?C', output, re.IGNORECASE)
        if temp_match:
            disk_info['temperature'] = int(temp_match.group(1))

        # Model
        model_match = re.search(r'Model[:\s]+(.+?)(?:\n|$)', output, re.IGNORECASE)
        if model_match:
            model = model_match.group(1).strip()
            disk_info['model'] = model

            # Try to extract manufacturer from model name
            disk_info['manufacturer'] = self._extract_manufacturer(model)

        # Serial number
        serial_match = re.search(r'Serial[:\s]+(.+?)(?:\n|$)', output, re.IGNORECASE)
        if serial_match:
            disk_info['serial'] = serial_match.group(1).strip()

        # Disk size
        size_match = re.search(r'Size[:\s]+(.+?)(?:\n|$)', output, re.IGNORECASE)
        if size_match:
            disk_info['size'] = size_match.group(1).strip()

        # Disk type (SSD, HDD, NVMe)
        if re.search(r'SSD|Solid State', output, re.IGNORECASE):
            disk_info['disk_type'] = 'SSD'
        elif re.search(r'NVMe', output, re.IGNORECASE):
            disk_info['disk_type'] = 'NVMe'
        else:
            disk_info['disk_type'] = 'HDD'

        # Add timestamp
        from datetime import datetime
        disk_info['last_updated'] = datetime.now().isoformat()

        return disk_info

    def _extract_manufacturer(self, model):
        """
        Extract manufacturer name from model string

        Args:
            model (str): Model string

        Returns:
            str: Manufacturer name
        """
        # Common manufacturer prefixes
        manufacturers = [
            'Samsung', 'WD', 'Western Digital', 'Seagate', 'Toshiba',
            'Crucial', 'Kingston', 'SanDisk', 'Intel', 'Micron',
            'Corsair', 'ADATA', 'Hitachi', 'HGST', 'Maxtor'
        ]

        model_upper = model.upper()
        for mfr in manufacturers:
            if mfr.upper() in model_upper:
                return mfr

        # If no match, return first word of model
        return model.split()[0] if model else 'Unknown'

    def scan_available_disks(self):
        """
        Scan system for available disk devices

        Returns:
            list: List of available disk paths
        """
        disks = []

        # Check /dev for common disk device names
        dev_path = '/dev'

        # Common disk device patterns
        patterns = ['sd[a-z]', 'nvme[0-9]n[0-9]', 'hd[a-z]']

        try:
            for item in os.listdir(dev_path):
                full_path = os.path.join(dev_path, item)

                # Check if it matches disk patterns and is a block device
                for pattern in patterns:
                    if re.match(pattern, item):
                        if os.path.exists(full_path):
                            disks.append(full_path)
                            break
        except Exception as e:
            print(f"Error scanning disks: {str(e)}")

        return sorted(disks)
