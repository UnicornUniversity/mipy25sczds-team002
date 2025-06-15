#!/bin/bash
set -e

echo "🚀 Deploying Deadlock Scores Server on AlmaLinux..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER_DIR="/var/www/deadlock-scores"
NGINX_CONFIG="/etc/nginx/conf.d/deadlock-scores.conf"
DOMAIN="srv641041.hstgr.cloud"  # Your existing domain
PUBLIC_IP="92.112.181.217"      # Your public IP

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root"
    exit 1
fi

print_status "Server environment: AlmaLinux 9.5"
print_status "Node.js: $(node --version)"
print_status "PM2: $(pm2 --version)"
print_status "Nginx: Running"

# Create server directory
print_status "Creating server directory..."
mkdir -p $SERVER_DIR
mkdir -p $SERVER_DIR/logs

# Copy application files (expecting files in current directory)
print_status "Copying application files..."
if [ ! -f "server.js" ]; then
    print_error "server.js not found in current directory!"
    print_error "Please run this script from the deadlock-scores-server directory"
    exit 1
fi

cp server.js $SERVER_DIR/
cp package.json $SERVER_DIR/
[ -f "ecosystem.config.js" ] && cp ecosystem.config.js $SERVER_DIR/

# Install dependencies
print_status "Installing Node.js dependencies..."
cd $SERVER_DIR
npm install --production

# Create ecosystem config if not exists
if [ ! -f "ecosystem.config.js" ]; then
    print_status "Creating PM2 ecosystem config..."
    cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'deadlock-scores',
    script: 'server.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '512M',
    env: {
      NODE_ENV: 'production',
      PORT: 3001
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
EOF
fi

# Stop existing PM2 process if running
print_status "Stopping existing processes..."
pm2 delete deadlock-scores 2>/dev/null || true

# Create Nginx configuration for deadlock scores
print_status "Creating Nginx configuration..."
cat > $NGINX_CONFIG << EOF
# Deadlock Scores Server Configuration
server {
    listen 80;
    server_name $DOMAIN $PUBLIC_IP;

    # Rate limiting for scores API
    limit_req_zone \$binary_remote_addr zone=deadlock_api:10m rate=10r/s;

    # Deadlock Scores API
    location /deadlock/api/ {
        limit_req zone=deadlock_api burst=20 nodelay;

        # Remove /deadlock prefix when forwarding to backend
        rewrite ^/deadlock/api/(.*)\$ /api/\$1 break;

        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type' always;

        # Handle preflight requests
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # Health check for deadlock server
    location /deadlock/health {
        rewrite ^/deadlock/health\$ /health break;
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;

        # Simple response for monitoring
        access_log off;
    }

    # Info endpoint
    location /deadlock/ {
        add_header Content-Type application/json;
        return 200 '{"service":"Deadlock Scores Server","status":"running","endpoints":["/deadlock/api/scores","/deadlock/health"],"version":"1.0.0"}';
    }
}
EOF

# Test Nginx configuration
print_status "Testing Nginx configuration..."
nginx -t

# Start the application
print_status "Starting Deadlock server with PM2..."
cd $SERVER_DIR
pm2 start ecosystem.config.js
pm2 save

# Reload Nginx (not restart to avoid disrupting existing services)
print_status "Reloading Nginx..."
systemctl reload nginx

# Test the deployment
print_status "Testing deployment..."
sleep 3

# Test health check
if curl -s "http://localhost:3001/health" > /dev/null; then
    print_status "✅ Deadlock server is responding on port 3001"
else
    print_error "❌ Deadlock server is not responding"
fi

# Test through Nginx
if curl -s "http://localhost/deadlock/health" > /dev/null; then
    print_status "✅ Nginx proxy is working"
else
    print_warning "⚠️  Nginx proxy might have issues"
fi

print_status "✅ Deployment completed successfully!"
echo ""
echo "🎮 Your Deadlock Scores Server is now running!"
echo ""
echo "📍 Endpoints:"
echo "  Info:         http://$DOMAIN/deadlock/"
echo "  Health:       http://$DOMAIN/deadlock/health"
echo "  Submit Score: POST http://$DOMAIN/deadlock/api/scores"
echo "  Get Scores:   GET http://$DOMAIN/deadlock/api/scores"
echo ""
echo "🔧 Management commands:"
echo "  pm2 status"
echo "  pm2 logs deadlock-scores"
echo "  pm2 restart deadlock-scores"
echo ""
echo "📝 Test your API:"
echo "  curl http://$DOMAIN/deadlock/health"
echo "  curl http://$DOMAIN/deadlock/api/scores"
echo ""
print_warning "📋 Your existing water-keeper service is still running on /api/"
print_warning "📋 Deadlock API is available on /deadlock/api/"