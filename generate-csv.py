import csv
import os
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument

def get_api_key_from_file(file_path="apikey.google"):
    """Read API key from a file."""
    try:
        with open(file_path, 'r') as file:
            api_key = file.read().strip()
            return api_key
    except FileNotFoundError:
        print(f"API key file '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading API key: {e}")
        return None

def setup_genai_api():
    """Setup the Google Generative AI API."""
    api_key = get_api_key_from_file()
    
    if not api_key:
        print("API key not found. Please create an 'apikey.google' file with your API key.")
        return None
    
    genai.configure(api_key=api_key)
    
    # Use the recommended model directly
    try:
        # Try the recommended model first
        model_name = "gemini-1.5-flash"
        print(f"Using model: {model_name}")
        return genai.GenerativeModel(model_name)
    
    except Exception as e:
        print(f"Error with recommended model: {e}")
        
        # Try to list available models as fallback
        try:
            print("Attempting to list available models...")
            available_models = [m.name for m in genai.list_models()]
            print("Available models:", available_models)
            
            # Look for any Gemini models
            gemini_models = [m for m in available_models if "gemini" in m.lower()]
            
            if gemini_models:
                model_name = gemini_models[0]
                print(f"Using available model: {model_name}")
                return genai.GenerativeModel(model_name)
            else:
                print("No Gemini models found. Please check your API key permissions.")
                return None
        
        except Exception as e2:
            print(f"Error listing models: {e2}")
            print("Unable to initialize model. Please check your API key and permissions.")
            return None

def generate_tasks(model, task_type, num_tasks=20):
    """Generate task titles using Google's Generative AI."""
    prompt = f"""Generate {num_tasks} realistic {task_type} task titles.
    Each title should be concise (5-8 words) and specific.
    Format as a simple list, one task per line.
    No numbers or bullet points."""
    
    try:
        response = model.generate_content(prompt)
        
        # Parse the response into individual tasks
        tasks = []
        for line in response.text.strip().split('\n'):
            task = line.strip()
            if task and not task.startswith('*') and not task.startswith('-'):
                tasks.append(task)
        
        return tasks[:num_tasks]  # Ensure we only return the requested number
    
    except InvalidArgument as e:
        print(f"API Error: {e}")
        return []

def save_to_csv(tasks, filename):
    """Save task titles to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for task in tasks:
            writer.writerow([task])
    
    print(f"Successfully saved {len(tasks)} tasks to {filename}")

def main():
    """Main function to generate and save task titles."""
    print("CSV Task Generator using Google Generative AI")
    print("---------------------------------------------")
    
    # Setup API
    model = setup_genai_api()
    if not model:
        return
    
    # Get task type from user
    task_type = input("What type of tasks would you like to generate? (e.g., work, personal, project): ")
    
    # Get desired number of tasks
    try:
        num_tasks = int(input(f"How many {task_type} tasks would you like to generate? [20]: ") or "20")
    except ValueError:
        print("Invalid number, using default of 20")
        num_tasks = 20
    
    # Get output filename
    default_filename = f"{task_type.lower().replace(' ', '_')}_tasks.csv"
    filename = input(f"Enter output filename [{default_filename}]: ") or default_filename
    
    # Generate tasks
    print(f"Generating {num_tasks} {task_type} tasks...")
    tasks = generate_tasks(model, task_type, num_tasks)
    
    if tasks:
        # Save to CSV
        save_to_csv(tasks, filename)
        
        # Preview some tasks
        print("\nPreview of generated tasks:")
        for i, task in enumerate(tasks[:5], 1):
            print(f"{i}. {task}")
        if len(tasks) > 5:
            print(f"... and {len(tasks) - 5} more tasks")
    else:
        print("Failed to generate tasks. Please check your API key and try again.")

if __name__ == "__main__":
    main()