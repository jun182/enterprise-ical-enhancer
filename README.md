# enterprise-ical-enhancer

## Introduction

Want to ensure your coworkers, who are stalking your shared Outlook calendar, know that you are busy? You could create a bunch of entries in the calendar yourself, but who has time for that?

This tool automatically generates realistic calendar events with task titles derived from AI or your own to-do list, creating a professional-looking busy schedule.

## Features

* Generate task titles via Google's Gemini AI
* Import tasks from your own to-do list PDF
* Create time-blocked calendar events that:
    * Fill your workday with realistic 9-15 events
    * Include both long meetings and short overlapping events
    * Follow natural scheduling patterns
    * Can extend across multiple days with tapered scheduling (lighter toward end of week)
* Export to standard ICS format for immediate import into Outlook, Google Calendar, etc.

## Setup

1. Install required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
2. Create a file named `apikey.google` with your Gemini API key and save it in the root folder.
3. Optional: Save your to-do list as `to-do.pdf` in the root folder.

## Program Structure

The program follows a logical flow from task generation to calendar creation:

### `start.py` (Main Entry Point)

The program begins with `start.py`, which orchestrates the workflow:

* Asks if you want to run `generate-csv.py` to create task lists.
* Asks if you want to run `main.py` to generate calendar events.
* Helps you locate and open the generated ICS files.

### `generate-csv.py` (Task Generation)

Handles creation of task titles through two methods:

**AI-based generation:**

* Connects to Google Gemini API.
* Generates realistic task titles based on a type you specify.
* Can be inspired by content from a PDF file.

**Direct PDF extraction:**

* Extracts text directly from your to-do PDF.
* Processes it into individual task titles.

Both methods save tasks to CSV files for use by the calendar generator.

### `main.py` (Calendar Event Generation)

Creates calendar events using sophisticated scheduling:

* Uses task titles from CSV files you select.
* Generates events following these rules:
    * Starts workday between 7:45-9:00 AM.
    * Ends workday between 5:00-7:00 PM.
    * Creates 9-15 events per day.
    * Varies event durations (30-240 minutes).
    * Adds overlapping short meetings to long events.
    * Fills gaps with appropriate-length events.
    * Supports multi-day scheduling with progressive reduction.
* Exports the schedule as an ICS file.

## Usage

1. Run `start.py` and follow the prompts:

    * When prompted to run `generate-csv.py`:
        * Select 'Y' to create new task titles.
        * The system will check for `to-do.pdf` and offer to use it.
        * You can generate AI tasks or extract directly from the PDF.
    * When prompted to run `main.py`:
        * Select 'Y' to create calendar events.
        * Enter date information (or press Enter for today's date).
        * Choose to generate events for multiple days if needed.
        * For 3+ days, you can enable progressive reduction (fewer events on later days).
        * Select a CSV file from the list of available files.

2. After generation completes:
    * The system shows a summary of generated events.
    * You can view detailed information if desired.
    * The program will offer to open the generated ICS file.
3. Import the ICS file into your calendar application.

## Multi-Day Event Generation

When generating events for multiple days, you can enable progressive reduction:

* Day 1-2: 100% event density.
* Day 3: 70% event density.
* Day 4: 50% event density.
* Day 5: 20% event density.

This creates a realistic tapering effect toward the end of the week.

## Technical Details

* Events can overlap based on configurable probability (40%).
* Long events (90+ minutes) get filled with shorter overlapping events.
* Event start and end times align to 15-minute intervals.
* Task titles are randomly selected from your CSV file.
* The system handles edge cases like end-of-day truncation.
* ICS files follow standard calendar format for maximum compatibility.

## Example Output

After running the program, you'll get an ICS file containing your generated events, ready to import into any calendar application. The console will show a summary like:
