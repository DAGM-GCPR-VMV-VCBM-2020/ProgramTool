from pathlib import Path

from jinja2 import Template, Environment, FileSystemLoader
import pandas as pd
import pdfkit

CONFERENCE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday"]

"""
Declare fontawesome icons used in the program and slide set.
If you want to add another icon, add another key to this dict.
Then, use this key in the oral/spotlight/poster column of the Google sheet.
"""
icons = dict()
icons["oral"] = "far fa-comments"
icons["spotlight"] = "far fa-lightbulb"
icons["poster"] = "fas fa-map"
icons["fast-forward"] = "fas fa-fast-forward"
icons["social"] = "fas fa-user-friends"
icons["paper"] = "far fa-file"
icons["short"] = "fas fa-ruler"

jinja_env = Environment(extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols'],
                        loader=FileSystemLoader('templates'),
                        lstrip_blocks=True,
                        trim_blocks=True)


def create_overall_dataframe(sheets):
    # Append all sheets to each other so we can work with them as a single DataFrame
    all_confs = [sheet for sheet in sheets.values()]
    single_df = pd.concat(all_confs, ignore_index=True)

    # make conference day column a categorical, needed for sorting
    single_df['day'] = pd.Categorical(single_df['day'], categories=CONFERENCE_DAYS)

    # turn track start column into datetime objects
    pd.to_datetime(single_df['track_start'], format="%H:%M")

    # sort the whole shebang
    single_df.sort_values(by=['day', 'track_start'], axis=0, inplace=True)

    return single_df


def write_program_jinja(conference_days, sheets, outfile=True, prefix=''):
    """
    Write the "verbose" program structure to an HTML file using Jinja2.
    Template can be found under templates/program.jinja2.
    :param conference_days: The weekdays to be displayed as sub-headings
    :param sheets: Dictionary containing the Google Sheet names as keys and a Pandas dataframe with the lines as values
    :return: None
    """
    single_df = create_overall_dataframe(sheets)

    template = jinja_env.get_template('program.jinja2')
    output = template.render(conference_days=conference_days,
                             df=single_df,
                             icons=icons)

    if outfile:
        with open(prefix + '/program_jinja.html', 'w+', encoding="utf-8") as fd:
            fd.write(output)
        print("Program with templating written to " + prefix + '/program_jinja.html')
    else:
        return output


def write_slides(conference_days, sheets):
    """
    Create a set of HTML slides containing the information about all conference tracks.
    For this, we first create a list of all tracks with their corresponding track information.
    Then, we loop over all the data entries belonging to this track and write out their information.
    The HTML template can be found under templates/track_info.jinja2.
    """
    single_df = create_overall_dataframe(sheets)

    trackdict = dict()
    for day in conference_days:
        items_per_day = single_df.loc[single_df['day'] == day]
        tracks_per_day = items_per_day['track_id'].unique().tolist()
        for track in tracks_per_day:
            trackdict[track] = dict()
            trackrow = single_df.loc[single_df['track_id'] == track].head(1)
            for key, val in trackrow.iterrows():
                trackdict[track]["conference"] = val['conference']
                trackdict[track]["track_title"] = val['track_name']
                trackdict[track]["start_time"] = val['track_start']
                trackdict[track]["end_time"] = val['track_end']
                trackdict[track]["youtube"] = val['youtube']
                trackdict[track]["discord"] = val['discord']
                trackdict[track]["chair"] = val['track_chair']
                trackdict[track]["entries"] = dict()
            for key, val in single_df.dropna().iterrows():
                if val['day'] == day and val['track_id'] == track:
                    trackdict[track]["entries"][val['paper_id']] = dict()
                    if val['paper_start']:
                        trackdict[track]["entries"][val['paper_id']]["start"] = str(val['paper_start'])
                    if val['paper_end']:
                        trackdict[track]["entries"][val['paper_id']]["end"] = str(val['paper_end'])
                    if val['author_name']:
                        trackdict[track]["entries"][val['paper_id']]["author"] = val['author_name']
                    if val['paper_title']:
                        trackdict[track]["entries"][val['paper_id']]["title"] = val['paper_title']
                    if val['oral_spotlight_poster']:
                        trackdict[track]["entries"][val['paper_id']]["oral_spotlight_poster"] = icons[val['oral_spotlight_poster']]

    # set up slide export
    export_path = Path.cwd() / "slides"
    Path.mkdir(export_path, exist_ok=True)

    pdf_options = {
        'page-width': '1920px',
        'page-height': '1080px',
        'encoding': 'UTF-8',
        'margin-top': '0px',
        'margin-right': '0px',
        'margin-bottom': '0px',
        'margin-left': '0px',
        'zoom': '0.9',
        'enable-local-file-access': ''
    }

    """
    Set up a dictionary with all the information needed for a track introduction slide.
    See track_info.jinja2 for information on how this information is displayed.
    """
    for track in trackdict:
        template = jinja_env.get_template('track_info.jinja2')
        output = template.render(
            icons=icons,
            conference=trackdict[track]["conference"],
            track_title=trackdict[track]["track_title"],
            start_time=trackdict[track]["start_time"],
            end_time=trackdict[track]["end_time"],
            discord="OVERALL DISCORD LINK HERE",
            youtube="OVERALL YOUTUBE LINK HERE",
            entries=trackdict[track]["entries"]
        )
        html = Path(export_path) / (str(track)+".html")
        with open(html, "w+", encoding="utf-8") as fd:
            fd.write(output)

    """
    Take all HTML files and convert them to PDFs.
    This only works if you have wkhtmltopdf installed and also, unfortunately,
    only on Linux. The Windows version does seem to have some issues with CSS and formatting.
    Uncomment the following lines at your own risk.
    """

    """
    all_htmls = list(export_path.glob('*.html'))
    for html_file in all_htmls:
        pdf_filename = str(html_file.parent)+"/"+str(html_file.stem)+".pdf"
        pdfkit.from_file(str(html_file), pdf_filename, options=pdf_options)
    """


def write_legend(outfile=True, prefix=''):
    """
    Write a legend in HTML form explaining colors and icons used.
    :param outfile: whether the output is written to HTML or dumped to a string (used in main.py)
    :param prefix: Output prefix, defaults to the current working directory (see main.py)
    :return:
    """
    template = jinja_env.get_template('legend.jinja2')
    output = template.render(icons=icons)

    if outfile:
        with open(prefix + '/legend_jinja.html', 'w+', encoding="utf-8") as fd:
            fd.write(output)
        print("Legend written to " + prefix + '/legend_jinja.html')
    else:
        return output


def write_all(legend, program, prefix=''):
    """
    Write out an HTML file containing both legend and program.
    :param legend: output of write_legend(outfile=False)
    :param program: output of write_program_jinja(outfile=False)
    :param prefix:
    :return:
    """
    with open(prefix + '/overall_program.html', 'w+', encoding="utf-8") as fd:
        fd.write(legend)
        fd.write('\n')
        fd.write(program)
    print("Written overall program to " + prefix + '/overall_program.html')
