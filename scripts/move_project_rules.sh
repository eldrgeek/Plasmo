#!/bin/bash

# Move project-specific Cursor rule files out of .cursor/rules
# keeping only global rules (files with 'alwaysApply: true').
# Project rules are moved into .cursor/project_rules.

set -e

RULES_DIR=".cursor/rules"
PROJECT_DIR=".cursor/project_rules"

if [ ! -d "$RULES_DIR" ]; then
    echo "Directory $RULES_DIR does not exist" >&2
    exit 1
fi

mkdir -p "$PROJECT_DIR"

for file in "$RULES_DIR"/*.mdc; do
    if grep -q "alwaysApply: true" "$file"; then
        echo "Keeping global rule $(basename "$file")"
    else
        echo "Moving $(basename "$file") to project_rules"
        mv "$file" "$PROJECT_DIR/"
    fi
done

echo "Done. Project rules moved to $PROJECT_DIR"
