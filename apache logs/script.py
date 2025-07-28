import os

def extract_e0_logs_from_file(filepath, output_filepath=None):
    """
    Extracts log lines where the EventId is 'E0' from a specified file
    and optionally saves them to a new CSV file.

    Args:
        filepath (str): The path to the log file (e.g., 'classified_logs.csv').
        output_filepath (str, optional): The path to the output CSV file
                                         where E0 lines will be saved.
                                         If None, lines are only returned.

    Returns:
        list: A list of strings, where each string is a log line
              with 'E0' as its EventId. Returns an empty list if the file
              is not found or an error occurs.
    """
    e0_lines = []
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()

        # Check if there are lines to process
        if not lines:
            print(f"File '{filepath}' is empty.")
            return []

        # The first line is typically the header
        header = lines[0].strip()
        e0_lines.append(header) # Include the header in the output

        # Process data lines, skipping the header
        for line in lines[1:]:
            line = line.strip() # Remove leading/trailing whitespace and newline characters
            if not line: # Skip empty lines
                continue

            # Split the line by comma. The EventId is the 5th column (index 4).
            parts = line.split(',')
            # Ensure the line has enough parts before accessing index 4
            if len(parts) > 4 and parts[4].strip() == 'E0':
                e0_lines.append(line)

        # Save the extracted lines to a new file if output_filepath is provided
        if output_filepath:
            with open(output_filepath, 'w') as outfile:
                for line in e0_lines:
                    outfile.write(line + '\n')
            print(f"Successfully extracted E0 logs to '{output_filepath}'")

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading or writing the file: {e}")
    return e0_lines

# Define the path to your log file
log_file_path = 'classified_logs.csv'
output_log_file_path = 'e0_classified_logs.csv' # New file to save E0 events

# Get the E0 lines from the file and save them to a new CSV
filtered_logs = extract_e0_logs_from_file(log_file_path, output_log_file_path)

# You can still print them to the console if you wish
# if filtered_logs:
#     for line in filtered_logs:
#         print(line)
# else:
#     print("No E0 events found or file could not be read.")
