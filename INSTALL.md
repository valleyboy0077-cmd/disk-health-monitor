# Installation and Deployment Guide

## Quick Start

### Step 1: Extract Files
```bash
unzip disk-health-monitor.zip
cd disk-health-monitor
```

### Step 2: Configure Disks
Edit `docker-compose.yml` and add your disk devices under the `devices:` section:

```yaml
devices:
  - /dev/sda
  - /dev/sdb
  - /dev/sdc
  # Add more as needed
```

### Step 3: Build Docker Image
```bash
docker-compose build
```

This will:
- Download Python 3.11 base image
- Install system dependencies (wget, unzip, smartmontools)
- Download and install HD Sentinel Linux CLI
- Install Python packages (Flask, APScheduler, etc.)
- Set up the application

### Step 4: Start the Container
```bash
docker-compose up -d
```

The `-d` flag runs it in detached mode (background).

### Step 5: Verify It's Running
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 6: Access Web Interface
Open your browser to:
- Local: http://localhost:30969
- Remote: http://YOUR_SERVER_IP:30969

## Detailed Configuration

### Docker Compose Options

#### Port Configuration
Change the port in `docker-compose.yml`:
```yaml
ports:
  - "8080:30969"  # Access on port 8080 instead
```

#### Timezone
Set your timezone:
```yaml
environment:
  - TZ=America/New_York  # Change to your timezone
```

#### Data Persistence
The `./data` directory is mounted to persist configuration:
```yaml
volumes:
  - ./data:/app/data
```

### Adding Multiple Disks

List all disks you want to monitor:
```yaml
devices:
  - /dev/sda
  - /dev/sdb
  - /dev/sdc
  - /dev/nvme0n1
  - /dev/nvme1n1
```

To find available disks on your system:
```bash
lsblk
# or
ls -la /dev/sd* /dev/nvme*
```

## Building Without Docker Compose

If you prefer to use Docker directly:

```bash
# Build image
docker build -t disk-health-monitor .

# Run container
docker run -d \
  --name disk-health-monitor \
  --privileged \
  -p 30969:30969 \
  -v $(pwd)/data:/app/data \
  -v /dev:/dev:ro \
  --device /dev/sda \
  --device /dev/sdb \
  disk-health-monitor
```

## Updating the Application

### Method 1: Rebuild
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Method 2: Pull and Restart
If you've made code changes:
```bash
docker-compose restart
```

## Uninstalling

### Remove Container Only
```bash
docker-compose down
```

### Remove Container and Data
```bash
docker-compose down -v
rm -rf data/
```

### Remove Everything
```bash
docker-compose down -v
docker rmi disk-health-monitor
cd ..
rm -rf disk-health-monitor/
```

## Troubleshooting Build Issues

### Issue: HD Sentinel Download Fails
If the HD Sentinel download fails during build:
1. Download manually from https://www.hdsentinel.com/hdslin/hdsentinel-020b-x64.zip
2. Place it in the project directory
3. Modify Dockerfile to use local file:
```dockerfile
COPY hdsentinel-020b-x64.zip .
RUN unzip hdsentinel-020b-x64.zip && \
    chmod +x HDSentinel && \
    mv HDSentinel /usr/local/bin/
```

### Issue: Permission Denied
Ensure you're running with sudo or as root:
```bash
sudo docker-compose build
sudo docker-compose up -d
```

### Issue: Port Already in Use
Change the port in docker-compose.yml:
```yaml
ports:
  - "30970:30969"  # Use different external port
```

## Production Deployment

### Using Nginx Reverse Proxy

1. Install Nginx:
```bash
sudo apt install nginx
```

2. Create Nginx config `/etc/nginx/sites-available/disk-health`:
```nginx
server {
    listen 80;
    server_name disk-health.yourdomain.com;

    location / {
        proxy_pass http://localhost:30969;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

3. Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/disk-health /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Adding SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d disk-health.yourdomain.com
```

### Auto-Start on Boot

Docker Compose already includes `restart: unless-stopped`, so the container will auto-start on system reboot.

To verify:
```bash
docker-compose ps
```

## System Requirements

- **OS**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+, etc.)
- **RAM**: 512MB minimum, 1GB recommended
- **Disk**: 500MB for Docker image
- **Docker**: Version 20.10+
- **Docker Compose**: Version 1.29+

## Next Steps

After installation:
1. Access the web interface
2. Add your first disk
3. Configure thresholds in Settings
4. Set up notifications (optional)
5. Monitor the dashboard!

For more information, see README.md
