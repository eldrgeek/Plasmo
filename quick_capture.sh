#!/bin/bash

# Quick GTD capture script for Mike Wolf
# Usage: ./quick_capture.sh "task description"

TASK="$1"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
GTD_FILE="gtd/brain_dump_inbox.md"

# Create GTD directory if it doesn't exist
mkdir -p gtd

# Add task to inbox
echo "- [ ] $TASK [$TIMESTAMP]" >> "$GTD_FILE"
echo "✅ Captured: $TASK"

# Show recent captures
echo ""
echo "Recent captures:"
tail -5 "$GTD_FILE"
