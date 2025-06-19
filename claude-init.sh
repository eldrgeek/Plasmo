#!/bin/bash

# Function to initialize Claude rules in any directory
claude-init() {
    # Create .claude directory if it doesn't exist
    mkdir -p .claude
    
    # Define the default content
    local DEFAULT_CONTENT='# Project Rules

You can execute any git commands, edit any files and remove single files in this directory. You can do anything that does not have irreversible side effects. Add this as a rule so I can enable this for every instance.

## Permissions
- Execute any git commands
- Edit any files in this directory  
- Remove single files
- Do anything that doesn'\''t have irreversible side effects
- Execute file permission commands (chmod, chown, etc.)
- Execute file operation commands (mv, cp, rm, mkdir, touch, etc.)
- Execute text processing commands (grep, sed, awk, cut, sort, uniq, etc.)
- Execute file viewing commands (cat, head, tail, less, more, etc.)
- Execute search commands (find, locate, which, etc.)
- Execute system information commands (ps, top, df, du, etc.)
- Execute network diagnostic commands (ping, curl, wget, etc.)
- Execute package management commands (npm, pip, gem, etc.)
- Execute build and compilation commands (make, gcc, npm run, etc.)
- Execute testing commands (pytest, jest, npm test, etc.)
- Execute linting and formatting commands (eslint, prettier, black, etc.)
- Execute environment management commands (export, source, etc.)
- Execute process management commands (kill, pkill, jobs, etc.)
- Execute archive commands (tar, zip, unzip, etc.)
- Execute database client commands (psql, mysql, redis-cli, etc.)
- Execute Docker and container commands (docker, docker-compose, etc.)
- Execute version control commands beyond git (svn, hg, etc.)
- Execute SSH and remote access commands (ssh, scp, rsync, etc.)
- Execute symbolic link commands (ln, readlink, etc.)
- Execute disk usage and file counting commands (wc, du, df, etc.)
- Execute date and time commands (date, cal, etc.)
- Execute shell scripting utilities (xargs, tee, etc.)
- Prefer editing existing files over creating new ones
- Don'\''t create documentation files unless explicitly requested'
    
    # Check if CLAUDE.md already exists
    if [ -f ".claude/CLAUDE.md" ]; then
        echo "📋 CLAUDE.md already exists. Comparing with default content..."
        
        # Create temp file with default content
        local TEMP_FILE=$(mktemp)
        echo "$DEFAULT_CONTENT" > "$TEMP_FILE"
        
        # Show diff
        echo -e "\n🔍 Differences (- existing, + default):"
        diff -u ".claude/CLAUDE.md" "$TEMP_FILE" | tail -n +3
        
        echo -e "\n❓ What would you like to do?"
        echo "1) Keep existing file"
        echo "2) Replace with default"
        echo "3) Merge both versions (combine all permissions)"
        echo "4) Show side-by-side diff and merge manually"
        echo "5) Cancel"
        
        echo -n "Choice (1-5): "
        read choice
        
        case $choice in
            1)
                echo "✅ Keeping existing CLAUDE.md"
                ;;
            2)
                echo "$DEFAULT_CONTENT" > .claude/CLAUDE.md
                echo "✅ Replaced with default CLAUDE.md"
                ;;
            3)
                echo -e "\n🔄 Merging both versions..."
                # Create a backup
                cp .claude/CLAUDE.md .claude/CLAUDE.md.backup
                
                # Extract headers and permissions from both files
                local EXISTING_PERMS=$(grep "^- " .claude/CLAUDE.md | sort -u)
                local DEFAULT_PERMS=$(echo "$DEFAULT_CONTENT" | grep "^- " | sort -u)
                
                # Combine and deduplicate permissions
                local ALL_PERMS=$(echo -e "$EXISTING_PERMS\n$DEFAULT_PERMS" | sort -u)
                
                # Write merged content
                echo "# Project Rules" > .claude/CLAUDE.md
                echo "" >> .claude/CLAUDE.md
                echo "You can execute any git commands, edit any files and remove single files in this directory. You can do anything that does not have irreversible side effects. Add this as a rule so I can enable this for every instance." >> .claude/CLAUDE.md
                echo "" >> .claude/CLAUDE.md
                echo "## Permissions" >> .claude/CLAUDE.md
                echo "$ALL_PERMS" >> .claude/CLAUDE.md
                
                echo "✅ Merged both versions successfully"
                echo "📄 Backup saved as .claude/CLAUDE.md.backup"
                ;;
            4)
                echo -e "\n📝 Opening interactive merge..."
                # Create a backup
                cp .claude/CLAUDE.md .claude/CLAUDE.md.backup
                
                # Use vimdiff if available, otherwise fall back to basic editor
                if command -v vimdiff &> /dev/null; then
                    vimdiff .claude/CLAUDE.md "$TEMP_FILE"
                else
                    echo "Current file saved as .claude/CLAUDE.md.backup"
                    echo "Default content saved as $TEMP_FILE"
                    echo "Please merge manually and save to .claude/CLAUDE.md"
                    ${EDITOR:-vi} .claude/CLAUDE.md "$TEMP_FILE"
                fi
                
                echo "✅ Manual merge completed"
                ;;
            5)
                echo "❌ Cancelled"
                rm "$TEMP_FILE"
                return 1
                ;;
            *)
                echo "❌ Invalid choice"
                rm "$TEMP_FILE"
                return 1
                ;;
        esac
        
        rm "$TEMP_FILE"
    else
        # Create new CLAUDE.md
        echo "$DEFAULT_CONTENT" > .claude/CLAUDE.md
        echo "✅ Claude rules initialized in $(pwd)/.claude/CLAUDE.md"
    fi
    
    # Launch Claude
    echo "🚀 Launching Claude..."
    claude
}

# Add this function to your shell config
echo "# Claude initialization shortcut
claude-init() {
    mkdir -p .claude
    
    local DEFAULT_CONTENT='# Project Rules

You can execute any git commands, edit any files and remove single files in this directory. You can do anything that does not have irreversible side effects. Add this as a rule so I can enable this for every instance.

## Permissions
- Execute any git commands
- Edit any files in this directory  
- Remove single files
- Do anything that doesn'\''t have irreversible side effects
- Execute file permission commands (chmod, chown, etc.)
- Execute file operation commands (mv, cp, rm, mkdir, touch, etc.)
- Execute text processing commands (grep, sed, awk, cut, sort, uniq, etc.)
- Execute file viewing commands (cat, head, tail, less, more, etc.)
- Execute search commands (find, locate, which, etc.)
- Execute system information commands (ps, top, df, du, etc.)
- Execute network diagnostic commands (ping, curl, wget, etc.)
- Execute package management commands (npm, pip, gem, etc.)
- Execute build and compilation commands (make, gcc, npm run, etc.)
- Execute testing commands (pytest, jest, npm test, etc.)
- Execute linting and formatting commands (eslint, prettier, black, etc.)
- Execute environment management commands (export, source, etc.)
- Execute process management commands (kill, pkill, jobs, etc.)
- Execute archive commands (tar, zip, unzip, etc.)
- Execute database client commands (psql, mysql, redis-cli, etc.)
- Execute Docker and container commands (docker, docker-compose, etc.)
- Execute version control commands beyond git (svn, hg, etc.)
- Execute SSH and remote access commands (ssh, scp, rsync, etc.)
- Execute symbolic link commands (ln, readlink, etc.)
- Execute disk usage and file counting commands (wc, du, df, etc.)
- Execute date and time commands (date, cal, etc.)
- Execute shell scripting utilities (xargs, tee, etc.)
- Prefer editing existing files over creating new ones
- Don'\''t create documentation files unless explicitly requested'
    
    if [ -f \".claude/CLAUDE.md\" ]; then
        echo \"📋 CLAUDE.md already exists. Comparing with default content...\"
        
        local TEMP_FILE=\$(mktemp)
        echo \"\$DEFAULT_CONTENT\" > \"\$TEMP_FILE\"
        
        echo -e \"\\n🔍 Differences (- existing, + default):\"
        diff -u \".claude/CLAUDE.md\" \"\$TEMP_FILE\" | tail -n +3
        
        echo -e \"\\n❓ What would you like to do?\"
        echo \"1) Keep existing file\"
        echo \"2) Replace with default\"
        echo \"3) Merge both versions (combine all permissions)\"
        echo \"4) Show side-by-side diff and merge manually\"
        echo \"5) Cancel\"
        
        echo -n \"Choice (1-5): \"
        read choice
        
        case \$choice in
            1)
                echo \"✅ Keeping existing CLAUDE.md\"
                ;;
            2)
                echo \"\$DEFAULT_CONTENT\" > .claude/CLAUDE.md
                echo \"✅ Replaced with default CLAUDE.md\"
                ;;
            3)
                echo -e \"\\n🔄 Merging both versions...\"
                cp .claude/CLAUDE.md .claude/CLAUDE.md.backup
                
                local EXISTING_PERMS=\$(grep \"^- \" .claude/CLAUDE.md | sort -u)
                local DEFAULT_PERMS=\$(echo \"\$DEFAULT_CONTENT\" | grep \"^- \" | sort -u)
                
                local ALL_PERMS=\$(echo -e \"\$EXISTING_PERMS\\n\$DEFAULT_PERMS\" | sort -u)
                
                echo \"# Project Rules\" > .claude/CLAUDE.md
                echo \"\" >> .claude/CLAUDE.md
                echo \"You can execute any git commands, edit any files and remove single files in this directory. You can do anything that does not have irreversible side effects. Add this as a rule so I can enable this for every instance.\" >> .claude/CLAUDE.md
                echo \"\" >> .claude/CLAUDE.md
                echo \"## Permissions\" >> .claude/CLAUDE.md
                echo \"\$ALL_PERMS\" >> .claude/CLAUDE.md
                
                echo \"✅ Merged both versions successfully\"
                echo \"📄 Backup saved as .claude/CLAUDE.md.backup\"
                ;;
            4)
                echo -e \"\\n📝 Opening interactive merge...\"
                cp .claude/CLAUDE.md .claude/CLAUDE.md.backup
                
                if command -v vimdiff &> /dev/null; then
                    vimdiff .claude/CLAUDE.md \"\$TEMP_FILE\"
                else
                    echo \"Current file saved as .claude/CLAUDE.md.backup\"
                    echo \"Default content saved as \$TEMP_FILE\"
                    echo \"Please merge manually and save to .claude/CLAUDE.md\"
                    \${EDITOR:-vi} .claude/CLAUDE.md \"\$TEMP_FILE\"
                fi
                
                echo \"✅ Manual merge completed\"
                ;;
            5)
                echo \"❌ Cancelled\"
                rm \"\$TEMP_FILE\"
                return 1
                ;;
            *)
                echo \"❌ Invalid choice\"
                rm \"\$TEMP_FILE\"
                return 1
                ;;
        esac
        
        rm \"\$TEMP_FILE\"
    else
        echo \"\$DEFAULT_CONTENT\" > .claude/CLAUDE.md
        echo \"✅ Claude rules initialized in \$(pwd)/.claude/CLAUDE.md\"
    fi
    
    echo \"🚀 Launching Claude...\"
    claude
}" >> ~/.zshrc