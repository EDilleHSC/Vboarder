#!/usr/bin/env python3
"""
Log and Memory File Cleanup Script for VBoarder
Handles rotation and archival of log files and old memory files.
"""
import gzip
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent
LOGS_DIR = PROJECT_ROOT / "logs"
AGENTS_DIR = PROJECT_ROOT / "agents"
ARCHIVE_DIR = PROJECT_ROOT / "archive" / "logs"
MEMORY_ARCHIVE_DIR = PROJECT_ROOT / "archive" / "memory"

# Retention policies
LOG_RETENTION_DAYS = 30  # Keep logs for 30 days
MEMORY_RETENTION_DAYS = 90  # Keep memory files for 90 days
COMPRESS_AFTER_DAYS = 7  # Compress files older than 7 days

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("cleanup")


def compress_file(file_path: Path) -> Path:
    """Compress a file using gzip and return the compressed file path."""
    gz_path = file_path.with_suffix(file_path.suffix + ".gz")

    if gz_path.exists():
        log.info(f"  Skipping {file_path.name} - already compressed")
        return gz_path

    with open(file_path, "rb") as f_in:
        with gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    file_path.unlink()  # Remove original
    log.info(f"  Compressed {file_path.name} -> {gz_path.name}")
    return gz_path


def get_file_age_days(file_path: Path) -> int:
    """Get the age of a file in days."""
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - mtime
    return age.days


def cleanup_logs():
    """Clean up old log files."""
    log.info("🧹 Cleaning up log files...")

    if not LOGS_DIR.exists():
        log.info("  No logs directory found, skipping")
        return

    compressed_count = 0
    archived_count = 0
    deleted_count = 0

    for log_file in LOGS_DIR.glob("*.log*"):
        if log_file.is_dir():
            continue

        age_days = get_file_age_days(log_file)

        # Delete very old files
        if age_days > LOG_RETENTION_DAYS:
            log_file.unlink()
            deleted_count += 1
            log.info(f"  Deleted old log: {log_file.name} ({age_days} days old)")
            continue

        # Compress files older than threshold
        if age_days > COMPRESS_AFTER_DAYS and not log_file.name.endswith(".gz"):
            compressed_path = compress_file(log_file)
            compressed_count += 1

            # Move to archive if very old
            if age_days > LOG_RETENTION_DAYS // 2:
                ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
                archive_path = ARCHIVE_DIR / compressed_path.name
                compressed_path.rename(archive_path)
                archived_count += 1
                log.info(f"  Archived {compressed_path.name}")

    log.info(
        f"  ✅ Logs: {compressed_count} compressed, {archived_count} archived, {deleted_count} deleted"
    )


def cleanup_agent_memory():
    """Clean up old agent memory backup files."""
    log.info("🧹 Cleaning up agent memory files...")

    if not AGENTS_DIR.exists():
        log.info("  No agents directory found, skipping")
        return

    compressed_count = 0
    archived_count = 0

    for agent_dir in AGENTS_DIR.glob("*/"):
        if not agent_dir.is_dir():
            continue

        # Look for .jsonl files (append-only logs)
        for memory_file in agent_dir.glob("memory.jsonl*"):
            age_days = get_file_age_days(memory_file)

            # Compress old .jsonl files
            if age_days > COMPRESS_AFTER_DAYS and not memory_file.name.endswith(".gz"):
                compressed_path = compress_file(memory_file)
                compressed_count += 1

                # Move to archive
                if age_days > MEMORY_RETENTION_DAYS // 2:
                    agent_archive = MEMORY_ARCHIVE_DIR / agent_dir.name
                    agent_archive.mkdir(parents=True, exist_ok=True)
                    archive_path = agent_archive / compressed_path.name
                    compressed_path.rename(archive_path)
                    archived_count += 1
                    log.info(f"  Archived {agent_dir.name}/{ compressed_path.name}")

    log.info(f"  ✅ Memory: {compressed_count} compressed, {archived_count} archived")


def cleanup_old_conversations():
    """Clean up old conversation files."""
    log.info("🧹 Cleaning up old conversation files...")

    conv_dir = PROJECT_ROOT / "data" / "conversations"
    if not conv_dir.exists():
        log.info("  No conversations directory found, skipping")
        return

    deleted_count = 0

    for conv_file in conv_dir.glob("*.json"):
        age_days = get_file_age_days(conv_file)

        if age_days > MEMORY_RETENTION_DAYS:
            conv_file.unlink()
            deleted_count += 1
            log.info(
                f"  Deleted old conversation: {conv_file.name} ({age_days} days old)"
            )

    log.info(f"  ✅ Conversations: {deleted_count} deleted")


def disk_usage_report():
    """Report disk usage for key directories."""
    log.info("📊 Disk Usage Report:")

    dirs_to_check = [
        LOGS_DIR,
        AGENTS_DIR,
        PROJECT_ROOT / "data",
        ARCHIVE_DIR,
    ]

    for dir_path in dirs_to_check:
        if not dir_path.exists():
            continue

        total_size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())

        size_mb = total_size / (1024 * 1024)
        log.info(f"  {dir_path.name}: {size_mb:.2f} MB")


def main():
    """Run all cleanup tasks."""
    log.info("=" * 60)
    log.info("🚀 VBoarder Cleanup Script Starting")
    log.info("=" * 60)

    try:
        cleanup_logs()
        cleanup_agent_memory()
        cleanup_old_conversations()
        disk_usage_report()

        log.info("=" * 60)
        log.info("✅ Cleanup completed successfully")
        log.info("=" * 60)
    except Exception as e:
        log.error(f"❌ Cleanup failed: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
