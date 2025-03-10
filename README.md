# Introduction

Want to ensure your coworkers, who are stalking your shared Outlook calendar, know that you are busy? 

You could create a bunch of entries in the calendar yourself, but who has time for that?

# Program Structure

When running `start.py`, the program does the following:

## Runs `generate-csv.py`

* Parses the `to-do.pdf` and sends it to Gemini.
* Asks Gemini to generate titles based on the parsed text.
* Retrieves the titles from Gemini and saves them to a `.csv` file.

## Runs `main.py`

* Checks for `.csv` files in the root directory.
* Generates `.ical` formatted calendar events according to the following criteria:
    * Fills the workday with 9-15 calendar events.
    * Calendar events can be between 30 minutes to 180 minutes.
    * If an event is longer than 120 minutes, it's considered a background event.
    * The duration of background events is filled with multiple 30-60 minute events.
    * Workday is defined as:
        * Starting at 08:00, +/- 60 minutes.
        * Picks a time in intervals of 15 minutes (with one exception for 07:55).
        * Ending at 17:00, +/- 60 minutes.
        * Picks a time in intervals of 15 minutes.
* Saves the events as `.ical`.

# Usage

1. Create a file named `apikey.google` with your Gemini API key and save it in the root folder.
2. If you have a to-do list, save it as a `.pdf` with the filename `to-do.pdf` in the root folder of the project.
3. Run `start.py` and follow the prompts.
4. Import the `.ics` file into your calendar program and display it to the world.