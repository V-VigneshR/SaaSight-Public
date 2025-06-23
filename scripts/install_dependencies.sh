#!/bin/bash
### scripts/install_dependencies.sh ###
set -e

echo "==== Starting dependency installation at $(date) ===="

# 🧠 Step 1: Find the latest deployment-archive dir
DEPLOYMENT_DIR=$(find /opt/codedeploy-agent/deployment-root -type d -name "deployment-archive" -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)

if [ ! -d "$DEPLOYMENT_DIR" ]; then
    echo "❌ ERROR: Could not find deployment-archive directory."
    exit 1
else
    echo "📦 Using deployment directory: $DEPLOYMENT_DIR"
fi

# 🧹 Step 2: Clean old files (preserve instance folder and backups)
echo "🧹 Cleaning /home/ec2-user..."
rm -rf /home/ec2-user/{app,scripts,static,templates,tests,venv,__pycache__}
rm -f /home/ec2-user/*.{py,txt,yml}
rm -f /home/ec2-user/Procfile

# 📂 Step 3: Copy new files
echo "📂 Copying files from latest deployment..."

cp -r $DEPLOYMENT_DIR/{app,scripts,static,templates,tests} /home/ec2-user/ 2>/dev/null || true
cp $DEPLOYMENT_DIR/Procfile /home/ec2-user/ 2>/dev/null || true

# 👇 ADD THIS:
cp $DEPLOYMENT_DIR/config.py /home/ec2-user/ 2>/dev/null || {
    echo "❌ Failed to copy config.py"
    exit 1
}

# 👑 Step 4: Set permissions, ensure instance dir, activate venv
echo "🎩 Setting permissions and virtualenv..."
chown -R ec2-user:ec2-user /home/ec2-user/
mkdir -p /home/ec2-user/instance
cd /home/ec2-user
python3 -m venv venv
source venv/bin/activate

# 🧩 Step 5: Install dependencies
echo "⬇ Installing packages..."
pip install --upgrade pip
pip install -r requirements.txt

# 🛠 Step 6: Run database migrations (with rollback)
echo "🔄 Running database migrations..."
export FLASK_APP=run.py

if ! flask db upgrade; then
    echo "❌ Migration failed! Rolling back to last working database..."

    sudo systemctl stop saasight || true

    LATEST_BACKUP=$(ls -t /home/ec2-user/backups/saasight.db.backup-* 2>/dev/null | head -n1)

    if [ -f "$LATEST_BACKUP" ]; then
        echo "🛠 Restoring from: $LATEST_BACKUP"
        cp "$LATEST_BACKUP" /home/ec2-user/instance/saasight.db
        echo "✅ Backup restore completed."
    else
        echo "🚨 No backup found! Manual intervention required."
    fi

    echo "🚫 Exiting deployment due to failed migration."
    exit 1
else
    echo "✅ DB migration successful."
fi

# 🧪 Step 7: Verify app boot and gunicorn
python -c "from app import create_app; print('✅ create_app import OK')" || {
    echo "🚨 Flask app creation failed."
    exit 1
}
gunicorn --version || {
    echo "🚨 Gunicorn missing or broken."
    exit 1
}

# ⚙️ Step 8: Create systemd service
echo "⚙️ Setting up systemd service..."
sudo tee /etc/systemd/system/saasight.service > /dev/null <<EOF
[Unit]
Description=SaaSight Flask App
After=network.target

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user
Environment="PATH=/home/ec2-user/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_APP=run.py"
ExecStart=/home/ec2-user/venv/bin/gunicorn -w 3 -b 0.0.0.0:8000 --chdir /home/ec2-user run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable saasight

echo "✅ Dependency install finished at $(date)"
