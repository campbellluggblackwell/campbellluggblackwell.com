"""
Program to clean metas and some tops of files

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


def html_text_spaces_clean(in_string):
    return re.sub('\n\s+', ' ', in_string).strip()


def main(input_base_path:str, output_base_path:str) -> None:

    tidy_options = load_tidy_options()
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

        soup = load_soup_file(original_full_filename)

        file_modified = False
        # Remove any <big></big> that is identical to its parent
        for tag in soup.find_all('big'):
            if tag.parent.name == tag.name: # name matches
                if tag.parent.attrs.keys() == tag.attrs.keys(): # keys match
                    for k in tag.attrs:
                        if tag.parent.attrs[k] != tag.attrs[k]:
                            continue
                    tag.parent.unwrap()
                    file_modified = True

        # Now remove any empty <big></big>
        for tag in soup.find_all('big'):
            if len(tag.contents) > 1:
                continue
            if len(tag.contents) == 0:
                tag.decompose()
                continue
            if tag.string is None:
                continue # No cleaning possible
            if len(tag.string.strip()) == 0:
                tag.decompose() # If stripped string is empty, delete
                file_modified = True


        #        tag.string = html_text_spaces_clean(tag.string)

        # # Delete: <meta content="OpenOffice.org 3.3 (Win32)" name="GENERATOR"/>
        # open_office = soup.find_all('meta', {
        #     'content':"OpenOffice.org 3.3 (Win32)",
        #     'name': "GENERATOR"
        # })
        # for tag in open_office:
        #     tag.decompose()
        # # Add lang="en" to <html>
        # for tag in soup.find_all('html'):
        #     tag['lang'] = 'en'

        # # Remove: <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        # for item in soup.contents:
        #     if isinstance(item, Doctype):
        #         item.extract()

        # # Add <!DOCTYPE html> to top of file
        # tag = Doctype('html')
        # soup.insert(0, tag)
        # # Remove any added space just below doctype html
        # if soup.contents[1].string == '\n':
        #     soup.contents[1].extract()


        if not file_modified:
            continue  # Don't write it to 'cleaned' if unchanged.
        
        # Run through tidy
        html, errors = tidy_document(
            str(soup),
            options= tidy_options )

        # embed()

        output_file = Path(os.path.join(output_directory, original_file.name))
        with open(output_file, 'w') as fp:
            fp.write(html)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("Must specify an input and an output directory.")
    # Disable base Tidy options
    tidylib.BASE_OPTIONS = {}
    print("Starting...")
    main(sys.argv[1], sys.argv[2])
    # main('./test_cases')
    print("Finished.")