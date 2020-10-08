# TimeTableTool

This tool reads a Google Spreadsheet and returns an overview of each day, 
sorted by conference using gspread, Pandas and jinja2.

## Prequisites
This tool was used (and intended for) DAGM GCPR | VMV | VCBM 2020. However, it can be adapted to bigger and smaller conference events.
- You must have one sheet per conference inside the workbook.
- Select a rough time raster for the timetable. Set this raster inside of `writer.py`:
    ```python
    TIME_RASTER = ["08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
               "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00"]
    ```
 - Select the names for the individual conference days (i.e. weekdays).
    ```python
   CONFERENCE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    ```
- The layout is set up so each conference consists of multiple "tracks" per day, these tracks themselves consist of individual events (i.e. orals, poster sessions etc.)
- The conferences can (and probably will) happen in parallel, this is accounted for. However, a single conference should not have multiple tracks running in parallel. (It could still work, but this scenario is untested.)
- The tool can also handle joint events, by having a separate sheet calles "JOINT" for events that are shared between the individual conferences.
- For more information on the overall conference organization have a look into the [guideline document](https://github.com/DAGM-GCPR-VMV-VCBM-2020/ProgramTool/blob/main/conference-media-guide_generic_v01.pdf).

### Setting the conference names
- Open `reader.py` to change the conference names. Changing the conference names should be pretty self-explanatory:
    ```python 
    NAME_sheet = workbook.worksheet("NAME OF GOOGLE WORKSHEET GOES HERE")
    ```
    - propagate `NAME` to the other variables. Hint: The conferences this tool was made for are called GCPR, VMV and VCBM. 
- Set the names of the conferences inside `writer.py` as well:
    ```python 
    trackids_NAME = all_sheets["CONF_NAME"]["track_id"].unique().tolist()
    tracknames_NAME = all_sheets["CONF_NAME"]["track_name"].unique().tolist()
    tracks["CONF_NAME"] = list(zip(trackids_NAME, tracknames_NAME))
    ```
    etc. 

## Setup of Google sheet
- Set up a worksheet for each conference with these columns (in this order!):

|conference|day|timeslot|track_id|track_name|track_start|track_end|track_chair|paper_start|paper_end|paper_id|paper_title|author_name|author_mail|oral_spotlight_poster|discord|youtube|paper|abstract|
|----------|---|--------|--------|----------|-----------|---------|-----------|-----------|---------|--------|-----------|-----------|-----------|---------------------|-------|-------|-----|--------|
|Conference for this Entry|Weekday|Timeslot in Time Raster|ID for conference track, used as anchor|Name for Track as displayed in timetable|Actual start time for track if start time differs from raster|Actual end time for track if end time differs from raster|Name of track chair or contact person per track|Start time of individual event of a track|End time of individual event of a track|ID of an individual event. For internal use.|Title of the entry|Author name(s) for the entry|Author mail address (for internal use)|Type of event. Can be: `oral`, `spotlight`, `poster`, `paper`, `fast-forward`, `social`|Link to discord Channel per track|Link to Youtube (Live/VOD) per Track|Link to PDF|Abstract (hidden per default)|

- If individual events belong to the same track, be sure to input the track information (track_id, track_name, track_start etc.) into every row for each event.
- The columns `day` and `timeslot` have to  represent the values given in CONFERENCE_DAYS and TIME_RASTER, respectively.

## Usage 
- Install the necessary requirements via pip:
    ```bash
    pip3 install --user -r requirements.txt
    ```

- Create a Google Docs API key so this application can access your documents. 
See [this URL](https://developers.google.com/sheets/api/quickstart/python) on how to create said API key.

- Save the file `credentials.json` from the previous step into `~/.config/gspread/credentials.json`. Under Windows systems, place the file under `%APPDATA%\gspread\credentials.json`.
    > Note: The `gspread` folder does not exist automatically once gspread is installed, you have to create it manually.
(Refer to the [gspread documentation](https://gspread.readthedocs.io/en/latest/) for further info.)

- Put the URL to the Google spreadsheet in question into main.py:
    ```python
    SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID"
    ```
- Run the whole thing: `python3 main.py`

## Acknowledgements
- [gspread](https://github.com/burnash/gspread) is used for reading the Google spreadsheet.
- The information inside the spreadsheet is converted into a [Pandas](https://pandas.pydata.org/) dataframe.
- Writing the HTML files is done using the [jinja2](https://jinja.palletsprojects.com/en/2.11.x/) templating language.
