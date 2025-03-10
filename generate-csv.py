import csv
import os
import google.generativeai as genai
import PyPDF2  # For PDF extraction
from google.api_core.exceptions import InvalidArgument
import datetime  # For date handling

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

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return None
        
    if os.path.getsize(pdf_path) == 0:
        print(f"PDF file is empty: {pdf_path}")
        return None
        
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) == 0:
                print("PDF contains no pages")
                return None
                
            # Extract text from each page
            pdf_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text + "\n"
            
            if not pdf_text.strip():
                print("PDF contains no extractable text")
                return None
                
            return pdf_text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def setup_genai_api():
    """Setup the Google Generative AI API."""
    api_key = get_api_key_from_file()
    
    if not api_key:
        print("API key not found. Please create an 'apikey.google' file with your API key.")
        return None
    
    genai.configure(api_key=api_key)
    
    # Use the recommended model
    model_name = "gemini-1.5-flash"
    print(f"Using model: {model_name}")
    return genai.GenerativeModel(model_name)

def generate_tasks_from_pdf(model, pdf_text, num_tasks=20):
    """Generate task titles based on content from a PDF file."""
    prompt = f"""Based on the following content from a to-do list:

{pdf_text[:3000]}  # Limit to 3000 chars to avoid token limits

Generate {num_tasks} similar task titles that match this style and content.
Each title should be concise (5-8 words) and specific.
Format as a simple list with one task per line.
No numbers or bullet points."""

    try:
        response = model.generate_content(prompt)
        
        # Parse the response into individual tasks
        tasks = []
        for line in response.text.strip().split('\n'):
            task = line.strip()
            # Clean up any bullet points or formatting
            if task:
                if task.startswith('- ') or task.startswith('* '):
                    task = task[2:]
                elif len(task) > 2 and task[0].isdigit() and task[1:3] in ['. ', ') ']:
                    task = task[3:]
                tasks.append(task)
        
        return tasks[:num_tasks]  # Ensure we only return the requested number
    
    except Exception as e:
        print(f"API Error: {e}")
        return []

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
            # Clean up any bullet points or formatting
            if task:
                if task.startswith('- ') or task.startswith('* '):
                    task = task[2:]
                elif len(task) > 2 and task[0].isdigit() and task[1:3] in ['. ', ') ']:
                    task = task[3:]
                tasks.append(task)
        
        return tasks[:num_tasks]  # Ensure we only return the requested number
    
    except Exception as e:
        print(f"API Error: {e}")
        return []

def save_to_csv(tasks, filename):
    """Save task titles to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for task in tasks:
            writer.writerow([task])
    
    print(f"Successfully saved {len(tasks)} tasks to {filename}")

def extract_tasks_directly_from_pdf(pdf_text):
    """Extract task titles directly from the PDF text without using AI."""
    if not pdf_text:
        return []
        
    # Split text into lines and clean them up
    lines = pdf_text.strip().split('\n')
    tasks = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
            
        # Clean up lines that look like tasks
        # Remove bullet points, numbers, checkboxes, etc.
        if line.startswith('- ') or line.startswith('* '):
            line = line[2:]
        elif line.startswith('□ ') or line.startswith('☐ ') or line.startswith('◻ '):
            line = line[2:]
        elif len(line) > 2 and line[0].isdigit() and line[1:3] in ['. ', ') ']:
            line = line[3:]
            
        # Only include lines that aren't too long (likely tasks, not paragraphs)
        if 5 <= len(line) <= 100:
            tasks.append(line)
    
    return tasks

def save_events_to_csv(events, filename):
    """Save events to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Event", "Start Time", "End Time"])
        for event in events:
            writer.writerow([event['title'], event['start_time'], event['end_time']])
    print(f"Successfully saved events to {filename}")

def generate_events_from_tasks(tasks, start_date):
    """Generate time-blocked events from tasks."""
    events = []
    current_time = datetime.datetime.combine(start_date, datetime.time(9, 0))  # Start at 9 AM
    
    for task in tasks:
        end_time = current_time + datetime.timedelta(minutes=30)  # Each task is 30 minutes
        events.append({
            'title': task,
            'start_time': current_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M')
        })
        current_time = end_time
    
    return events, current_time

def main():
    """Main function to generate and save task titles."""
    print("Task/Event Generator")
    print("---------------------------------------------")
    
    # Setup API
    try:
        model = setup_genai_api()
        if not model:
            return
    except Exception as e:
        print(f"Error setting up API: {e}")
        return
    
    # Ask user if they want to use the PDF file
    pdf_path = "to-do.pdf"
    print(f"Checking for '{pdf_path}'...")
    
    pdf_exists = os.path.exists(pdf_path)
    if not pdf_exists:
        print(f"Warning: '{pdf_path}' not found in the current directory.")
        use_pdf = False
    else:
        use_pdf = input(f"Found '{pdf_path}'. Use it as inspiration for tasks? (y/n): ").lower().startswith('y')
    
    # Extract PDF text if using PDF
    pdf_text = None
    if use_pdf:
        print(f"Reading content from '{pdf_path}'...")
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text:
            print("Could not extract usable text from PDF.")
            use_pdf = False
    
    # Generate AI tasks
    tasks = []
    if use_pdf and pdf_text:
        # Get desired number of AI-enhanced tasks
        try:
            num_tasks = int(input("How many AI-enhanced tasks would you like to generate? [20]: ") or "20")
        except ValueError:
            print("Invalid number, using default of 20")
            num_tasks = 20
        
        # Generate AI tasks based on PDF content
        print(f"Generating {num_tasks} AI-enhanced tasks based on PDF content...")
        tasks = generate_tasks_from_pdf(model, pdf_text, num_tasks)
        
        # Save AI tasks to CSV
        ai_filename = "ai_enhanced_tasks.csv"
        if tasks:
            save_to_csv(tasks, ai_filename)
            print(f"\nSaved {len(tasks)} AI-enhanced tasks to {ai_filename}")
        
        # Extract direct tasks from PDF and save to timeblock CSV
        print("\nExtracting tasks directly from PDF for time blocking...")
        direct_tasks = extract_tasks_directly_from_pdf(pdf_text)
        
        if direct_tasks:
            timeblock_filename = "timeblock_tasks.csv"
            save_to_csv(direct_tasks, timeblock_filename)
            print(f"Saved {len(direct_tasks)} directly extracted tasks to {timeblock_filename}")
            
            # Preview direct tasks
            print("\nPreview of directly extracted tasks:")
            for i, task in enumerate(direct_tasks[:5], 1):
                print(f"{i}. {task}")
            if len(direct_tasks) > 5:
                print(f"... and {len(direct_tasks) - 5} more tasks")
                
            # Ask if user wants to create time-blocked events using direct tasks
            create_events = input("\nGenerate time-blocked calendar events from the direct tasks? (y/n): ").lower().startswith('y')
            
            if create_events:
                # Code to generate time blocks using direct_tasks
                # [Include your time blocking code here, using direct_tasks instead of tasks]
                event_date = datetime.date.today()
                events_filename = f"timeblock_events_{event_date.strftime('%Y%m%d')}.csv"
                
                # Generate time blocks for these tasks
                print(f"Creating time blocks for events on {event_date.strftime('%Y-%m-%d')}...")
                events, end_time = generate_events_from_tasks(direct_tasks, event_date)
                
                if events:
                    # Save to CSV
                    save_events_to_csv(events, events_filename)
        else:
            print("No tasks could be directly extracted from the PDF.")
            
    else:
        # Standard task generation without PDF
        task_type = input("What type of tasks would you like to generate? (e.g., work, personal, project): ")
        
        try:
            num_tasks = int(input(f"How many {task_type} tasks would you like to generate? [20]: ") or "20")
        except ValueError:
            print("Invalid number, using default of 20")
            num_tasks = 20
        
        default_filename = f"{task_type.lower().replace(' ', '_')}_tasks.csv"
        filename = input(f"Enter output filename [{default_filename}]: ") or default_filename
        
        print(f"Generating {num_tasks} {task_type} tasks...")
        tasks = generate_tasks(model, task_type, num_tasks)
        
        if tasks:
            save_to_csv(tasks, filename)
            
            # Preview tasks
            print("\nPreview of generated tasks:")
            for i, task in enumerate(tasks[:5], 1):
                print(f"{i}. {task}")
            if len(tasks) > 5:
                print(f"... and {len(tasks) - 5} more tasks")

if __name__ == "__main__":
    main()