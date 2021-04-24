"""
Program to clean campbellLuggBlackwell web pages.

TIDY only

"""


import glob
from IPython import embed
import os
import re
from pathlib import Path
import sys

import tidylib
from tidylib import tidy_document


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


def main(input_base_path:str, output_base_path:str) -> None:
    # Process each .html file
    input_base_path = input_base_path + '/'
    original_files = glob.glob(input_base_path + '*.html')
    output_directory = Path(output_base_path)

    try:
        output_directory.mkdir()
    except:
        pass

    for _original_file_as_str in original_files:

        original_file = Path(_original_file_as_str)
        original_full_filename = input_base_path + original_file.name

        html = load_html_file(original_full_filename)

        html, errors = tidy_document(
            html,
            options= {
                "indent": 1,           # Pretty; not too much of a performance hit
                "tidy-mark": 0,        # No tidy meta tag in output
                "doctype": 'html5',
                "drop-empty-elements": 0,
                "drop-empty-paras": 0,
                "add-meta-charset": 1,
                "logical-emphasis": 1,
                "wrap": 80
            })

        # embed()

        output_file = Path(os.path.join(output_directory, original_file.name))
        with open(output_file, 'w') as fp:
            fp.write(html)

if __name__ == "__main__":
    # Disable base options
    tidylib.BASE_OPTIONS = {}
    main('../../website', './cleaned')
    # main('../test_cases', './cleaned')
