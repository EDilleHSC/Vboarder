#!/bin/bash
set -e

# Base directory for the agents
BASE_DIR="/mnt/d/ai/projects/vboarder/agents"

# Timestamp for the archive
STAMP=$(date +"%Y%m%d_%H%M%S")

# Where backups will be stored
BACKUP_DIR="$BASE_DIR/tools/backups"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Compress the entire agents directory into a tar.gz file
tar --exclude="tools/backups" -czf "$BACKUP_DIR/agents_${STAMP}.tar.gz" -C "$BASE_DIR" .

echo "💾 Backup complete → $BACKUP_DIR/agents_${STAMP}.tar.gz"
