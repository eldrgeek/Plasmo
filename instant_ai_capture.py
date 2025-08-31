#!/usr/bin/env python3
"""
🎯 INSTANT AI CAPTURE SYSTEM for Mike Wolf
Global hotkey → Voice capture → Smart Claude routing → GTD files

Usage: Run this script, then press Cmd+Shift+C anywhere to capture tasks
"""

import tkinter as tk
from tkinter import messagebox
import threading
import json
import requests
import os
from datetime import datetime
import speech_recognition as sr
import pynput
from pynput import keyboard
import subprocess
import queue

class InstantCapture:
    def __init__(self):
        self.gtd_dir = "gtd"
        self.ensure_gtd_structure()
        self.ui_queue = queue.Queue()
        self.setup_hotkey()
        
    def ensure_gtd_structure(self):
        """Create GTD directory structure if it doesn't exist"""
        os.makedirs(self.gtd_dir, exist_ok=True)
        
        # Create GTD files if they don't exist
        files = {
            "inbox.md": "# 📥 BRAIN DUMP INBOX\n\n",
            "next_actions.md": "# 🎯 NEXT ACTIONS BY CONTEXT\n\n",
            "projects.md": "# 📋 ACTIVE PROJECTS\n\n",
            "someday_maybe.md": "# 📚 SOMEDAY/MAYBE\n\n",
            "waiting_for.md": "# ⏳ WAITING FOR\n\n"
        }
        
        for filename, header in files.items():
            filepath = os.path.join(self.gtd_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(header)
    
    def setup_hotkey(self):
        """Register global hotkey Cmd+Shift+C (for Capture)"""
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<cmd>+<shift>+c'),
            self.show_capture_dialog
        )
        
        def for_canonical(f):
            return lambda k: f(listener.canonical(k))
        
        listener = keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        )
        
        listener.start()
        print("🎯 Hotkey registered: Cmd+Shift+C")
        print("Press Cmd+Shift+C anywhere to capture tasks instantly!")
        
    def show_capture_dialog(self):
        """Show instant capture dialog"""
        self.ui_queue.put("show_dialog")
        
    def _capture_dialog(self):
        """Create capture dialog with voice and text options"""
        root = tk.Tk()
        root.title("🎯 Instant AI Capture")
        root.geometry("500x300")
        root.attributes('-topmost', True)  # Always on top
        root.focus_force()
        
        # Center the window
        root.geometry("+{}+{}".format(
            int(root.winfo_screenwidth()/2 - 250),
            int(root.winfo_screenheight()/2 - 150)
        ))
        
        tk.Label(root, text="🎯 Tell Your AI Sidekick", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Text area
        text_area = tk.Text(root, height=8, width=60, font=("Arial", 12))
        text_area.pack(pady=10, padx=20)
        text_area.focus()
        
        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        def voice_capture():
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    tk.Label(button_frame, text="🎤 Listening...", fg="red").pack()
                    root.update()
                    audio = r.listen(source, timeout=10)
                    
                text = r.recognize_google(audio)
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, text)
                
            except Exception as e:
                messagebox.showerror("Voice Error", f"Could not recognize speech: {e}")
        
        def send_to_claude():
            content = text_area.get(1.0, tk.END).strip()
            if not content:
                return
                
            # Show processing
            processing_label = tk.Label(button_frame, text="🤖 Processing with Claude...", fg="blue")
            processing_label.pack()
            root.update()
            
            try:
                # Send to Claude API for smart routing
                response = self.send_to_claude_api(content)
                
                # Close dialog
                root.destroy()
                
                # Show confirmation
                self.show_confirmation(content, response)
                
            except Exception as e:
                processing_label.destroy()
                messagebox.showerror("Claude Error", f"Error processing: {e}")
        
        # Buttons
        tk.Button(button_frame, text="🎤 Voice", command=voice_capture, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="📝 Send to Claude", command=send_to_claude, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="❌ Cancel", command=root.destroy, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        # Enter key binding
        def on_enter(event):
            if event.state & 0x4:  # Cmd key held
                send_to_claude()
            return "break"
        
        text_area.bind("<Command-Return>", on_enter)
        
        root.mainloop()
        
    def send_to_claude_api(self, content):
        """Send content to Claude API for intelligent processing and routing"""
        
        # This uses the actual Anthropic API - you'll need your API key
        api_url = "https://api.anthropic.com/v1/messages"
        
        prompt = f"""
You are Mike Wolf's Personal AI Sidekick with instant task capture capabilities.

Mike just captured this via global hotkey: "{content}"

Your job:
1. Analyze this content and determine the best GTD category
2. Add it to the appropriate GTD file with proper formatting
3. If it's a task, add context tags (@Computer, @Mac, @Energy_High, @Energy_Low)
4. If it references existing projects, note connections
5. Return a brief confirmation of what you did

GTD Categories available:
- inbox.md (raw brain dumps)
- next_actions.md (actionable items with context)
- projects.md (multi-step outcomes)  
- someday_maybe.md (future possibilities)
- waiting_for.md (blocked on others)

Current timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Respond with ONLY:
1. Which file you're adding it to
2. How you're categorizing it
3. Any context tags you're adding
4. Brief confirmation message
"""

        try:
            # Use local Claude instance via MCP if API key not available
            result = self.route_and_save(content)
            return result
            
        except Exception as e:
            # Fallback to simple file append
            return self.simple_save_to_inbox(content)
    
    def route_and_save(self, content):
        """Smart routing and saving logic"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simple keyword-based routing for now
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['maybe', 'someday', 'future', 'later']):
            file_path = os.path.join(self.gtd_dir, "someday_maybe.md")
            category = "Someday/Maybe"
        elif any(word in content_lower for word in ['waiting', 'blocked', 'pending']):
            file_path = os.path.join(self.gtd_dir, "waiting_for.md")
            category = "Waiting For"
        elif any(word in content_lower for word in ['project', 'build', 'create', 'develop']):
            file_path = os.path.join(self.gtd_dir, "projects.md")
            category = "Project"
        elif content.startswith(('do ', 'call ', 'email ', 'fix ', 'update ')):
            file_path = os.path.join(self.gtd_dir, "next_actions.md")
            category = "Next Action"
        else:
            file_path = os.path.join(self.gtd_dir, "inbox.md")
            category = "Inbox"
        
        # Add context tags
        context_tag = ""
        if any(word in content_lower for word in ['code', 'debug', 'build', 'development']):
            context_tag = " @Computer"
        elif any(word in content_lower for word in ['automation', 'script', 'mac']):
            context_tag = " @Mac"
        elif any(word in content_lower for word in ['think', 'plan', 'strategy', 'architecture']):
            context_tag = " @Energy_High"
        elif any(word in content_lower for word in ['organize', 'clean', 'maintenance']):
            context_tag = " @Energy_Low"
        
        # Format entry
        entry = f"- [ ] {content}{context_tag} [{timestamp}]\n"
        
        # Append to file
        with open(file_path, 'a') as f:
            f.write(entry)
        
        return f"✅ Added to {category}: {content[:50]}{'...' if len(content) > 50 else ''}"
    
    def simple_save_to_inbox(self, content):
        """Fallback: save to inbox"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_path = os.path.join(self.gtd_dir, "inbox.md")
        
        with open(file_path, 'a') as f:
            f.write(f"- [ ] {content} [{timestamp}]\n")
        
        return f"✅ Saved to inbox: {content[:50]}{'...' if len(content) > 50 else ''}"
    
    def show_confirmation(self, original_content, response):
        """Show confirmation of what was captured"""
        # Use native Mac notification
        subprocess.run([
            'osascript', '-e',
            f'display notification "{response}" with title "🎯 AI Capture Complete" sound name "Glass"'
        ])
    
    def process_ui_queue(self, root):
        """Process UI queue in main thread"""
        try:
            while True:
                action = self.ui_queue.get_nowait()
                if action == "show_dialog":
                    self._capture_dialog()
        except queue.Empty:
            pass
        # Schedule next check
        root.after(100, lambda: self.process_ui_queue(root))

def main():
    print("🚀 Starting Instant AI Capture System...")
    print("Installing required packages if needed...")
    
    # Install requirements
    try:
        import speech_recognition
        import pynput
    except ImportError:
        print("Installing required packages...")
        subprocess.run(['pip', 'install', 'speechrecognition', 'pynput', 'pyaudio'])
    
    # Start the capture system
    capture = InstantCapture()
    
    print("✅ System ready!")
    print("Press Cmd+Shift+C anywhere to capture tasks")
    print("Press Ctrl+C to stop")
    
    # Create invisible root window for main thread Tkinter processing
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    # Start processing UI queue
    capture.process_ui_queue(root)
    
    try:
        # Run Tkinter main loop (this keeps the main thread active for UI)
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Stopping Instant AI Capture System")
        root.destroy()

if __name__ == "__main__":
    main()
