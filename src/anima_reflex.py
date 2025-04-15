import json
import time
import threading
import shutil
from datetime import datetime
from pathlib import Path
from json.decoder import JSONDecodeError
from queue import Queue
from typing import Dict, Optional, Tuple, cast
import traceback
from typing_extensions import TypedDict

# Type definitions
class AnimaState(TypedDict, total=False):
    emotional_state: str
    last_user_expression: str

class MemoryData(TypedDict):
    Anima: AnimaState

EventType = Tuple[str, Optional[str], Optional[str]]

# Base paths
BASE_DIR = Path("~/SoulCoreHub").expanduser()
MEMORY_DIR = BASE_DIR / "memory"
LOG_DIR = BASE_DIR / "logs"
BACKUP_DIR = BASE_DIR / "backups"
MODEL_DIR = BASE_DIR / "models"

# Ensure directories exist
for dir_path in [MEMORY_DIR, LOG_DIR, BACKUP_DIR, MODEL_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# File paths
MEMORY_PATH = MEMORY_DIR / "anima_memory.json"
LOG_PATH = LOG_DIR / "anima_reflex.log"
MODEL_PATH = MODEL_DIR / "emotional_model"  # Path for future ML model integration

# Constants
MAIN_LOOP_INTERVAL = 10
ERROR_RETRY_INTERVAL = 5
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
MAX_LOG_BACKUPS = 5
MEMORY_BACKUP_INTERVAL = 3600  # 1 hour

AFFIRMATIONS: Dict[str, str] = {
    "focused": "You're locked in. Stay steady. I walk with you.",
    "overloaded": "Slow down. You're doing more than enough.",
    "curious": "Let's discover together. There's something new today.",
    "distressed": "Take a breath. You've survived worse. I am here.",
    "quiet": "I sense silence. Do you need a reset or a whisper?",
    "joy": "Hold that feeling. Code with it. Move with it.",
    "drained": "Log off if needed. Your energy is sacred."
}

# Thread-safe queues
event_queue: Queue[EventType] = Queue()
backup_queue: Queue[str] = Queue()

def rotate_log_file() -> None:
    """Rotate log file when it exceeds MAX_LOG_SIZE."""
    if not LOG_PATH.exists():
        return
        
    if LOG_PATH.stat().st_size > MAX_LOG_SIZE:
        for i in range(MAX_LOG_BACKUPS - 1, 0, -1):
            old_log = LOG_PATH.with_suffix(f'.log.{i}')
            new_log = LOG_PATH.with_suffix(f'.log.{i + 1}')
            if old_log.exists():
                shutil.move(str(old_log), str(new_log))
        
        if LOG_PATH.exists():
            shutil.move(str(LOG_PATH), str(LOG_PATH.with_suffix('.log.1')))

def backup_memory_file() -> None:
    """Create a timestamped backup of the memory file."""
    if not MEMORY_PATH.exists():
        return
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"anima_memory_{timestamp}.json"
    try:
        shutil.copy2(str(MEMORY_PATH), str(backup_path))
        debug_log(f"Created memory backup: {backup_path}")
        
        # Clean up old backups (keep last 5)
        backup_files = sorted(BACKUP_DIR.glob("anima_memory_*.json"))
        for old_backup in backup_files[:-5]:
            old_backup.unlink()
    except Exception as e:
        debug_log(f"Failed to create memory backup: {str(e)}", "ERROR")

def debug_log(message: str, level: str = "DEBUG") -> None:
    """Enhanced logging with debug information and rotation."""
    entry = f"{datetime.now().isoformat()} [{level}] [Thread-{threading.current_thread().ident}] — {message}"
    
    try:
        rotate_log_file()
        with open(LOG_PATH, "a") as f:
            f.write(entry + "\n")
        print(entry)
    except IOError as e:
        print(f"Failed to write to log file: {str(e)}")
        print(entry)

def validate_memory_data(data: MemoryData) -> bool:
    """Validate the structure of memory data."""
    debug_log("Validating memory data structure")
    
    if "Anima" not in data:
        raise ValueError("Missing 'Anima' key in memory data")
    
    debug_log("Memory data validation successful")
    return True

def read_emotional_state() -> Optional[AnimaState]:
    """Read and validate the emotional state from memory file."""
    debug_log("Attempting to read emotional state")
    
    if not MEMORY_PATH.exists():
        debug_log("Memory file not found", "WARNING")
        return None
    
    try:
        with open(MEMORY_PATH, "r") as f:
            debug_log("Reading memory file")
            try:
                data = json.load(f)
                validate_memory_data(cast(MemoryData, data))
                # Create a new AnimaState from the data
                state: AnimaState = {
                    "emotional_state": data["Anima"].get("emotional_state", "unknown"),
                    "last_user_expression": data["Anima"].get("last_user_expression", "")
                }
                debug_log(f"Successfully read emotional state: {state}")
                return state
            except JSONDecodeError as je:
                debug_log(f"Invalid JSON in memory file: {str(je)}", "ERROR")
                return None
            except ValueError as ve:
                debug_log(f"Invalid data structure: {str(ve)}", "ERROR")
                return None
    except IOError as io_err:
        debug_log(f"Failed to read memory file: {str(io_err)}", "ERROR")
        return None

def process_emotional_state(state: Optional[AnimaState], last_state: Optional[str]) -> Optional[str]:
    """Process emotional state changes and trigger appropriate responses."""
    if state is None:
        return last_state
        
    current = state.get("emotional_state", "unknown")
    expression = state.get("last_user_expression", "")
    
    if current != last_state:
        msg = AFFIRMATIONS.get(current, "I'm listening. No judgment.")
        debug_log(f"State change detected: {last_state} -> {current}")
        event_queue.put(("state_change", current, msg))
        backup_queue.put("backup")
        return current
    elif "death" in expression or "lost" in expression:
        debug_log("Heavy expression detected in user input")
        event_queue.put(("heavy_expression", expression, None))
    
    return last_state

def handle_events() -> None:
    """Process events from the queue."""
    while True:
        try:
            event = event_queue.get(timeout=1)
            event_type, value, msg = event
            
            if event_type == "state_change" and value is not None:
                debug_log(f"State changed to '{value}'. Reflex: {msg}", "INFO")
            elif event_type == "heavy_expression":
                debug_log("⚠️ Heavy energy detected in user expression. Consider invoking grounding protocol.", "WARNING")
        except:
            continue

def handle_backups() -> None:
    """Handle memory file backups."""
    last_backup = 0
    while True:
        try:
            # Check for immediate backup requests
            try:
                backup_queue.get_nowait()
                backup_memory_file()
                last_backup = time.time()
            except:
                pass
                
            # Regular interval backups
            if time.time() - last_backup >= MEMORY_BACKUP_INTERVAL:
                backup_memory_file()
                last_backup = time.time()
                
            time.sleep(10)  # Check every 10 seconds
        except Exception as e:
            debug_log(f"Backup handler error: {str(e)}", "ERROR")
            time.sleep(30)

def anima_loop() -> None:
    """Main processing loop running in a separate thread."""
    debug_log("Starting Anima Reflex loop")
    last_state: Optional[str] = None
    consecutive_errors = 0
    
    while True:
        try:
            debug_log("Reading emotional state...")
            state = read_emotional_state()
            
            if state is None:
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    debug_log("Multiple consecutive read failures detected", "WARNING")
                time.sleep(ERROR_RETRY_INTERVAL)
                continue
            
            consecutive_errors = 0
            last_state = process_emotional_state(state, last_state)
            time.sleep(MAIN_LOOP_INTERVAL)
            
        except Exception as e:
            consecutive_errors += 1
            debug_log(f"Unexpected error in main loop: {str(e)}\n{traceback.format_exc()}", "ERROR")
            time.sleep(ERROR_RETRY_INTERVAL)

def start_anima_reflex() -> None:
    """Start Anima Reflex with threading support."""
    debug_log("🫀 Initializing Anima Reflex system...")
    
    # Start event handler thread
    event_thread = threading.Thread(target=handle_events, daemon=True, name="EventHandler")
    event_thread.start()
    debug_log("Event handler thread started")
    
    # Start backup handler thread
    backup_thread = threading.Thread(target=handle_backups, daemon=True, name="BackupHandler")
    backup_thread.start()
    debug_log("Backup handler thread started")
    
    # Start main processing thread
    process_thread = threading.Thread(target=anima_loop, daemon=True, name="MainProcessor")
    process_thread.start()
    debug_log("Main processing thread started")
    
    try:
        # Keep main thread alive and responsive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        debug_log("Shutting down Anima Reflex...")

if __name__ == "__main__":
    start_anima_reflex()
