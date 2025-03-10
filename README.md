# Introduction

Want to ensure your coworkers, who are stalking your shared Outlook calendar, knows that you are busy? 

You could create a bunch of entries in the calendar yourself, but who has time for that?

# Program structure

When running "start.py", the program does the following;

## runs "generate-csv.py"

  parses the "to-do.pdf" and sends it to Gemini
  asks gemini to generate titles based on the parsed text
  retrieves the titles from gemini and saves it to .csv

## runs "main.py"

  checks for .csv files in the root dir
  generates .ical formatted calendar events according to following criterias
    fills workday with 9-15 calendar events
  calendar events can be between 30 minutes to 180 minutes
  if event is longer than 120 minutes it's considered a background event
  the duration of background events are filled with multiple 30-60 minute events
    workday is defined as
      starting at 0800, +/- 60 minutes
      picks a time in the intervals of 15 minutes
        with one exception for 0755
      ending at 1700, +/- 60 minutes
      picks a time in the intervals of 15 minutes
  saves as .ical

# Usage

Create a file named "apikey.google" with your Gemini API key and save it in the root folder.

If you have a to-do list, save it as a .pdf with the filename "to-do.pdf" in the root folder of the project.

Then, run the "start.py" and follow the prompts.

Import the .ics file in your respective calendar program and display it to the world.
