import datetime
import random
import csv

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
  
  # Ask for CSV file or a single event title
  csv_path = input("Enter path to CSV file with event titles (or press Enter to enter a single title): ")
  
  if csv_path.strip():
    titles = get_event_titles_from_csv(csv_path)
    if not titles:
      summary = input("No titles found or error reading CSV. Enter event title: ")
      titles = [summary]
    else:
      print(f"Loaded {len(titles)} event titles from CSV")
  else:
    summary = input("Enter event title: ")
    titles = [summary]
  
  # Generate random end of workday (17:00 ± 1 hour in 15-min increments)
  possible_end_times = [
    (16, 0), (16, 15), (16, 30), (16, 45),
    (17, 0), (17, 15), (17, 30), (17, 45),
    (18, 0)
  ]
  end_hour, end_minute = random.choice(possible_end_times)
  end_of_workday = datetime.datetime(year, month, day, end_hour, end_minute)
  
  # Generate events
  events = []
  long_events = []  # Track events 2+ hours long for overlapping
  event_count = 0
  previous_end_time = None
  previous_start_time = None
  
  # Target event count (9-15)
  target_event_count = random.randint(9, 15)
  
  # First pass: create main events
  while True:
    if event_count == 0:
      # For the first event, randomize start time
      possible_times = [(7, 45), (8, 0), (8, 15), (8, 30), (8, 45), (9, 0)]
      hour, minute = random.choice(possible_times)
      start_time = datetime.datetime(year, month, day, hour, minute)
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

    # Generate the ics event string using titles from CSV or default title
    event_title = titles[event_count % len(titles)]
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
      
      # Generate the ics event string using titles from CSV
      event_title = titles[event_count % len(titles)]
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
  
  # Write the events to an ics file
  with open("workday_events.ics", "w") as f:
    f.write(f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//BusySchedule//EN\n")
    for event, _, _, _, _, _ in events:
      f.write(event)
    f.write("END:VCALENDAR")

  # Print information about the events
  print(f"Events generated successfully! Saved as workday_events.ics")
  print(f"Date: {year}-{month:02d}-{day:02d}")
  print(f"Workday ending at {end_hour:02d}:{end_minute:02d}")
  print(f"Generated {len(events)} events")
  
  # Identify overlaps for reporting
  overlaps = []
  for i in range(len(events)):
    for j in range(i+1, len(events)):
      _, _, _, _, start_i, end_i = events[i]
      _, _, _, _, start_j, end_j = events[j]
      if (start_i < end_j and start_j < end_i):
        overlaps.append((i+1, j+1))
  
  for i, (_, hour, minute, duration_minutes, _, _) in enumerate(events):
    hours = duration_minutes // 60
    minutes = duration_minutes % 60
    duration_display = f"{hours} hours, {minutes} minutes" if hours > 0 else f"{minutes} minutes"
    
    print(f"Event {i+1}:")
    print(f"  Start time: {hour:02d}:{minute:02d}")
    print(f"  Duration: {duration_display}")
  
  if overlaps:
    print(f"\nFound {len(overlaps)} overlapping event pairs")

if __name__ == "__main__":
  main()