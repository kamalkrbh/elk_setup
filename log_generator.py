import datetime
import random
import time
import os

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
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower() # "ollama" or "groq"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:latest") # Default Ollama model
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434") # Default Ollama API URL
# --- End Configuration ---

groq_client = None
ollama_client = None

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
                model="mixtral-8x7b-32768", # Or your preferred Groq model
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
    timestamp = datetime.datetime.now().isoformat()
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
    log_dir = os.path.join(os.path.dirname(__file__), "log") # Changed to 'logs' to match previous request
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "dummy_app.log")

    try:
        print(f"Generating dummy logs to {log_file_path}... Press Ctrl+C to stop.")
        with open(log_file_path, "a") as f:
            while True:
                log_entry = generate_log_line()
                print(log_entry) # Still print to stdout for immediate feedback
                f.write(log_entry + "\n")
                f.flush() # Ensure logs are written immediately
                #time.sleep(random.uniform(0.5, 3.0)) # Simulate random log generation frequency
    except KeyboardInterrupt:
        print("\nLog generation stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")
