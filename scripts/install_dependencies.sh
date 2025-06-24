#!/bin/bash
### scripts/install_dependencies.sh ###
set -e

echo "==== Starting dependency installation at $(date) ===="

# 🐍 Step 0: Install Python 3.12 if not available
echo "🐍 Ensuring Python 3.12 is available..."
if ! command -v python3.12 &> /dev/null; then
    echo "📦 Installing Python 3.12..."
    if command -v dnf &> /dev/null; then
        # Amazon Linux 2023
        sudo dnf update -y
        sudo dnf install -y python3.12 python3.12-pip python3.12-devel
    elif command -v yum &> /dev/null; then
        # Amazon Linux 2 - install from source
        sudo yum update -y
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel wget
        
        cd /tmp
        wget https://www.python.org/ftp/python/3.12.4/Python-3.12.4.tgz
        tar xzf Python-3.12.4.tgz
        cd Python-3.12.4
        ./configure --enable-optimizations --prefix=/usr/local
        make -j$(nproc)
        sudo make altinstall
        
        # Create symlinks
        sudo ln -sf /usr/local/bin/python3.12 /usr/bin/python3.12
        sudo ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3.12
    else
        echo "❌ Unsupported package manager"
        exit 1
    fi
else
    echo "✅ Python 3.12 already available"
fi

# Verify Python 3.12 installation
python3.12 --version

# 🧠 Step 1: Identify deployment archive location
DEPLOYMENT_DIR=$(find /opt/codedeploy-agent/deployment-root -name "appspec.yml" | head -1 | xargs dirname)
echo "📍 Deployment directory: $DEPLOYMENT_DIR"

if [ ! -d "$DEPLOYMENT_DIR" ]; then
    echo "❌ Deployment directory not found"
    exit 1
fi

echo "📦 Using deployment directory: $DEPLOYMENT_DIR"
echo "🔍 Files in deployment directory:"
ls -la "$DEPLOYMENT_DIR"

# 🧹 Step 2: Clean old app files (preserve backups)
echo "🧹 Cleaning /home/ec2-user..."
rm -rf /home/ec2-user/{app,scripts,static,templates,tests,venv,__pycache__,migrations}
rm -f /home/ec2-user/*.{py,txt,yml}

# 📂 Step 3: Copy application files and handle database
echo "📂 Copying application files..."
# Ensure instance directory exists with correct permissions
mkdir -p /home/ec2-user/instance
chmod 775 /home/ec2-user/instance

for item in app scripts static templates tests migrations config.py requirements.txt run.py appspec.yml Procfile runtime.txt; do
    if [ -e "$DEPLOYMENT_DIR/$item" ]; then
        cp -r "$DEPLOYMENT_DIR/$item" /home/ec2-user/
        echo "✅ Copied: $item"
    fi
done

# Database handling with proper fallbacks
if [ -f "$DEPLOYMENT_DIR/instance/saasight.db" ]; then
    # Case 1: Database exists in deployment package
    cp "$DEPLOYMENT_DIR/instance/saasight.db" /home/ec2-user/instance/
    echo "✅ Copied database from deployment package"
elif [ -f "/home/ec2-user/instance/saasight.db" ]; then
    # Case 2: Existing database in correct location
    echo "✅ Using existing database in instance directory"
elif [ -f "/home/ec2-user/saasight.db" ]; then
    # Case 3: Database in root directory (legacy)
    mv /home/ec2-user/saasight.db /home/ec2-user/instance/
    echo "⚠️ Moved legacy database to instance directory"
else
    # Case 4: No database exists
    touch /home/ec2-user/instance/saasight.db
    echo "ℹ️ Created new database file"
fi

# Set strict permissions
chown ec2-user:ec2-user /home/ec2-user/instance/saasight.db
chmod 664 /home/ec2-user/instance/saasight.db

# Verify critical files
echo "🔍 Verifying critical files:"
for file in config.py requirements.txt run.py; do
    if [ -f "/home/ec2-user/$file" ]; then
        echo "✅ $file - OK"
    else
        echo "❌ $file - MISSING"
        exit 1
    fi
done

# 👑 Step 4: Create virtualenv
echo "🎩 Setting up virtualenv..."
cd /home/ec2-user
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
python --version
echo "✅ Virtual environment created"

# 🧩 Step 5: Install dependencies
echo "⬇ Installing packages..."
pip install --upgrade pip
pip install -r requirements.txt || {
    echo "🚨 Failed to install Python dependencies."
    exit 1
}

# 🛠 Step 6: Database migrations with backup
echo "🔄 Running database migrations..."
export FLASK_APP=run.py

# Create backup before migration
mkdir -p /home/ec2-user/backups
BACKUP_FILE="/home/ec2-user/backups/saasight.db.backup-$(date +%Y%m%d%H%M%S)"
cp /home/ec2-user/instance/saasight.db "$BACKUP_FILE"
echo "✅ Created backup: $BACKUP_FILE"

if ! flask db upgrade; then
    echo "❌ Migration failed! Restoring backup..."
    cp "$BACKUP_FILE" /home/ec2-user/instance/saasight.db
    echo "✅ Backup restored"
    exit 1
else
    echo "✅ DB migration successful"
fi

# 🧪 Step 7: Verify setup
python -c "from app import create_app; print('✅ create_app import OK')" || {
    echo "🚨 Flask app creation failed."
    exit 1
}

gunicorn --version || {
    echo "🚨 Gunicorn not installed."
    exit 1
}

# ⚙️ Step 8: Configure systemd service
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
Environment="FLASK_ENV=production"
# Explicit database path
Environment="DATABASE_PATH=/home/ec2-user/instance/saasight.db"
ExecStart=/home/ec2-user/venv/bin/gunicorn -w 3 -b 0.0.0.0:8000 --chdir /home/ec2-user run:app
Restart=always
RestartSec=5

# Ensure permissions are set on start
ExecStartPre=/bin/chown -R ec2-user:ec2-user /home/ec2-user/instance
ExecStartPre=/bin/chmod 664 /home/ec2-user/instance/saasight.db

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable saasight

echo "✅ Dependency install finished at $(date)"