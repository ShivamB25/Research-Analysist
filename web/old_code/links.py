import re
import json

# Function to read the text from a file
def read_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# The file containing the text output
file_path = 'output.txt'

# Read the text from the file
text_output = read_text_from_file(file_path)

# Regular expression to capture links
link_pattern = re.compile(r'https?://[^\s,\'")]+')

# Find all links in the text
links = link_pattern.findall(text_output)

# Remove duplicates by converting the list to a set and back to a list
unique_links = list(set(links))

# Store the links in a JSON file
with open('links.json', 'w') as json_file:
    json.dump(unique_links, json_file, indent=4)

print(f"Extracted {len(unique_links)} unique links.")