#!/bin/bash

DATE=$(date +%Y-%m-%d)
ARCHIVE="vboarder_reports/archives/ops_archive_${DATE}.tar.gz"

mkdir -p vboarder_reports/archives

if compgen -G "vboarder_reports/ops_summary_${DATE}_*" > /dev/null; then
  tar -czf "$ARCHIVE" vboarder_reports/ops_summary_${DATE}_*
  rm -f vboarder_reports/ops_summary_${DATE}_*
  echo "✅ Archived and cleaned up ops summaries for $DATE"
else
  echo "⚠️ No ops summary files found for $DATE"
fi
