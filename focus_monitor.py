#!/usr/bin/env python3
"""
Focus Monitor for Personal AI Sidekick
Tracks application focus changes and can trigger accountability prompts
"""

import time
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import argparse


@dataclass
class FocusEvent:
    timestamp: datetime
    app_name: str
    duration_ms: Optional[int] = None
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'app_name': self.app_name,
            'duration_ms': self.duration_ms
        }


class FocusMonitor:
    """Monitor app focus changes and maintain working set"""
    
    def __init__(self, 
                 log_file: str = "focus_log.json",
                 working_set_file: str = "working_set.json",
                 rules_file: str = "focus_rules.json",
                 prompts_file: str = "focus_prompts.json"):
        self.log_file = log_file
        self.working_set_file = working_set_file  
        self.rules_file = rules_file
        self.prompts_file = prompts_file
        
        self.current_app = None
        self.focus_start_time = None
        self.focus_history: List[FocusEvent] = []
        self.working_set: Set[str] = set()
        self.rules = self.load_rules()
        
        # Load existing data
        self.load_working_set()
        self.load_focus_history()
    
    def get_current_app(self) -> Optional[str]:
        """Get currently focused application using AppleScript"""
        try:
            cmd = ['osascript', '-e', 'tell application "System Events" to get name of first application process whose frontmost is true']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout getting current app")
        except Exception as e:
            print(f"⚠️ Error getting current app: {e}")
        return None
    
    def load_rules(self) -> Dict:
        """Load focus monitoring rules"""
        default_rules = {
            "max_off_task_minutes": 10,
            "ignored_apps": ["Finder", "System Preferences", "Activity Monitor"],
            "distraction_apps": ["Safari", "Chrome", "Firefox", "Twitter", "Discord", "Slack"],
            "work_apps": ["Xcode", "VSCode", "Cursor", "Terminal", "iTerm", "Claude"],
            "check_interval_seconds": 30,
            "prompt_after_distraction_minutes": 5
        }
        
        try:
            with open(self.rules_file, 'r') as f:
                rules = json.load(f)
                # Merge with defaults
                default_rules.update(rules)
                return default_rules
        except FileNotFoundError:
            # Create default rules file
            with open(self.rules_file, 'w') as f:
                json.dump(default_rules, f, indent=2)
            return default_rules
        except Exception as e:
            print(f"⚠️ Error loading rules: {e}")
            return default_rules
    
    def load_working_set(self):
        """Load working set of apps from file"""
        try:
            with open(self.working_set_file, 'r') as f:
                self.working_set = set(json.load(f))
        except FileNotFoundError:
            # Start with reasonable defaults including Cursor
            self.working_set = {"Terminal", "iTerm", "Xcode", "VSCode", "Cursor", "Claude"}
            self.save_working_set()
        except Exception as e:
            print(f"⚠️ Error loading working set: {e}")
    
    def save_working_set(self):
        """Save working set to file"""
        try:
            with open(self.working_set_file, 'w') as f:
                json.dump(sorted(list(self.working_set)), f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving working set: {e}")
    
    def load_focus_history(self):
        """Load focus history from file"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                self.focus_history = []
                for entry in data:
                    event = FocusEvent(
                        timestamp=datetime.fromisoformat(entry['timestamp']),
                        app_name=entry['app_name'],
                        duration_ms=entry.get('duration_ms')
                    )
                    self.focus_history.append(event)
        except FileNotFoundError:
            self.focus_history = []
        except Exception as e:
            print(f"⚠️ Error loading focus history: {e}")
            self.focus_history = []
    
    def save_focus_event(self, event: FocusEvent):
        """Save focus event to log"""
        self.focus_history.append(event)
        
        # Keep only last 1000 events to avoid file getting too large
        if len(self.focus_history) > 1000:
            self.focus_history = self.focus_history[-1000:]
        
        try:
            with open(self.log_file, 'w') as f:
                json.dump([event.to_dict() for event in self.focus_history], f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving focus event: {e}")
    
    def save_prompt(self, prompt: str, app_name: str):
        """Save prompt to file for external processing"""
        prompt_data = {
            "timestamp": datetime.now().isoformat(),
            "app_name": app_name,
            "prompt": prompt,
            "status": "pending"
        }
        
        try:
            # Load existing prompts
            try:
                with open(self.prompts_file, 'r') as f:
                    prompts = json.load(f)
            except FileNotFoundError:
                prompts = []
            
            prompts.append(prompt_data)
            
            # Keep only last 50 prompts
            if len(prompts) > 50:
                prompts = prompts[-50:]
            
            with open(self.prompts_file, 'w') as f:
                json.dump(prompts, f, indent=2)
                
            print(f"💾 Saved prompt to {self.prompts_file}")
            
        except Exception as e:
            print(f"⚠️ Error saving prompt: {e}")
    
    def add_to_working_set(self, app_name: str):
        """Add app to working set"""
        self.working_set.add(app_name)
        self.save_working_set()
        print(f"✅ Added '{app_name}' to working set")
    
    def remove_from_working_set(self, app_name: str):
        """Remove app from working set"""
        if app_name in self.working_set:
            self.working_set.remove(app_name)
            self.save_working_set()
            print(f"❌ Removed '{app_name}' from working set")
    
    def is_distraction_app(self, app_name: str) -> bool:
        """Check if app is considered a distraction"""
        return app_name in self.rules.get("distraction_apps", [])
    
    def should_ignore_app(self, app_name: str) -> bool:
        """Check if we should ignore this app for monitoring"""
        return app_name in self.rules.get("ignored_apps", [])
    
    def get_time_in_app(self, app_name: str, minutes: int = 60) -> int:
        """Get total time spent in app over last N minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        total_ms = 0
        
        for event in self.focus_history:
            if event.timestamp >= cutoff and event.app_name == app_name and event.duration_ms:
                total_ms += event.duration_ms
        
        return total_ms // 1000  # Return seconds
    
    def check_focus_rules(self, app_name: str) -> Optional[str]:
        """Check if current focus violates any rules and return prompt if needed"""
        
        # Ignore certain apps
        if self.should_ignore_app(app_name):
            return None
        
        # Check if it's a new app not in working set
        if app_name not in self.working_set:
            # Check if it's a known distraction
            if self.is_distraction_app(app_name):
                time_in_app = self.get_time_in_app(app_name, minutes=10)
                prompt_threshold = self.rules.get("prompt_after_distraction_minutes", 5) * 60
                
                if time_in_app > prompt_threshold:
                    return f"You've been in {app_name} for {time_in_app//60} minutes. Still on task?"
            else:
                return f"New app detected: {app_name}. Add to working set? (This app appears to be work-related)"
        
        # Check total time off working set apps
        off_task_time = 0
        cutoff = datetime.now() - timedelta(minutes=30)
        
        for event in self.focus_history:
            if (event.timestamp >= cutoff and 
                event.app_name not in self.working_set and 
                not self.should_ignore_app(event.app_name) and 
                event.duration_ms):
                off_task_time += event.duration_ms // 1000
        
        max_off_task = self.rules.get("max_off_task_minutes", 10) * 60
        if off_task_time > max_off_task:
            return f"You've been off-task for {off_task_time//60} minutes. Time to refocus?"
        
        return None
    
    def monitor_once(self) -> Optional[str]:
        """Check focus once and return any needed prompt"""
        current_app = self.get_current_app()
        
        if not current_app:
            return None
        
        now = datetime.now()
        
        # If app changed, log the previous session
        if self.current_app and self.current_app != current_app:
            duration_ms = int((now - self.focus_start_time).total_seconds() * 1000)
            event = FocusEvent(
                timestamp=self.focus_start_time,
                app_name=self.current_app,
                duration_ms=duration_ms
            )
            self.save_focus_event(event)
            
            # Show working set status
            in_working_set = "✅" if self.current_app in self.working_set else "❓"
            print(f"📱 {self.focus_start_time.strftime('%H:%M:%S')} → {now.strftime('%H:%M:%S')} | {self.current_app} → {current_app} ({duration_ms//1000}s) {in_working_set}")
        
        # Update current state
        if self.current_app != current_app:
            self.current_app = current_app
            self.focus_start_time = now
        
        # Check rules and return prompt if needed
        return self.check_focus_rules(current_app)
    
    def start_monitoring(self, interval_seconds: Optional[int] = None):
        """Start continuous monitoring - NON-INTERACTIVE"""
        if interval_seconds is None:
            interval_seconds = self.rules.get("check_interval_seconds", 30)
        
        print(f"🔍 Starting focus monitoring (checking every {interval_seconds}s)")
        print("💡 Working set apps:", ", ".join(sorted(self.working_set)))
        print(f"📁 Prompts will be saved to: {self.prompts_file}")
        print("🛑 Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while True:
                prompt = self.monitor_once()
                if prompt:
                    print(f"\n🤖 ACCOUNTABILITY PROMPT: {prompt}")
                    self.save_prompt(prompt, self.current_app)
                    print(f"💾 Prompt saved for external processing")
                    print("=" * 60)
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            
            # Save final event if needed
            if self.current_app and self.focus_start_time:
                duration_ms = int((datetime.now() - self.focus_start_time).total_seconds() * 1000)
                event = FocusEvent(
                    timestamp=self.focus_start_time,
                    app_name=self.current_app,
                    duration_ms=duration_ms
                )
                self.save_focus_event(event)
                print(f"💾 Saved final session: {self.current_app} ({duration_ms//1000}s)")
    
    def show_stats(self, hours: int = 1):
        """Show focus statistics for the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        app_times = {}
        
        print(f"📊 Focus Statistics (Last {hours} hour(s)):")
        print("=" * 50)
        
        if not self.focus_history:
            print("❓ No focus history available yet. Start monitoring first!")
            return
        
        # Process events
        for event in self.focus_history:
            if event.timestamp >= cutoff and event.duration_ms:
                if event.app_name not in app_times:
                    app_times[event.app_name] = 0
                app_times[event.app_name] += event.duration_ms // 1000
        
        if not app_times:
            print(f"❓ No focus data for the last {hours} hour(s)")
            recent_count = len([e for e in self.focus_history if e.timestamp >= datetime.now() - timedelta(days=1)])
            print(f"💡 Found {len(self.focus_history)} total events, {recent_count} in last 24h")
            
            if self.focus_history:
                latest = max(self.focus_history, key=lambda x: x.timestamp)
                print(f"📅 Latest event: {latest.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {latest.app_name}")
            return
        
        sorted_apps = sorted(app_times.items(), key=lambda x: x[1], reverse=True)
        total_time = sum(app_times.values())
        
        for app_name, seconds in sorted_apps:
            minutes = seconds // 60
            percentage = (seconds / total_time) * 100 if total_time > 0 else 0
            
            # Status indicators
            status_icon = "✅" if app_name in self.working_set else "❓"
            distraction_icon = "⚠️ " if self.is_distraction_app(app_name) else ""
            
            print(f"{status_icon} {distraction_icon}{app_name:<20}: {minutes:3d}m {seconds%60:2d}s ({percentage:5.1f}%)")
        
        # Summary
        work_time = sum(seconds for app, seconds in sorted_apps if app in self.working_set)
        distraction_time = sum(seconds for app, seconds in sorted_apps if self.is_distraction_app(app))
        
        print(f"\n📋 Summary:")
        print(f"  • ✅ Working set time: {work_time//60:3d}m {work_time%60:2d}s ({(work_time/total_time)*100:4.1f}%)")
        print(f"  • ⚠️  Distraction time: {distraction_time//60:3d}m {distraction_time%60:2d}s ({(distraction_time/total_time)*100:4.1f}%)")
        print(f"  • 📊 Total tracked:   {total_time//60:3d}m {total_time%60:2d}s")


def main():
    parser = argparse.ArgumentParser(description="Personal AI Sidekick Focus Monitor")
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--check-once', action='store_true', help='Check focus once and exit')
    parser.add_argument('--stats', type=int, nargs='?', const=1, help='Show stats for last N hours (default: 1)')
    parser.add_argument('--add-app', type=str, help='Add app to working set')
    parser.add_argument('--remove-app', type=str, help='Remove app from working set')
    parser.add_argument('--show-working-set', action='store_true', help='Show current working set')
    parser.add_argument('--interval', type=int, default=30, help='Monitoring interval in seconds')
    parser.add_argument('--show-prompts', action='store_true', help='Show recent prompts')
    
    args = parser.parse_args()
    
    monitor = FocusMonitor()
    
    if args.add_app:
        monitor.add_to_working_set(args.add_app)
    elif args.remove_app:
        monitor.remove_from_working_set(args.remove_app)
    elif args.show_working_set:
        print("📝 Current working set:")
        for app in sorted(monitor.working_set):
            in_rules = "✅" if app in monitor.rules.get("work_apps", []) else ""
            print(f"  • {app} {in_rules}")
        print(f"\n💡 Total: {len(monitor.working_set)} apps")
    elif args.show_prompts:
        try:
            with open(monitor.prompts_file, 'r') as f:
                prompts = json.load(f)
            
            print("🤖 Recent accountability prompts:")
            print("=" * 50)
            
            for prompt in prompts[-10:]:  # Show last 10
                timestamp = datetime.fromisoformat(prompt['timestamp'])
                print(f"📅 {timestamp.strftime('%m/%d %H:%M')} | {prompt['app_name']}")
                print(f"💬 {prompt['prompt']}")
                print(f"📊 Status: {prompt['status']}")
                print()
                
        except FileNotFoundError:
            print("❓ No prompts file found. Start monitoring first!")
    elif args.check_once:
        prompt = monitor.monitor_once()
        if prompt:
            print(f"🤖 {prompt}")
        else:
            in_working_set = "✅" if monitor.current_app in monitor.working_set else "❓"
            print(f"✅ Currently focused on: {monitor.current_app} {in_working_set}")
    elif args.monitor:
        monitor.start_monitoring(args.interval)
    elif args.stats is not None:
        monitor.show_stats(args.stats)
    else:
        # Default: show recent stats
        monitor.show_stats(1)


if __name__ == "__main__":
    main()
