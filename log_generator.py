import datetime
import random
import time
import os
import argparse
import shutil

try:
    from groq import Groq
except ImportError:
    Groq = None # type: ignore

try:
    from langchain_ollama import OllamaLLM
except ImportError:
    OllamaLLM = None # type: ignore

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
PYTHON_FILES = ["module_alpha.py", "service_beta.py", "utils_gamma.py", "main_delta.py"]

# --- Configuration ---
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "groq").lower() # "ollama" or "groq"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:latest") # Default Ollama model
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434") # Default Ollama API URL

groq_client = None
ollama_client = None

# Global datetime objects for log timestamp generation
LOG_START_DATE = None
LOG_END_DATE = None # Will remain None if not specified, for indefinite sequential generation
current_log_time_for_next_log = None

if LLM_PROVIDER == "groq":
    if Groq:
        if not GROQ_API_KEY:
            print("Warning: LLM_PROVIDER is 'groq' but GROQ_API_KEY environment variable not set. AI-generated log messages will be basic.")
        else:
            try:
                groq_client = Groq(api_key=GROQ_API_KEY)
                print("Using Groq for AI log generation.")
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}. AI-generated logs will be basic.")
    else:
        print("Warning: LLM_PROVIDER is 'groq' but 'groq' library not installed. Run 'pip install groq'. AI-generated logs will be basic.")
elif LLM_PROVIDER == "ollama":
    if OllamaLLM:
        try:
            ollama_client = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
            print(f"Using Ollama (model: {OLLAMA_MODEL}, url: {OLLAMA_BASE_URL}) for AI log generation.")
        except Exception as e:
            print(f"Warning: Could not initialize Ollama client: {e}. AI-generated logs will be basic.")
    else:
        print("Warning: LLM_PROVIDER is 'ollama' but 'langchain-ollama' library not installed. Run 'pip install langchain-ollama'. AI-generated logs will be basic.")
else:
    print(f"Warning: Unknown LLM_PROVIDER '{LLM_PROVIDER}'. AI-generated log messages will be basic. Set LLM_PROVIDER to 'ollama' or 'groq'.")

# Date parsing and initialization for sequential timestamps
try:
    _env_log_start_date_str = os.environ.get("LOG_START_DATE", "2025-01-01T00:00:00")  # Default to 2023-01-01T00:00:00 if not set
    _env_log_end_date_str = os.environ.get("LOG_END_DATE", "2025-01-01T23:59:59")  # Default to 2023-01-01T23:59:59 if not set

    start_date_to_parse = _env_log_start_date_str if _env_log_start_date_str else "2023-01-01T00:00:00"  # Fallback to default if not set
    LOG_START_DATE = datetime.datetime.fromisoformat(start_date_to_parse)

    if _env_log_end_date_str:
        LOG_END_DATE = datetime.datetime.fromisoformat(_env_log_end_date_str)
        if LOG_START_DATE and LOG_END_DATE and LOG_START_DATE >= LOG_END_DATE:
            print(f"Warning: LOG_START_DATE ({LOG_START_DATE.isoformat()}) is on or after LOG_END_DATE ({LOG_END_DATE.isoformat()}). "
                  "Log generation may stop immediately or produce limited logs.")
    # If _env_log_end_date_str is None, LOG_END_DATE remains None, allowing indefinite generation.

except ValueError as e:
    print(f"Warning: Invalid date format for LOG_START_DATE or LOG_END_DATE: {e}. "
          "Please use ISO format (YYYY-MM-DDTHH:MM:SS).")
    print("Falling back to default start date (1 day ago) and no end date (runs indefinitely).")
    LOG_START_DATE = datetime.datetime.now() - datetime.timedelta(days=1)
    LOG_END_DATE = None

# Initialize current_log_time_for_next_log with the determined LOG_START_DATE
current_log_time_for_next_log = LOG_START_DATE

def generate_ai_message(filename, level):
    """Generates a log message using Groq API."""
    if not groq_client and not ollama_client:
        return "This is a sample log message (AI not configured/failed)."

    try:
        prompt = (
            f"Generate a dummy log message for a Python application. Do not return thinking process, LLM understading but just the log in the response. "
            f"The log level is '{level}', , and it should be a realistic log message. "
            f"Example:  Error occured while uploading file doc.zip."
            f"OR Successfully connected to database at localhost:5432. "
        )
        
        ai_response_content = ""
        if LLM_PROVIDER == "groq" and groq_client:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant", # Or your preferred Groq model
                temperature=0.7,
                max_tokens=80,
            )
            ai_response_content = chat_completion.choices[0].message.content.strip()
        elif LLM_PROVIDER == "ollama" and ollama_client:
            # Langchain's OllamaLLM.invoke returns a string directly
            ai_response_content = ollama_client.invoke(prompt).strip()
        else:
            return "This is a sample log message (AI provider not available)."

        # print(f"AI Raw Response: {ai_response_content}") # For debugging
        return ai_response_content
    except Exception as e:
        print(f"Error calling {LLM_PROVIDER} API: {e}")
        return f"AI log generation failed with {LLM_PROVIDER}. (Using fallback message)"

def generate_log_line():
    """Generates a single dummy log line."""
    global current_log_time_for_next_log

    timestamp_to_use = current_log_time_for_next_log
    
    # Increment current_log_time_for_next_log for the *next* log entry
    # This controls the simulated time progression in logs.
    increment_seconds = random.uniform(0.1, 2.5) # e.g., log events happen 0.1 to 2.5 simulated seconds apart
    current_log_time_for_next_log += datetime.timedelta(seconds=increment_seconds)
    
    timestamp = timestamp_to_use.isoformat()
    filename = random.choice(PYTHON_FILES)
    level = random.choice(LOG_LEVELS)
    
    ai_message_content = generate_ai_message(filename, level)
    
    # Dummy metrics
    cpu_usage = round(random.uniform(5.0, 80.0), 2)
    memory_mb = random.randint(128, 2048)
    response_time_ms = random.randint(10, 500)
    
    log_message = f"metric_cpu_usage={cpu_usage}% metric_memory_mb={memory_mb}MB metric_response_time_ms={response_time_ms}ms - {ai_message_content}"
    
    return f"{timestamp} [{level}] ({filename}): {log_message}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dummy application logs.")
    parser.add_argument(
        "--delete-existing-logs",
        action="store_true",
        help="Delete the existing log directory without prompting before generating new logs."
    )
    parser.add_argument(
        "--keep-existing-logs",
        action="store_true",
        help="Keep the existing log directory without prompting and append new logs."
    )
    args = parser.parse_args()

    log_dir = os.path.join(os.path.dirname(__file__), "log") # Changed to 'logs' to match previous request

    should_delete = False
    if args.delete_existing_logs:
        should_delete = True
    elif args.keep_existing_logs:
        should_delete = False
    else: # Neither flag was specified, so ask the user
        if os.path.exists(log_dir) and os.listdir(log_dir): # Check if log_dir exists and is not empty
            while True:
                choice = input(f"Log directory '{log_dir}' exists and is not empty. Delete existing logs? (yes/no): ").lower().strip()
                if choice in ['yes', 'y']:
                    should_delete = True
                    break
                elif choice in ['no', 'n']:
                    should_delete = False
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")

    if should_delete and os.path.exists(log_dir):
        print(f"Deleting existing log directory: {log_dir}...")
        shutil.rmtree(log_dir)

    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "dummy_app.log")

    try:
        print(f"Generating sequential dummy logs to {log_file_path}...")
        if LOG_START_DATE:
            print(f"Starting logs from: {LOG_START_DATE.isoformat()}")
        if LOG_END_DATE:
            print(f"Will stop if log time exceeds: {LOG_END_DATE.isoformat()}")
        else:
            print("Logs will be generated indefinitely or until Ctrl+C is pressed.")
        print("Press Ctrl+C to stop.")

        with open(log_file_path, "a") as f:
            while True:
                # Check if the timestamp for the log we are about to generate exceeds the end date
                if LOG_END_DATE and current_log_time_for_next_log > LOG_END_DATE:
                    print(f"\nNext log timestamp ({current_log_time_for_next_log.isoformat()}) would exceed LOG_END_DATE ({LOG_END_DATE.isoformat()}). Stopping.")
                    break

                log_entry = generate_log_line()
                print(log_entry) # Still print to stdout for immediate feedback
                f.write(log_entry + "\n")
                f.flush() # Ensure logs are written immediately
                time.sleep(random.uniform(0.5, 1.5)) # Real-time delay between writing log lines
    except KeyboardInterrupt:
        print("\nLog generation stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")
