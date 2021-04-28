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


def main(input_base_path:str) -> None:

    input_base_path = input_base_path + '/'
    original_files = glob.glob(input_base_path + '*.html')
    if len(original_files)==0:
        print("Warning: No html files found.  Directory may be incorrect.")
    out = list()
    out.append("Files that do not have a META description")
    out.append(f'Report Ran:{time.strftime("%Y-%m-%d %H:%M")}')
    out.append("-------")
    out.append('<table style="text-align:right;">')
               
    for original_file_as_str in original_files:

        original_file = Path(original_file_as_str)
        original_full_filename = input_base_path + original_file.name

        soup = load_soup_file(original_full_filename)

        has_description = False
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if 'name' not in tag.attrs:
                continue
            if tag.attrs['name'] != 'description':
                continue
            if 'content' not in tag.attrs:
                continue
            has_description = True
        if not has_description:
            _fn = Path(original_file_as_str).name
            out.append(f'<tr><td><a href="{_fn}">_fn</a></td></tr>')

    out.append("</table>")
    # Run through tidy
    options = load_tidy_options()
    html, errors = tidy_document(
        '\n<br/>'.join(out),
        options= options)

    # embed()

    output_file = './missing_descriptions.html'
    with open(output_file, 'w') as fp:
        fp.write(html)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Must input a directory.")
    print("Starting...")
    # Disable base options
    tidylib.BASE_OPTIONS = {}
    main(sys.argv[1])
    # main('./test_cases')
    print("Finished.")



