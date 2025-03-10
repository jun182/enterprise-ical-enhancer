import datetime
import random
import csv
import os

def generate_ics_event(start_time, end_time, summary):
  """Generates an ics event string."""
  event_string = f"""
BEGIN:VEVENT
UID:{start_time.strftime('%Y%m%dT%H%M%S')}
DTSTAMP:{datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start_time.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_time.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{summary}
END:VEVENT
"""
  return event_string

def get_event_titles_from_csv(csv_path):
  """Import event titles from a CSV file."""
  titles = []
  try:
    with open(csv_path, 'r') as csvfile:
      reader = csv.reader(csvfile)
      for row in reader:
        if row:  # Skip empty rows
          titles.append(row[0])  # Assuming titles are in the first column
    return titles
  except Exception as e:
    print(f"Error reading CSV: {e}")
    return []

def ask_yes_no_question(question, default="y"):
    """Ask a yes/no question with default 'y' when pressing enter."""
    response = input(f"{question} [{default}]: ").strip().lower()
    if response == "":
        return default == "y"
    return response.startswith("y")

def find_csv_files():
    """Find CSV files in the current directory."""
    csv_files = [f for f in os.listdir() if f.endswith('.csv')]
    return csv_files

def main():
  """Generates an ics file with events filling a workday."""

  today = datetime.datetime.now()
  
  # Get the event details from the user with defaults
  year_input = input(f"Enter year [{today.year}]: ")
  year = today.year if year_input == "" else int(year_input)
  
  month_input = input(f"Enter month [{today.month}]: ")
  month = today.month if month_input == "" else int(month_input)
  
  day_input = input(f"Enter day [{today.day}]: ")
  day = today.day if day_input == "" else int(day_input)
  
  # Ask if user wants to create events for multiple days
  multi_day = ask_yes_no_question("Do you want to add events for multiple days?")
  
  days_to_generate = 1  # Default to 1 day (just the specified date)
  
  # Ask about progressive reduction if generating multiple days
  progressive_reduction = False
  if multi_day:
    # Ask how many additional days
    try:
      additional_days_input = input("How many additional days do you want to add events for? [0]: ")
      additional_days = 0 if additional_days_input == "" else int(additional_days_input)
      days_to_generate = 1 + additional_days  # The specified day plus additional days
      
      # Ask about progressive reduction if generating more than 2 days
      if days_to_generate > 2:
        progressive_reduction = ask_yes_no_question("Progressively reduce events for later days (70%/50%/20% after day 2)?")
    except ValueError:
      print("Invalid input. Defaulting to 1 day.")
      days_to_generate = 1

  # Define scaling factors for different days (only used if progressive_reduction is True)
  event_scaling_factors = {
    0: 1.0,  # First day - 100% events
    1: 1.0,  # Second day - 100% events
    2: 0.7,  # Third day - 70% events
    3: 0.5,  # Fourth day - 50% events
    4: 0.2,  # Fifth day (Friday) - 20% events
  }
  
  # Look for CSV files in the current directory
  csv_files = find_csv_files()
  selected_csv = None

  if csv_files:
    print(f"Found {len(csv_files)} CSV file(s)")
    
    # Cycle through CSV files until user selects one
    i = 0
    while selected_csv is None and i < len(csv_files) * 2:  # Limit cycles to avoid infinite loop
      current_csv = csv_files[i % len(csv_files)]
      if ask_yes_no_question(f"Use '{current_csv}'?"):
        selected_csv = current_csv
        break
      else:
        i += 1
        
        # After cycling through all files once, confirm if we should continue
        if i > 0 and i % len(csv_files) == 0:
          if not ask_yes_no_question("Check CSV files again?"):
            break
    
    if selected_csv:
      csv_path = selected_csv
      print(f"Using '{csv_path}'")
      titles = get_event_titles_from_csv(csv_path)
      if not titles:
        summary = input("No titles found or error reading CSV. Enter event title: ")
        titles = [summary]
      else:
        print(f"Loaded {len(titles)} event titles from CSV")
    else:
      summary = input("Enter event title: ")
      titles = [summary]
  else:
    # No CSV files found
    print("No CSV files found in the current directory.")
    summary = input("Enter event title: ")
    titles = [summary]
  
  # Initialize lists to store all events and summary info
  all_events = []
  day_summaries = []
  
  # Generate events for each day
  for day_offset in range(days_to_generate):
    # Calculate the current date
    current_date = datetime.date(year, month, day) + datetime.timedelta(days=day_offset)
    
    # Get scaling factor for this day (if progressive reduction is enabled)
    scaling_factor = 1.0
    if progressive_reduction and day_offset > 1:
        scaling_factor = event_scaling_factors.get(day_offset, 0.2)  # Default to 20% for any day beyond our mapping
    
    print(f"\nGenerating events for {current_date.strftime('%Y-%m-%d')}:")
    if progressive_reduction and day_offset > 1:
        print(f"Event density: {int(scaling_factor * 100)}% (progressive reduction enabled)")
    
    # Generate random end of workday (18:00 ± 1 hour in 15-min increments)
    possible_end_times = [
      (17, 0), (17, 15), (17, 30), (17, 45),
      (18, 0), (18, 15), (18, 30), (18, 45),
      (19, 0)
    ]
    end_hour, end_minute = random.choice(possible_end_times)
    end_of_workday = datetime.datetime.combine(current_date, datetime.time(end_hour, end_minute))
    
    # Generate events
    events = []
    long_events = []  # Track events 2+ hours long for overlapping
    event_count = 0
    previous_end_time = None
    previous_start_time = None
    
    # Target event count with scaling if enabled
    base_target = random.randint(9, 15)
    if progressive_reduction and day_offset > 1:
        target_event_count = max(3, int(base_target * scaling_factor))  # Ensure at least 3 events
    else:
        target_event_count = base_target
        
    # First pass: create main events
    while True:
      # For progressive reduction, we'll also modify the chance of adding a new event
      if progressive_reduction and day_offset > 1:
          # Skip this iteration with probability (1-scaling_factor) after we have at least 3 events
          if event_count >= 3 and random.random() > scaling_factor:
              # Either break the loop or continue with reduced probability
              if random.random() > scaling_factor:
                  break
              continue

      if event_count == 0:
        # For the first event, randomize start time
        possible_times = [(7, 45), (8, 0), (8, 15), (8, 30), (8, 45), (9, 0)]
        hour, minute = random.choice(possible_times)
        start_time = datetime.datetime.combine(current_date, datetime.time(hour, minute))
      else:
        # Increase overlap probability to 40% to create more events
        should_overlap = random.random() < 0.4 and previous_start_time is not None
        
        if should_overlap:
          # For overlapping events, start sometime between previous start and end
          # Ensure at least 15 minutes after previous start
          min_start = previous_start_time + datetime.timedelta(minutes=15)
          max_start = previous_end_time - datetime.timedelta(minutes=15)
          
          # If there's not enough time to overlap properly, default to non-overlapping
          if min_start >= max_start:
            should_overlap = False
        
        if should_overlap and min_start < max_start:
          # Calculate random start time within the available window
          overlap_minutes = random.randrange(0, int((max_start - min_start).total_seconds() / 60), 15)
          start_time = min_start + datetime.timedelta(minutes=overlap_minutes)
        else:
          # For non-overlapping events, start after the previous event ends with a shorter break (5-15 min)
          break_time = random.choice([5, 10, 15])
          start_time = previous_end_time + datetime.timedelta(minutes=break_time)
        
        # If the start time is already past the end of workday, we're done
        if start_time >= end_of_workday:
          break
          
        hour = start_time.hour
        minute = start_time.minute

      # Generate random duration - bias toward shorter events
      # 70% chance of 30-90 minutes, 30% chance of 90-240 minutes
      if progressive_reduction and day_offset > 1 and random.random() > scaling_factor:
          duration_minutes = random.randrange(30, 61, 15)  # Only short events for later days
      else:
          # Regular duration logic
          if random.random() < 0.7:
              duration_minutes = random.randrange(30, 91, 15)  # 30-90 minutes
          else:
              duration_minutes = random.randrange(90, 241, 15)  # 90-240 minutes
      
      # Create datetime object for the end time
      end_time = start_time + datetime.timedelta(minutes=duration_minutes)
      
      # If end time is past end of workday, truncate it
      if end_time > end_of_workday:
        end_time = end_of_workday
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
      
      # Store the times for the next iteration
      previous_end_time = end_time
      previous_start_time = start_time

      # Generate the ics event string using randomly selected title from CSV
      event_title = random.choice(titles)
      ics_event = generate_ics_event(start_time, end_time, event_title)
      events.append((ics_event, hour, minute, duration_minutes, start_time, end_time))
      event_count += 1
      
      # Track longer events (90+ minutes) for adding overlapping short events
      if duration_minutes >= 90:
        long_events.append((start_time, end_time, event_count))

    # Second pass: add multiple overlapping events for longer events
    for long_start, long_end, long_event_num in long_events:
      # Calculate duration of the long event
      long_duration = int((long_end - long_start).total_seconds() / 60)
      
      # Target coverage: ~75% of the long event (randomized between 65-85%)
      coverage_percent = random.uniform(0.65, 0.85)
      target_overlap_minutes = int(long_duration * coverage_percent)
      
      # Calculate how many short events needed (15-45 min each)
      avg_short_duration = 30  # average short event duration
      num_short_events = max(1, target_overlap_minutes // avg_short_duration)
      
      # Add short events until we reach the target coverage
      overlap_covered = 0
      attempts = 0
      
      while overlap_covered < target_overlap_minutes and attempts < num_short_events * 2 and event_count < target_event_count + 5:
        # Calculate a valid window for the short event to start
        # Ensure it starts after the long event starts
        min_start = long_start + datetime.timedelta(minutes=overlap_covered)
        
        # Ensure it ends before the long event ends
        max_start = long_end - datetime.timedelta(minutes=15)
        
        if min_start >= max_start:
          break
        
        # Calculate random start time within the available window
        overlap_minutes = random.randrange(0, int((max_start - min_start).total_seconds() / 60), 15)
        short_start = min_start + datetime.timedelta(minutes=overlap_minutes)
        
        # Generate short event duration (15-45 minutes in 15-minute increments)
        short_duration = random.choice([15, 30, 45])
        
        # Create datetime object for the end time
        short_end = short_start + datetime.timedelta(minutes=short_duration)
        
        # Ensure the short event ends before the long event ends
        if short_end > long_end:
          short_end = long_end
          short_duration = int((short_end - short_start).total_seconds() / 60)
        
        # Generate the ics event string using randomly selected title from CSV
        event_title = random.choice(titles)  # Randomly choose title here too
        ics_event = generate_ics_event(short_start, short_end, event_title)
        events.append((ics_event, short_start.hour, short_start.minute, short_duration, short_start, short_end))
        event_count += 1
        
        # Update coverage tracking
        overlap_covered += short_duration
        attempts += 1
    
    # Add extra events if we're below the minimum target (9)
    while event_count < 9:
      # Find gaps between events
      sorted_events = sorted([(start, end) for _, _, _, _, start, end in events])
      gaps = []
      
      for i in range(len(sorted_events) - 1):
        gap_start = sorted_events[i][1]
        gap_end = sorted_events[i+1][0]
        gap_duration = int((gap_end - gap_start).total_seconds() / 60)
        
        if gap_duration >= 30:  # Only consider gaps of at least 30 minutes
          gaps.append((gap_start, gap_end))
      
      if not gaps:
        break
      
      # Choose a random gap
      gap_start, gap_end = random.choice(gaps)
      
      # Create an event in this gap
      duration_minutes = min(random.choice([15, 30, 45]), int((gap_end - gap_start).total_seconds() / 60) - 5)
      start_time = gap_start + datetime.timedelta(minutes=5)
      end_time = start_time + datetime.timedelta(minutes=duration_minutes)
      
      # Generate event title
      event_title = titles[event_count % len(titles)]
      ics_event = generate_ics_event(start_time, end_time, event_title)
      events.append((ics_event, start_time.hour, start_time.minute, duration_minutes, start_time, end_time))
      event_count += 1
    
    # After generating events for this day
    all_events.extend(events)
    
    # Store summary for this day
    day_summaries.append({
      'date': current_date.strftime('%Y-%m-%d'),
      'event_count': len(events),
      'end_time': f"{end_hour:02d}:{end_minute:02d}"
    })
  
  # Generate filename based on date range
  if days_to_generate == 1:
    filename = f"events_{year}{month:02d}{day:02d}.ics"
  else:
    end_date = datetime.date(year, month, day) + datetime.timedelta(days=days_to_generate-1)
    filename = f"events_{year}{month:02d}{day:02d}_to_{end_date.year}{end_date.month:02d}{end_date.day:02d}.ics"
  
  # Write all events to an ics file
  with open(filename, "w") as f:
    f.write(f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//BusySchedule//EN\n")
    for event, _, _, _, _, _ in all_events:
      f.write(event)
    f.write("END:VCALENDAR")

  # Print information about the events
  print(f"\nEvents generated successfully! Saved as {filename}")
  print(f"Total events generated: {len(all_events)}")
  
  # Print summary for each day
  print("\nSummary by day:")
  for day_info in day_summaries:
    print(f"Date: {day_info['date']}, Events: {day_info['event_count']}, Workday ending at: {day_info['end_time']}")
  
  # Print detailed event information if requested
  if ask_yes_no_question("Show detailed event information?"):
    # Group events by day for better organization
    events_by_day = {}
    for event, hour, minute, duration, start, end in all_events:
      day_key = start.strftime('%Y-%m-%d')
      if day_key not in events_by_day:
        events_by_day[day_key] = []
      events_by_day[day_key].append((event, hour, minute, duration, start, end))
    
    # Print events grouped by day
    for day_key in sorted(events_by_day.keys()):
      print(f"\nEvents for {day_key}:")
      for i, (_, hour, minute, duration_minutes, _, _) in enumerate(events_by_day[day_key]):
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        duration_display = f"{hours} hours, {minutes} minutes" if hours > 0 else f"{minutes} minutes"
        
        print(f"Event {i+1}:")
        print(f"  Start time: {hour:02d}:{minute:02d}")
        print(f"  Duration: {duration_display}")

if __name__ == "__main__":
  main()