import subprocess
import os

def ask_yes_no_question(question, default="y"):
    """Ask a yes/no question with default 'y' when pressing enter."""
    response = input(f"{question} [{default}]: ").strip().lower()
    if response == "":
        return default == "y"
    return response.startswith("y")

def find_ics_files():
    """Find and sort all .ics files in the current directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ics_files = [f for f in os.listdir(current_dir) if f.endswith('.ics')]
    return sorted(ics_files)  # Sort the list alphabetically

# Run the generate-csv.py script
if ask_yes_no_question("Run generate-csv.py?"):
    subprocess.run(["python", "generate-csv.py"])

# Ask to run the main.py script
if ask_yes_no_question("Run main.py?"):
    subprocess.run(["python", "main.py"])

# Find all .ics files
ics_files = find_ics_files()

if not ics_files:
    print("No .ics files found in the directory.")
    if ask_yes_no_question("Open the folder instead?"):
        folder_path = os.path.dirname(os.path.abspath(__file__))
        os.startfile(folder_path)
else:
    print(f"Found {len(ics_files)} .ics files")
    
    # Cycle through .ics files until user selects one or chooses to exit
    opened_file = False
    i = 0
    while not opened_file and i < len(ics_files) * 2:  # Limit cycles to avoid infinite loop
        current_file = ics_files[i % len(ics_files)]
        
        if ask_yes_no_question(f"Open '{current_file}'?"):
            ics_file_path = os.path.abspath(current_file)
            try:
                os.startfile(ics_file_path)
                opened_file = True
                print(f"Opened {current_file}")
            except Exception as e:
                print(f"Error opening file: {e}")
        else:
            i += 1
            
            # After cycling through all files once, check if we should continue
            if i > 0 and i % len(ics_files) == 0:
                if not ask_yes_no_question("Check files again?"):
                    break
    
    # If no file was opened, offer to open the folder
    if not opened_file and ask_yes_no_question("Open folder instead?"):
        folder_path = os.path.dirname(os.path.abspath(__file__))
        os.startfile(folder_path)