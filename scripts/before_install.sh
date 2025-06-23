#!/bin/bash
### scripts/before_install.sh ###
set -e

echo "🔒 Starting pre-installation steps..."

# Create database backup
echo "💾 Backing up database..."
sudo systemctl stop saasight || true
mkdir -p /home/ec2-user/backups
cp /home/ec2-user/instance/saasight.db /home/ec2-user/backups/saasight.db.backup-$(date +%Y%m%d-%H%M%S)
sudo systemctl start saasight || true

echo "✅ Pre-installation completed!"