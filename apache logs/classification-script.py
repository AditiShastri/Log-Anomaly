import re
import csv

def classify_log_entry(log_line):
    """
    Classifies a single log line into an event template and extracts components.
    Returns (Time, Level, Content, EventId, EventTemplate)
    """
    # Regex patterns and their corresponding EventId and EventTemplate.
    # Ordered from most specific to more general, or by commonness, to ensure correct classification.
    event_patterns = [
        # E1: jk2_init() Found child <*> in scoreboard slot <*> (Normal/Expected)
        (r"^\[(.*?)\] \[(notice)\] jk2_init\(\) Found child (\d+) in scoreboard slot (\d+)$", "E1", "jk2_init() Found child <*> in scoreboard slot <*>", lambda m: f"jk2_init() Found child {m.group(3)} in scoreboard slot {m.group(4)}"),
        # E2: workerEnv.init() ok <*> (Normal/Expected)
        (r"^\[(.*?)\] \[(notice)\] workerEnv\.init\(\) ok (.*)$", "E2", "workerEnv.init() ok <*>", lambda m: f"workerEnv.init() ok {m.group(3)}"),
        # E3: mod_jk child workerEnv in error state <*> (Potentially Anomalous)
        (r"^\[(.*?)\] \[(error)\] mod_jk child workerEnv in error state (\d+)$", "E3", "mod_jk child workerEnv in error state <*>", lambda m: f"mod_jk child workerEnv in error state {m.group(3)}"),
        # E4: [client *] Directory index forbidden by rule: * (Highly Anomalous/Critical)
        (r"^\[(.*?)\] \[(error)\] \[client (.*?)\] Directory index forbidden by rule: (.*)$", "E4", "[client <*>] Directory index forbidden by rule: <*>", lambda m: f"[client {m.group(3)}] Directory index forbidden by rule: {m.group(4)}"),
        # E5: jk2_init() Can't find child <*> in scoreboard (Potentially Anomalous)
        (r"^\[(.*?)\] \[(error)\] jk2_init\(\) Can't find child (\d+) in scoreboard$", "E5", "jk2_init() Can't find child <*> in scoreboard", lambda m: f"jk2_init() Can't find child {m.group(3)} in scoreboard"),
        # E6: mod_jk child init <*> <*> (Potentially Anomalous)
        (r"^\[(.*?)\] \[(error)\] mod_jk child init (\d+) (-?\d+)$", "E6", "mod_jk child init <*> <*>", lambda m: f"mod_jk child init {m.group(3)} {m.group(4)}"),
        # E7: Server Resuming Normal Operations (Normal/Expected)
        (r"^\[(.*?)\] \[(notice)\] Apache/.*? configured -- resuming normal operations$", "E7", "Apache/<?> configured -- resuming normal operations", lambda m: "Apache/<?> configured -- resuming normal operations"),
        # E8: Graceful Restart Requested (Normal/Expected)
        (r"^\[(.*?)\] \[(notice)\] Graceful restart requested, doing restart$", "E8", "Graceful restart requested, doing restart", lambda m: "Graceful restart requested, doing restart"),
        # E9: Module Shutting Down (mod_jk2) (Normal/Expected)
        (r"^\[(.*?)\] \[(notice)\] mod_jk2 Shutting down$", "E9", "mod_jk2 Shutting down", lambda m: "mod_jk2 Shutting down"),
        # E10: Factory Error Creating JNI Channel (Potentially Anomalous)
        (r"^\[(.*?)\] \[(error)\] env\.createBean2\(\): Factory error creating channel\.jni:jni \( channel\.jni, jni\)$", "E10", "env.createBean2(): Factory error creating channel.jni:jni ( channel.jni, jni)", lambda m: "env.createBean2(): Factory error creating channel.jni:jni ( channel.jni, jni)"),
        # E11: Can't Create JNI Channel (Potentially Anomalous)
        (r"^\[(.*?)\] \[(error)\] config\.update\(\): Can't create channel\.jni:jni$", "E11", "config.update(): Can't create channel.jni:jni", lambda m: "config.update(): Can't create channel.jni:jni"),
        # E12: Factory Error Creating VM (Potentially Anomalous)
        (r"^\[(.*?)\] \[(error)\] env\.createBean2\(\): Factory error creating vm: \( vm, \)$", "E12", "env.createBean2(): Factory error creating vm: ( vm, )", lambda m: "env.createBean2(): Factory error creating vm: ( vm, )"),
        # E13: Invalid Method in Request (Highly Anomalous/Critical)
        (r"^\[(.*?)\] \[(error)\] Invalid method in request(.*)$", "E13", "Invalid method in request", lambda m: f"Invalid method in request{m.group(3)}"), # Capture the rest of the line
        # E14: URI Too Long (Highly Anomalous/Critical)
        (r"^\[(.*?)\] \[(error)\] request failed: URI too long \(longer than \d+\)$", "E14", "request failed: URI too long (longer than <*>)", lambda m: f"request failed: URI too long (longer than {m.group(3)})"),
        # E15: Attempt to Invoke Directory as Script (Highly Anomalous/Critical)
        (r"^\[(.*?)\] \[(error)\] attempt to invoke directory as script: (.*)$", "E15", "attempt to invoke directory as script: <*>", lambda m: f"attempt to invoke directory as script: {m.group(3)}"),
        # E16: Error Reading Headers (Potentially Anomalous)
        (r"^\[(.*?)\] \[(error)\] request failed: error reading the headers$", "E16", "request failed: error reading the headers", lambda m: "request failed: error reading the headers"),
        # E17: LDAP Notice (Normal/Expected) - Now more specific, was part of E23 description
        (r"^\[(.*?)\] \[(notice)\] LDAP: (.*)$", "E17", "LDAP: <*>", lambda m: f"LDAP: {m.group(3)}"),
        # E18: Digest Notice (Normal/Expected) - Now more specific, was part of E23 description
        (r"^\[(.*?)\] \[(notice)\] Digest: (.*)$", "E18", "Digest: <*>", lambda m: f"Digest: {m.group(3)}"),
        # E19: suEXEC Notice (Normal/Expected)
        (r"^\[(.*?)\] \[(notice)\] suEXEC mechanism enabled \(wrapper: (.*)\)$", "E19", "suEXEC mechanism enabled (wrapper: <*>)", lambda m: f"suEXEC mechanism enabled (wrapper: {m.group(3)})"),
        # E20: mod_python Notice (Normal/Expected) - Now more specific, was part of E24 description
        (r"^\[(.*?)\] \[(notice)\] mod_python: (.*)$", "E20", "mod_python: <*>", lambda m: f"mod_python: {m.group(3)}"),
        # E21: mod_security Notice (Normal/Expected) - Now more specific, was part of E24 description
        (r"^\[(.*?)\] \[(notice)\] mod_security/(.*) configured$", "E21", "mod_security/<?> configured", lambda m: f"mod_security/{m.group(3)} configured"),
        # E22: Generic File Does Not Exist (Highly Anomalous/Critical) - This should be one of the last error patterns as it's very general.
        # This will now capture the generic ones not caught by more specific E28/E29.
        (r"^\[(.*?)\] \[(error)\] File does not exist: (.*)$", "E22", "File does not exist: <*>", lambda m: f"File does not exist: {m.group(3)}"),

        # New granular categories for previously E0 events:

        # E23: LDAP/Digest Notices (Informational) - Catch-all for LDAP/Digest if E17/E18 don't fit
        (r"^\[(.*?)\] \[(notice)\] (LDAP|Digest): (.*)$", "E23", "<LDAP/Digest Type>: <*>", lambda m: f"{m.group(3)}: {m.group(4)}"),
        
        # E24: Module Initialization Notices (Informational) - Catch-all for other module notices
        (r"^\[(.*?)\] \[(notice)\] (mod_python|mod_security)/(.*)$", "E24", "<Module Type>/<?>: <*>", lambda m: f"{m.group(3)}/{m.group(4)}: {m.group(5)}"),

        # E25: Configuration Creation Errors (Potentially Anomalous) - Refined from original E0
        (r"^\[(.*?)\] \[(error)\] config\.update\(\): Can't create (channel\.jni|vm|worker\.jni:onStartup|worker\.jni:onShutdown)(.*)$", "E25", "config.update(): Can't create <component_type><optional_details>", lambda m: f"config.update(): Can't create {m.group(3)}{m.group(4)}"),
        (r"^\[(.*?)\] \[(error)\] env\.createBean2\(\): Factory error creating (channel\.jni:jni|vm): (.*)$", "E25", "env.createBean2(): Factory error creating <bean_type>: <details>", lambda m: f"env.createBean2(): Factory error creating {m.group(3)}: {m.group(4)}"),

        # E27: Script Not Found/Unable to Stat (Highly Anomalous/Critical) - Refined from original E0
        (r"^\[(.*?)\] \[(error)\] \[client (.*?)\] script not found or unable to stat: (.*)$", "E27", "[client <*>] script not found or unable to stat: <*>", lambda m: f"[client {m.group(3)}] script not found or unable to stat: {m.group(4)}"),

        # E28: Application-Specific File Not Found (Highly Anomalous/Critical) - Refined from original E0
        # Grouping common application-related paths
        (r"^\[(.*?)\] \[(error)\] \[client (.*?)\] File does not exist: /var/www/html/(phpmyadmin|cacti|openwebmail|wordpress|drupal|phpgroupware|mambo|oscommerce|osc|osCommerce|catalog|admin|store|onlineshop|shop|b2|b2evo|community|bbs|zboard|msgboard|talk|chat|cvs|articles|WebCalendar|webcalendar|awstats-cgibin|aws|awstats/cgi-bin|awstats/awstats\.|awstats\.pl|ip1\.cgi|modules|Forums|bin|twiki|mute|level|NULL\.printer|scripts/nsiislog\.dll|sumthin|scripts/root\.exe|MSADC|c|d|scripts/\.\.%5c\.\.|scripts/\.\.\\xc1\\x1c\.\.|scripts/\.\.\\xc0\\xaf\.\.|scripts/\.\.\\xc1\\x9c\.\.|scripts/\.\.%2f\.\.|scripts/\.\.%5c%5c\.\.|scripts/root\.exe\?/c\+dir|scripts/\.\.%252e/\.\.%252e/winnt/system32/cmd\.exe\?/c\+dir|scripts/\.\.%35c../winnt/system32/cmd\.exe\?/c\+dir|scripts/\.\.%e0%80%af../\.\.%e0%80%af../\.\.%e0%80%af../winnt/system32/cmd\.exe\?/c\+dir|scripts/\.\.%.*?)(.*)$", 
         "E28", "File does not exist: /var/www/html/<application_path>", 
         lambda m: f"File does not exist: /var/www/html/{m.group(4)}{m.group(5) if m.group(5) else ''}"),
    ]

    for pattern, event_id, event_template, content_extractor in event_patterns:
        match = re.match(pattern, log_line)
        if match:
            time_str = match.group(1)
            level = match.group(2)
            content = content_extractor(match) # Use the lambda to extract content
            return time_str, level, content, event_id, event_template

    # If no specific pattern matches, try to classify as a generic event
    unknown_match = re.match(r"^\[(.*?)\] \[(.*?)\] (.*)$", log_line)
    if unknown_match:
        time_str = unknown_match.group(1)
        level = unknown_match.group(2)
        content = unknown_match.group(3).strip()
        return time_str, level, content, "E0", "Unknown Event: <*>"
    else:
        # Truly unparseable line (e.g., missing timestamp/level) - now classified as E0
        return "", "", log_line.strip(), "E0", "Unknown Event: <*>"


# Input and output file names
input_log_file = 'Apache.log'
output_csv_file = 'classified_logs.csv'

# Open the log file and process it line by line
with open(input_log_file, 'r') as infile, open(output_csv_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    
    # Write the header row
    writer.writerow(["LineId", "Time", "Level", "Content", "EventId", "EventTemplate"])
    
    line_id = 1
    for line in infile:
        time, level, content, event_id, event_template = classify_log_entry(line.strip())
        writer.writerow([line_id, time, level, content, event_id, event_template])
        line_id += 1

print(f"CSV file '{output_csv_file}' generated successfully.")
