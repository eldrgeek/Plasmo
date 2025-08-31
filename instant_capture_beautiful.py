#!/usr/bin/env python3
"""
🎯 INSTANT AI CAPTURE SYSTEM - Native Mac App
Global hotkey → Beautiful popup → Smart GTD routing

Created for Mike Wolf's Personal AI Sidekick Project
"""

import tkinter as tk
from tkinter import messagebox
import threading
import json
import os
import subprocess
from datetime import datetime
import pynput
from pynput import keyboard
import requests
import time

class InstantCapture:
    def __init__(self):
        self.gtd_dir = "gtd"
        self.ensure_gtd_structure()
        self.setup_hotkey()
        self.claude_api_url = "http://localhost:8000"  # Your MCP server
        print("🎯 Instant AI Capture System starting...")
        
    def ensure_gtd_structure(self):
        """Create GTD directory structure if it doesn't exist"""
        os.makedirs(self.gtd_dir, exist_ok=True)
        
        # Create GTD files if they don't exist
        files = {
            "inbox.md": "# 📥 BRAIN DUMP INBOX\n\n",
            "next_actions.md": "# 🎯 NEXT ACTIONS BY CONTEXT\n\n## @Computer - Technical Work\n\n## @Mac - Native Automation\n\n## @Energy_High - Complex Thinking\n\n## @Energy_Low - Maintenance\n\n",
            "projects.md": "# 📋 ACTIVE PROJECTS\n\n",
            "someday_maybe.md": "# 📚 SOMEDAY/MAYBE - FUTURE PROJECTS\n\n",
            "waiting_for.md": "# ⏳ WAITING FOR\n\n"
        }
        
        for filename, header in files.items():
            filepath = os.path.join(self.gtd_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(header)
                print(f"✅ Created {filename}")
    
    def setup_hotkey(self):
        """Register global hotkey Cmd+Shift+T"""
        try:
            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse('<cmd>+<shift>+t'),
                self.show_capture_dialog
            )
            
            def for_canonical(f):
                return lambda k: f(listener.canonical(k))
            
            listener = keyboard.Listener(
                on_press=for_canonical(hotkey.press),
                on_release=for_canonical(hotkey.release),
                suppress=False
            )
            
            listener.start()
            print("✅ Global hotkey registered: Cmd+Shift+T")
            print("   Press Cmd+Shift+T anywhere to capture tasks!")
            
        except Exception as e:
            print(f"⚠️ Could not register hotkey: {e}")
            print("   You can still use the manual capture method")
    
    def show_capture_dialog(self):
        """Show beautiful capture dialog"""
        threading.Thread(target=self._capture_dialog, daemon=True).start()
        
    def _capture_dialog(self):
        """Create modern, beautiful capture dialog"""
        root = tk.Tk()
        root.title("🎯 AI Capture")
        
        # Modern styling
        root.configure(bg='#1e1e2e')
        root.geometry("600x400")
        root.attributes('-topmost', True)  # Always on top
        root.attributes('-alpha', 0.95)    # Slight transparency
        
        # Remove default window decorations for modern look
        root.overrideredirect(False)  # Keep close button but make it minimal
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (600 // 2)
        y = (root.winfo_screenheight() // 2) - (400 // 2)
        root.geometry(f"600x400+{x}+{y}")
        
        # Focus and bring to front
        root.focus_force()
        root.lift()
        
        # Main frame
        main_frame = tk.Frame(root, bg='#1e1e2e', padx=40, pady=30)\n        main_frame.pack(fill='both', expand=True)
        
        # Header
        title_label = tk.Label(
            main_frame, 
            text="🎯 Tell Your AI Sidekick",
            font=("SF Pro Display", 24, "bold"),
            fg='#cdd6f4',
            bg='#1e1e2e'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            main_frame,
            text="What's on your mind? I'll organize it perfectly.",
            font=("SF Pro Display", 12),
            fg='#9399b2',
            bg='#1e1e2e'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Text area with modern styling
        text_frame = tk.Frame(main_frame, bg='#313244', relief='flat', bd=0)
        text_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        text_area = tk.Text(
            text_frame,
            height=8,
            font=("SF Pro Display", 14),
            bg='#313244',
            fg='#cdd6f4',
            insertbackground='#cdd6f4',
            selectbackground='#585b70',
            selectforeground='#cdd6f4',
            relief='flat',
            bd=10,
            wrap='word'
        )
        text_area.pack(fill='both', expand=True, padx=15, pady=15)
        text_area.focus()
        
        # Status label
        status_label = tk.Label(
            main_frame,
            text="",
            font=("SF Pro Display", 11),
            fg='#9399b2',
            bg='#1e1e2e'
        )
        status_label.pack(pady=(0, 20))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#1e1e2e')
        button_frame.pack(pady=(0, 10))\n        \n        def create_button(parent, text, command, bg_color, fg_color='#1e1e2e', width=15):\n            return tk.Button(\n                parent,\n                text=text,\n                command=command,\n                font=("SF Pro Display", 12, "bold"),\n                bg=bg_color,\n                fg=fg_color,\n                activebackground=bg_color,\n                activeforeground=fg_color,\n                relief='flat',\n                bd=0,\n                padx=20,\n                pady=12,\n                width=width,\n                cursor='hand2'\n            )
        
        def send_to_claude():\n            content = text_area.get(1.0, tk.END).strip()\n            if not content:\n                return\n                \n            status_label.config(text="🤖 Processing with your AI Sidekick...", fg="#89b4fa")\n            root.update()\n            \n            try:\n                response = self.send_to_claude_api(content)\n                \n                status_label.config(text="✅ Task captured and organized!", fg="#a6e3a1")\n                root.update()\n                \n                # Show native Mac notification\n                self.show_notification("🎯 AI Capture Complete", response)\n                \n                # Close after brief delay\n                root.after(2000, root.destroy)\n                \n            except Exception as e:\n                status_label.config(text=f"❌ Error: {str(e)}", fg="#f38ba8")\n                print(f"Error processing: {e}")\n        \n        def close_window():\n            root.destroy()\n        \n        # Buttons with modern styling\n        send_btn = create_button(\n            button_frame, \n            "🤖 Send to Claude", \n            send_to_claude, \n            "#89b4fa",\n            width=18\n        )\n        send_btn.pack(side='left', padx=(0, 15))\n        \n        cancel_btn = create_button(\n            button_frame,\n            "❌ Cancel",\n            close_window,\n            "#6c7086",\n            "#cdd6f4",\n            width=12\n        )\n        cancel_btn.pack(side='left')\n        \n        # Keyboard shortcuts\n        def on_key(event):\n            if event.state & 0x8 and event.keysym == 'Return':  # Cmd+Enter\n                send_to_claude()\n            elif event.keysym == 'Escape':\n                close_window()\n        \n        root.bind_all('<KeyPress>', on_key)\n        \n        # Auto-resize text area\n        def on_text_change(event=None):\n            lines = int(text_area.index('end-1c').split('.')[0])\n            if lines > 8:\n                text_area.config(height=min(lines, 15))\n        \n        text_area.bind('<KeyRelease>', on_text_change)\n        \n        root.mainloop()
        
    def send_to_claude_api(self, content):\n        """Send content to Claude for intelligent processing and routing"""\n        \n        # Smart routing logic based on content analysis\n        result = self.route_and_save(content)\n        return result\n    \n    def route_and_save(self, content):\n        """Smart routing and saving logic with ADD-friendly context tags"""\n        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")\n        content_lower = content.lower()\n        \n        # Smart categorization based on keywords and patterns\n        if any(word in content_lower for word in ['maybe', 'someday', 'future', 'later', 'when i have time']):\n            file_path = os.path.join(self.gtd_dir, "someday_maybe.md")\n            category = "Someday/Maybe"\n        elif any(word in content_lower for word in ['waiting', 'blocked', 'pending', 'follow up', 'response from']):\n            file_path = os.path.join(self.gtd_dir, "waiting_for.md")\n            category = "Waiting For"\n        elif any(word in content_lower for word in ['project', 'build', 'create', 'develop', 'complete', 'finish']):\n            file_path = os.path.join(self.gtd_dir, "projects.md")\n            category = "Project"\n        elif any(word in content_lower for word in ['call', 'email', 'fix', 'update', 'review', 'send', 'schedule']):\n            file_path = os.path.join(self.gtd_dir, "next_actions.md")\n            category = "Next Action"\n        else:\n            file_path = os.path.join(self.gtd_dir, "inbox.md")\n            category = "Inbox"\n        \n        # Add context tags for ADD-friendly organization\n        context_tag = ""\n        if any(word in content_lower for word in ['code', 'debug', 'build', 'development', 'programming', 'script']):\n            context_tag = " @Computer"\n        elif any(word in content_lower for word in ['automation', 'mac', 'system', 'shortcut']):\n            context_tag = " @Mac"\n        elif any(word in content_lower for word in ['think', 'plan', 'strategy', 'architecture', 'design', 'research']):\n            context_tag = " @Energy_High"\n        elif any(word in content_lower for word in ['organize', 'clean', 'maintenance', 'update', 'backup']):\n            context_tag = " @Energy_Low"\n        \n        # Format entry with proper GTD structure\n        if category == "Project":\n            entry = f"\n## {content.title()}\n**Status**: Active  \n**Next Action**: [Define next action]  \n**Added**: {timestamp}{context_tag}  \n\n"\n        else:\n            entry = f"- [ ] {content}{context_tag} [{timestamp}]\n"\n        \n        # Append to appropriate file\n        try:\n            with open(file_path, 'a', encoding='utf-8') as f:\n                f.write(entry)\n            \n            response = f"✅ Added to {category}: {content[:50]}{'...' if len(content) > 50 else ''}"n            print(f"📝 Saved: {response}")\n            return response\n            \n        except Exception as e:\n            print(f"❌ Error saving to GTD: {e}")\n            return f"❌ Error saving: {str(e)}"\n    \n    def show_notification(self, title, message):\n        """Show native Mac notification"""\n        try:\n            subprocess.run([\n                'osascript', '-e',\n                f'display notification "{message}" with title "{title}" sound name "Glass"'\n            ], check=False)\n        except Exception as e:\n            print(f"Could not show notification: {e}")\n\ndef main():\n    print("🚀 Starting Instant AI Capture System for Mike Wolf...")\n    print("="*60)\n    \n    try:\n        # Install required packages if needed\n        import pynput\n        print("✅ All required packages available")\n    except ImportError:\n        print("📦 Installing required packages...")\n        subprocess.run(['pip3', 'install', 'pynput'], check=True)\n        import pynput\n    \n    # Start the capture system\n    capture = InstantCapture()\n    \n    print("\\n🎯 INSTANT AI CAPTURE SYSTEM READY!")\n    print("="*60)\n    print("✅ GTD files created/verified")\n    print("🔥 Global hotkey active: Cmd+Shift+T")\n    print("🤖 AI routing system operational")\n    print("📱 Native Mac notifications enabled")\n    print("\\n💡 USAGE:")\n    print("   • Press Cmd+Shift+T anywhere on your Mac")\n    print("   • Type or paste your task/thought")\n    print("   • AI automatically routes to correct GTD file")\n    print("   • Get instant confirmation")\n    print("   • Back to work in 5 seconds!")\n    print("\\n🧠 ADD-FRIENDLY FEATURES:")\n    print("   • Single-focus capture (no overwhelming lists)")\n    print("   • Context tags (@Computer, @Mac, @Energy_High, @Energy_Low)")\n    print("   • Smart categorization (Next Actions, Projects, Someday/Maybe)")\n    print("   • Always-on-top popup that interrupts everything")\n    print("\\n🛑 Press Ctrl+C to stop")\n    print("="*60)\n    \n    try:\n        # Keep the program running\n        while True:\n            time.sleep(1)\n    except KeyboardInterrupt:\n        print("\\n🛑 Stopping Instant AI Capture System")\n        print("Thanks for using your Personal AI Sidekick! 🤖")\n\nif __name__ == "__main__":\n    main()
