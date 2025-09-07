# test_main.py
from datavolley import example_file
from datavolley.io.dvw import read_dvw

# Test the functions
file_path = example_file()
content = read_dvw(file_path)
