import subprocess
import os

# Run the generate-csv.py script
subprocess.run(["python", "generate-csv.py"])

# Ask to run the main.py script
run_main = input("Do you want to run the main.py script? (y/n): ")
if run_main.lower() == 'y':
    subprocess.run(["python", "main.py"])

# Ask to open the folder with the generated files or open the .ics file directly
open_choice = input("Press Enter to open the .ics file directly or type 'folder' to open the folder with the generated files: ")

if open_choice.lower() == 'folder':
    folder_path = os.path.dirname(os.path.abspath("generate-csv.py"))
    os.startfile(folder_path)
else:
    ics_file_path = os.path.abspath("workday_events.ics")  # Replace with the actual .ics file name
    os.startfile(ics_file_path)