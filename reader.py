"""
This file reads the contents of a Google Docs document that contains a row-based format.
Multiple sheets can be selected per document, i.e. for different parts of a conference.
"""
import gspread
import pandas as pd


def get_sheets(scopes, url):
    """
    Read in the Google spreadsheet using gspread and convert them into Pandas
    dataframes. We're using pandas for ease of sorting and filtering.
    """
    gc = gspread.oauth(scopes)
    workbook = gc.open_by_url(url)
    gcpr_sheet = workbook.worksheet("GCPR")
    vmv_sheet = workbook.worksheet("VMV")
    vcbm_sheet = workbook.worksheet("VCBM")
    joint_sheet = workbook.worksheet("JOINT")

    df_gcpr = pd.DataFrame(gcpr_sheet.get_all_records())
    df_vmv = pd.DataFrame(vmv_sheet.get_all_records())
    df_vcbm = pd.DataFrame(vcbm_sheet.get_all_records())
    df_joint = pd.DataFrame(joint_sheet.get_all_records())

    # create a dictionary with all the sheets of the workbook
    all_sheets = dict()
    all_sheets["GCPR"] = df_gcpr
    all_sheets["VMV"] = df_vmv
    all_sheets["VCBM"] = df_vcbm
    all_sheets["JOINT"] = df_joint

    return all_sheets



