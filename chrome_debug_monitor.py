#!/usr/bin/env python3
"""
Chrome Debug Monitor (Simplified)
==================================
Monitors Chrome debug instance and ensures it stays running.
Minimal, focused, and reliable.

Features:
- Detects Chrome debug on port 9222
- Auto-starts Chrome if not running
- Handles graceful shutdown
- Logs to console and file
- Runs as a daemon via launchd

Usage:
    python3 chrome_debug_monitor.py [--port 9222] [--interval 30]
"""

import sys
import time
import signal
import subprocess
import logging
from pathlib import Path
from argparse import ArgumentParser

# Configuration
DEBUG_PORT = 9222
CHECK_INTERVAL = 30  # seconds
PROJECT_DIR = Path(__file__).parent
LAUNCHER_SCRIPT = PROJECT_DIR / "chrome_debug_launcher.py"
MODAL_SERVER_URL = "http://localhost:3001"  # FrontRow modal server

# Logging setup
log_dir = PROJECT_DIR / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "chrome_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state
running = True


def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger.info(f"Received signal {signum}, shutting down...")
    running = False


def send_notification(message: str, priority: str = "info", duration: int = 3000) -> bool:
    """
    Send notification to FrontRow modal server.
    Returns True if successful, False otherwise.
    Non-blocking - failures are logged but don't crash the monitor.
    """
    try:
        import requests
        from datetime import datetime

        notification_data = {
            "action": "show",
            "message": message,
            "priority": priority,
            "duration": duration,
            "icon": "🖥️",
            "timestamp": datetime.now().isoformat(),
            "source": "chrome_debug_monitor"
        }

        response = requests.post(
            f"{MODAL_SERVER_URL}/api/test/modal",
            json=notification_data,
            timeout=2
        )

        if response.status_code == 200:
            logger.debug(f"Notification sent: {message}")
            return True
        else:
            logger.debug(f"Notification failed: {response.status_code}")
            return False

    except Exception as e:
        logger.debug(f"Notification error (modal server may be offline): {e}")
        return False


def is_chrome_debug_running(port: int) -> bool:
    """
    Check if Chrome debug is actually running (not just zombie process).
    Checks both that port responds AND that Chrome has active tabs/targets.
    """
    try:
        import requests

        # First check: Is the port responding?
        version_response = requests.get(
            f"http://localhost:{port}/json/version",
            timeout=2
        )
        if version_response.status_code != 200:
            return False

        # Second check: Does Chrome have any active tabs/targets?
        # When Chrome UI is closed but process lingers, this returns []
        targets_response = requests.get(
            f"http://localhost:{port}/json",
            timeout=2
        )
        if targets_response.status_code == 200:
            targets = targets_response.json()
            # Chrome should have at least one page/target when running
            has_targets = len(targets) > 0
            if not has_targets:
                logger.debug("Chrome port alive but no tabs/targets - treating as stopped")
            return has_targets

        # If we can't check targets, assume it's running
        return True

    except Exception as e:
        logger.debug(f"Chrome check failed: {e}")
        return False


def start_chrome_debug() -> bool:
    """Start Chrome with debugging using launcher script"""
    if not LAUNCHER_SCRIPT.exists():
        logger.error(f"Launcher script not found: {LAUNCHER_SCRIPT}")
        return False

    try:
        logger.info("Starting Chrome with debugging...")
        result = subprocess.run(
            [sys.executable, str(LAUNCHER_SCRIPT)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logger.info("Chrome debug started successfully")
            return True
        else:
            logger.error(f"Chrome launcher failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("Chrome launcher timed out")
        return False
    except Exception as e:
        logger.error(f"Failed to start Chrome: {e}")
        return False


def monitor_loop(port: int, interval: int):
    """Main monitoring loop"""
    logger.info(f"Chrome Debug Monitor started (port={port}, interval={interval}s)")
    send_notification("🟢 Chrome Debug Monitor started", "success", 2000)

    restart_count = 0

    # Initial check
    if not is_chrome_debug_running(port):
        logger.info("Chrome debug not running, starting...")
        if start_chrome_debug():
            time.sleep(5)  # Wait for Chrome to fully start
            restart_count += 1
            send_notification("✅ Chrome debug started successfully", "success", 2500)
        else:
            send_notification("⚠️ Failed to start Chrome debug", "warning", 3000)
    else:
        logger.info("Chrome debug already running")
        send_notification("Chrome debug already running", "info", 2000)

    # Monitoring loop
    while running:
        try:
            if not is_chrome_debug_running(port):
                logger.warning("Chrome debug stopped, restarting...")
                send_notification("⚠️ Chrome debug stopped, restarting...", "warning", 2500)
                if start_chrome_debug():
                    restart_count += 1
                    logger.info(f"Chrome restarted (count: {restart_count})")
                    send_notification(f"✅ Chrome debug restarted (#{restart_count})", "success", 2500)
                    time.sleep(5)
                else:
                    logger.error("Failed to restart Chrome, will retry...")
                    send_notification("❌ Failed to restart Chrome, retrying...", "error", 3000)

            time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
            time.sleep(interval)

    logger.info("Monitor shutting down...")
    send_notification("🔴 Chrome Debug Monitor stopped", "info", 2000)


def main():
    """Main entry point"""
    parser = ArgumentParser(description="Chrome Debug Monitor")
    parser.add_argument(
        "--port",
        type=int,
        default=DEBUG_PORT,
        help=f"Debug port to monitor (default: {DEBUG_PORT})"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=CHECK_INTERVAL,
        help=f"Check interval in seconds (default: {CHECK_INTERVAL})"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check status and exit"
    )

    args = parser.parse_args()

    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    # Status check mode
    if args.status:
        if is_chrome_debug_running(args.port):
            print(f"✅ Chrome debug running on port {args.port}")
            sys.exit(0)
        else:
            print(f"❌ Chrome debug not running on port {args.port}")
            sys.exit(1)

    # Run monitor
    try:
        monitor_loop(args.port, args.interval)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Monitor crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
