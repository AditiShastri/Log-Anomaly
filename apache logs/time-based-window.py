import pandas as pd
from gensim.models import Word2Vec
import numpy as np
import os
import joblib

# --- Define File Paths ---
# Using new filenames to avoid overwriting your previous results
classified_log_file = 'classified_logs.csv'
word2vec_model_path = "word2vec_log_events_5min_window.model"
log_sequence_matrix_path = "log_sequence_matrix_5min_window.joblib"

# --- Step 1: Load the classified log data ---
try:
    df_classified = pd.read_csv(classified_log_file)
    print(f"'{classified_log_file}' loaded successfully.")
    print(f"Shape of df_classified: {df_classified.shape}")
except FileNotFoundError:
    print(f"Error: '{classified_log_file}' not found.")
    exit()

# --- Step 2: Generate log sequence events (lse) using a 5-minute time window ---
print("\nGenerating log sequences based on a 5-minute time window...")

# Convert 'Time' column to datetime objects
try:
    # Pandas can often infer the format automatically, which is robust
    df_classified['Timestamp'] = pd.to_datetime(df_classified['Time'])
    print("Successfully converted 'Time' column to datetime objects.")
except Exception as e:
    print(f"Error converting 'Time' column to datetime: {e}")
    # As a fallback, try a specific format if auto-parsing fails
    try:
        df_classified['Timestamp'] = pd.to_datetime(df_classified['Time'], format='%a %b %d %H:%M:%S %Y')
        print("Successfully converted 'Time' column with specific format.")
    except Exception as e2:
        print(f"Could not parse time format. Error: {e2}")
        exit()

# Set the new 'Timestamp' column as the index for time-based grouping
df_classified = df_classified.set_index('Timestamp')

# Group by 5-minute intervals and collect EventIds for each window
# '5T' is the offset alias for 5 minutes.
# We create a list of EventId lists for each non-empty group.
log_sequence_events = [
    group['EventId'].tolist()
    for _, group in df_classified.groupby(pd.Grouper(freq='5T'))
    if not group.empty
]

print(f"Generated {len(log_sequence_events)} log sequence events (lse) using a 5-minute window.")

if not log_sequence_events:
    print("No log sequence events were generated. Exiting.")
    exit()

print("First 5 generated LSEs:", log_sequence_events[:5])


# --- Step 3: Train or Load Word2Vec Model ---
model = None
if os.path.exists(word2vec_model_path):
    print(f"\nWord2Vec model '{word2vec_model_path}' found. Loading model.")
    try:
        model = Word2Vec.load(word2vec_model_path)
        print("Word2Vec model loaded successfully.")
    except Exception as e:
        print(f"Error loading Word2Vec model: {e}. Attempting to re-train.")
else:
    print(f"\nWord2Vec model '{word2vec_model_path}' not found. Training a new model.")

if model is None:
    try:
        # Use the time-windowed sequences to train the model
        model = Word2Vec(sentences=log_sequence_events, vector_size=100, window=5, min_count=1, workers=4)
        model.save(word2vec_model_path)
        print(f"Word2Vec model trained and saved successfully as '{word2vec_model_path}'")
    except Exception as e:
        print(f"An error occurred during Word2Vec training or saving: {e}")
        exit()

# --- Step 4: Average the Vectors for each Log Sequence Event (lse) ---
def sequence_to_vector(sequence, model):
    """
    Converts a sequence of event IDs into a single vector by averaging their Word2Vec embeddings.
    """
    vectors = [model.wv[event_id] for event_id in sequence if event_id in model.wv]
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        # Return a zero vector if no event_id in the sequence is in the model's vocabulary
        return np.zeros(model.vector_size)

print("\nConverting log sequences to vectors by averaging...")
lse_vectors = [sequence_to_vector(lse, model) for lse in log_sequence_events]

# Convert the list of vectors into a single NumPy matrix
log_sequence_matrix = np.array(lse_vectors)

print(f"Created Log Sequence Matrix with shape: {log_sequence_matrix.shape}")
if log_sequence_matrix.size > 0:
    print("First 3 rows of the Log Sequence Matrix (first 5 dimensions):")
    print(log_sequence_matrix[:3, :5])

# --- Step 5: Store the Log Sequence Matrix ---
try:
    joblib.dump(log_sequence_matrix, log_sequence_matrix_path)
    print(f"Log Sequence Matrix saved successfully to '{log_sequence_matrix_path}'")
except Exception as e:
    print(f"Error saving Log Sequence Matrix: {e}")

print("\nScript finished.")