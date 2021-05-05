"""
Program to Report problems.

"""


import glob
from IPython import embed
import os
import re
from pathlib import Path
import sys

from bs4 import BeautifulSoup, NavigableString, Doctype
from urllib.parse import urlparse
import tidylib
from tidylib import tidy_document
import time

def load_html_file(filename):
    """
        Load in .html file
        Some files are utf-8 and others are cp1252.  Need to load them differently.
    """
    print(f"{filename}")
    try:
        with open(filename, 'r', encoding='utf8') as fp:
            html = fp.read()
    except UnicodeDecodeError as e:
        try:
            with open(filename, 'r', encoding='cp1252') as fp:
                html = fp.read()
        except Exception as e:
            raise Exception(f"Can't process file: {filename}\n{e}\n")
    return html


def load_soup_file(filename):
    """
            # Load in .html file into beautiful soup
    """
    html = load_html_file(filename)
    soup = BeautifulSoup(html, features="html.parser")
    return soup

def load_tidy_options():
    with open('../tidy_config.txt', 'r') as fp:
        _c = fp.read()
    _c2 = [line for line in _c.split('\n') if not line.startswith('//')]
    _c3 = {s.split(':')[0].strip():s.split(':')[1].strip() for s in _c2}
    return _c3


def main(old_website_path:str, new_website_path:str) -> None:

    this_dir = os.getcwd()
    os.chdir(old_website_path)
    original_files = glob.glob('./*')
    if len(original_files)==0:
        print("Warning: No files found.  Old directory may be incorrect.")
    os.chdir(this_dir)
    os.chdir(new_website_path)
    new_files = glob.glob('./*')
    if len(new_files)==0:
        print("Warning: No files found.  New directory may be incorrect.")
    os.chdir(this_dir)

    out = list()
    out.append("Files in rootsweb that don't have a corresponding Bluehost file")
    out.append(f'Report Ran:{time.strftime("%Y-%m-%d %H:%M")}<br>')
    out.append("-------<br>")
    out.append('<table style="text-align:right;">')

    any_bad = False
    for original_file in original_files:
        if original_file not in new_files:
            any_bad = True
            out.append(f'<tr><td>{original_file}</td></tr>')
    out.append("</table>")
    if not any_bad:
        out.append("(No missing files found)")
    # Run through tidy
    options = load_tidy_options()
    html, errors = tidy_document(
        '\n'.join(out),
        options= options)

    output_file = './missing_old_files.html'
    with open(output_file, 'w') as fp:
        fp.write(html)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("source and destination directory required.")
    print("Starting...")
    main(sys.argv[1], sys.argv[2])
    print("Finished.")



