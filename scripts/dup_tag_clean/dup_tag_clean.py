"""
Fix bad tags
 - Redundant <big> and <font> tags
 - tags with no content (or all whitespace) (except <p> which turns into <br>)

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
from tqdm import tqdm

def load_html_file(filename):
    """
        Load in .html file
        Some files are utf-8 and others are cp1252.  Need to load them differently.
    """
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


def tag_is_essentially_empty(tag):
    if len(tag.contents) > 1:
        return False
    if len(tag.contents) == 0:
        return True
    if tag.string is None:
        return False
    if len(tag.string.strip()) == 0:
        return True
    return False


def tag_is_identical_to_parent(tag):
    if tag.parent.name == tag.name: # name matches
        if tag.parent.attrs.keys() == tag.attrs.keys(): # keys match
            for k in tag.attrs:
                if tag.parent.attrs[k] != tag.attrs[k]:
                    return False
            return True


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

    for _original_file_as_str in tqdm(original_files):

        original_file = Path(_original_file_as_str)
        original_full_filename = input_base_path + original_file.name
        soup = load_soup_file(original_full_filename)

        file_modified = False

        # if original_file.name == 'CampbellCemListAA_AZ.html':
        #     embed()
        # Remove any <big></big> that is identical to its parent.
        # NO! because multiple "big"s actually change the size.
        if False:
            for tag in soup.find_all('big'):
                if tag_is_identical_to_parent(tag):
                    tag.parent.unwrap()
                    file_modified = True

        # Convert any empty <p> tags into <br>
        for tag in soup.find_all('p'):
            if tag_is_essentially_empty(tag):
                br = soup.new_tag('br')
                tag.insert_before(br)
                tag.decompose()
                file_modified = True

        # Now remove some remaining empty tags
        # Loop to remove <p><font></font></p> - like nested empty tags
        keep_looping = True
        while keep_looping:
            keep_looping = False
            to_check = ['p', 'caption', 'big', 'font']
            for tag in soup.find_all(to_check):
                if tag_is_essentially_empty(tag):
                    tag.decompose()
                    file_modified = True
                    keep_looping = True

        if False: # Skipped
            # Remove spaces in text
            to_check = ['p', 'title', 'td']
            for tag in soup.find_all(to_check):
                if tag.string is None:
                    continue
                despaced = html_text_spaces_clean(tag.string)
                if despaced != tag.string:
                    tag.string = despaced
                    file_modified = True

        # Remove sdval and sdnum from <td> tags
        # github issue #20
        for tag in soup.find_all(['td']):
            for att in ['sdval', 'sdnum']:
                if att in tag.attrs:
                    del tag[att]
                    file_modified = True

        if not file_modified:
            continue  # Don't write it to 'cleaned' if unchanged.

        
        # Run through tidy
        html, errors = tidy_document(
            str(soup),
            options= tidy_options )

        # Double check something was actually changed
        # (since tidy may restore things like extra spaces)

        original_html = load_html_file(original_full_filename)
        if html == original_html:
            continue

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

'''
Note:
if len(tag.get_text(strip=True)) == 0:
is a bit too loose.  If there are <br/> inside the tag, then it considers it empty.
Generally, don't use the .get_text(strip=True) to check if tags are empty.
'''