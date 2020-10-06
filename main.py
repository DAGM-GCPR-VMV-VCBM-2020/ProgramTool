from pathlib import Path

from reader import get_sheets
from writer import write_program_jinja, CONFERENCE_DAYS, write_all, write_legend, write_slides

"""
OBACHT! READ THIS FIRST BEFORE YOU DO ANYTHING!
Before you run this program, you have to obtain an API key for Google Sheets!
See here: https://developers.google.com/sheets/api/quickstart/python
Place the file 'credentials.json' into ~/.config/gspread/credentials.json
AFTER THIS, install the needed requirements via pip (requirements.txt is included).
THEN, configure the file you want to get from Google Sheets below.
"""

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Change this to whatever your Google spreadsheet URL is
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/105IOc5wUjvvK6RwTtd0WBdbVyFUMVvL-1-e7bHFlNjE"

# HTML files will be created inside of <directory with main.py>/OUTPUT_PREFIX
OUTPUT_PREFIX = "program_output"


def main():
    # Create the output directory, if set.
    if OUTPUT_PREFIX:
        Path.mkdir(Path.cwd() / OUTPUT_PREFIX, exist_ok=True)

    print("Fetching Google sheet...")
    all_sheets = get_sheets(SCOPES, SPREADSHEET_URL)

    print("Writing legend...")
    write_legend(prefix=OUTPUT_PREFIX)

    print("Writing program...")
    write_program_jinja(CONFERENCE_DAYS, all_sheets, outfile=True, prefix=OUTPUT_PREFIX)

    print("Writing overview...")
    legend = write_legend(outfile=False)
    program = write_program_jinja(CONFERENCE_DAYS, all_sheets, outfile=False)
    write_all(legend, program, prefix=OUTPUT_PREFIX)

    print("Writing slides...")
    write_slides(CONFERENCE_DAYS, all_sheets)


if __name__ == '__main__':
    main()
