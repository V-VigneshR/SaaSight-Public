### start_server.sh ###
#!/bin/bash
set -e

echo "Starting SaaSight service..."
cd /home/ec2-user
source venv/bin/activate

# Health check
python -c "from app import create_app; print('✓ app import OK')"
gunicorn --check-config -w 1 -b 127.0.0.1:8001 run:app

# Restart service
sudo systemctl daemon-reload
sudo systemctl stop saasight || true
sleep 2
sudo systemctl start saasight
sleep 5

# Verify service
if systemctl is-active --quiet saasight; then
    echo "✓ SaaSight is active"
    curl -fs http://localhost:8000 && echo "✓ HTTP OK" || echo "⚠ HTTP FAIL"
else
    echo "✗ SaaSight failed"
    sudo journalctl -u saasight --no-pager -l --since "5 min ago"
    exit 1
fi

echo "✓ Server startup completed!"
