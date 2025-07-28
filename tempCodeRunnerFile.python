import pandas as pd

# Load the classified log data
try:
    df_classified = pd.read_csv('classified_logs.csv')
except FileNotFoundError:
    print("Error: classified_logs.csv not found. Please run the previous script to generate it.")
    exit()

# Extract the sequence of EventIds
event_id_sequence = df_classified['EventId'].tolist()

# Define window parameters
# this is as per the diagram
window_size = 3 # Example: W=3 from your diagram
stride = 1      # Example: For overlapping windows, move 1 step at a time

# Generate log sequence events (lse) using a sliding window
log_sequence_events = []
for i in range(0, len(event_id_sequence) - window_size + 1, stride):
    window = event_id_sequence[i : i + window_size]
    log_sequence_events.append(window)

print(f"Generated {len(log_sequence_events)} log sequence events (lse) with window size {window_size} and stride {stride}.")
print(log_sequence_events[:5]) # Print first 5 for a preview

# This 'log_sequence_events' list is what you'll feed into the Word2Vec model's 'sentences' parameter.