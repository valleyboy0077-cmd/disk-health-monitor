# Disk Health Monitor

A Docker-based disk health monitoring application with a web GUI interface. Monitor your disk health, temperature, and receive notifications when thresholds are exceeded.

## Features

- 🖴 **Real-time Disk Monitoring**: Monitor multiple disks simultaneously
- 📊 **Visual Health Indicators**: Color-coded health bars (Green/Orange/Red)
- 🌡️ **Temperature Monitoring**: Track disk temperatures with customizable thresholds
- ⚙️ **Individual Disk Configuration**: Set custom health thresholds for each disk
- 🔔 **Notifications**: Support for Webhooks and Pushover notifications
- 🐳 **Docker Container**: Easy deployment with Docker Compose
- 💾 **Persistent Storage**: Configuration and data persist across container restarts

## Technology Stack

- **Backend**: Python 3.11, Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Disk Monitoring**: HD Sentinel Linux CLI
- **Scheduler**: APScheduler (checks every 5 minutes)
- **Container**: Docker

## Prerequisites

- Docker and Docker Compose installed
- Host system running Linux
- Root/sudo access for disk device access

## Installation

### 1. Extract the Files

Extract the `disk-health-monitor.zip` file:

```bash
unzip disk-health-monitor.zip
cd disk-health-monitor
```

### 2. Configure Docker Compose

Edit `docker-compose.yml` to add your disk devices:

```yaml
devices:
  - /dev/sda
  - /dev/sdb
  - /dev/nvme0n1
  # Add all disks you want to monitor
```

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:30969
```

Or use your server's IP address:
```
http://YOUR_SERVER_IP:30969
```

## Usage

### Adding Disks

1. Click the "➕ Add Disk" button in the header
2. Either:
   - Select from the list of detected disks, OR
   - Manually enter the disk path (e.g., `/dev/sda`)
3. Click "Add Disk"

### Configuring Thresholds

1. Navigate to the "Settings" tab
2. **Disk Health Thresholds**: Set warning and critical percentages for each disk
   - Default Warning: 90%
   - Default Critical: 75%
3. **Temperature Thresholds**: Set global temperature thresholds
   - Default Warning: 48°C
   - Default Critical: 60°C
4. Click "💾 Save Settings"

### Setting Up Notifications

#### Webhook Notifications

1. Go to Settings → Notifications
2. Select "Webhook" from the dropdown
3. Enter your webhook URL
4. Save settings

The webhook will receive POST requests with this payload:
```json
{
  "message": "WARNING: Disk /dev/sda health at 85%",
  "disk_path": "/dev/sda",
  "manufacturer": "Samsung",
  "model": "Samsung SSD 860 EVO",
  "serial": "S3Z9NB0K123456",
  "health_percent": 85,
  "temperature": 42,
  "timestamp": "2025-10-31T10:30:00"
}
```

#### Pushover Notifications

1. Sign up for [Pushover](https://pushover.net/)
2. Get your User Key and create an API Token
3. Go to Settings → Notifications
4. Select "Pushover" from the dropdown
5. Enter your API Token and User Key
6. Save settings

## Docker Commands

```bash
# Start the container
docker-compose up -d

# Stop the container
docker-compose down

# View logs
docker-compose logs -f

# Restart the container
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# Remove container and volumes
docker-compose down -v
```

## File Structure

```
disk-health-monitor/
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependencies
├── app.py                     # Main Flask application
├── disk_monitor.py            # Disk monitoring logic
├── notification_handler.py    # Notification handling
├── templates/
│   └── index.html            # Web interface
└── data/                     # Persistent data (created automatically)
    ├── config.json           # Application configuration
    └── disk_data.json        # Cached disk data
```

## Configuration Files

### config.json
Stores application configuration:
- List of monitored disks
- Individual disk thresholds
- Temperature thresholds
- Notification settings

### disk_data.json
Caches the latest disk health data for quick display in the web interface.

## Monitoring Schedule

- Disks are checked every **5 minutes** automatically
- Manual refresh available via the "🔄 Refresh" button
- Notifications have a **1-hour cooldown** to prevent spam

## Troubleshooting

### Container won't start
- Ensure Docker has permission to access `/dev` devices
- Check that `privileged: true` is set in docker-compose.yml
- Verify disk devices are correctly listed under `devices:`

### Disks not detected
- Ensure the container is running in privileged mode
- Check that disk devices are mounted: `docker exec disk-health-monitor ls -la /dev`
- Verify HD Sentinel is installed: `docker exec disk-health-monitor HDSentinel -h`

### Notifications not working
- Check notification configuration in Settings
- View logs for error messages: `docker-compose logs -f`
- Test webhook URL manually with curl
- Verify Pushover credentials are correct

### Permission denied errors
- The container needs privileged access to read disk information
- Ensure `privileged: true` is set in docker-compose.yml

## Security Considerations

- The container runs in **privileged mode** to access disk devices
- Only expose port 30969 to trusted networks
- Consider using a reverse proxy with authentication for external access
- Webhook URLs and API keys are stored in plain text - secure the data directory

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the logs: `docker-compose logs -f`
2. Verify configuration in the web interface
3. Ensure HD Sentinel is working: `docker exec disk-health-monitor HDSentinel -dev /dev/sda -r`

## Acknowledgments

- [HD Sentinel](https://www.hdsentinel.com/) for the Linux CLI tool
- Flask framework for the web interface
- Docker for containerization
