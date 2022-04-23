# Update rootsweb links
#
# rlugg 2022-04-22
#
# From Bill:
# I'd like to run a script on all our HTML files to revise the links that refer to "freepages."

# For example, change
# <a href="http://freepages.genealogy.rootsweb.ancestry.com/%7Ecapane/index.html">Return Home</a>
# to
# <a href="index.html">Return Home</a>
# where, the filename between the 
# "capane/" and the ".html" would be a wild card.

# Of course, sometimes in the present files it may appear as  ...ancestry.com/~capane...

# And after updating the HTML files, then we'd publish the revised pages on our BlueHost site.

# I don't see a need to process the files with an extension of .html.bak or .~html.


import bs4
import glob
from IPython import embed
import jinja2
from jinja2 import Template
import os
from pathlib import Path
from bs4 import BeautifulSoup
import sys
import tidylib
from tidylib import tidy_document
import httplib2
from typing import Any
from tqdm import tqdm


def is_a_webpage(url):
    """ Checks url argument to determine if it is a working webpage """
    h = httplib2.Http()
    resp = h.request(url, 'HEAD')
    return int(resp[0]['status']) < 400


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


def load_soup_file(filename: str) -> Any:
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


def main(input_site_path, output_path):

    original_files = input_site_path.glob('*.html')
    try:
        output_path.mkdir()
    except FileExistsError:
        pass

    find_string = 'http://freepages.genealogy.rootsweb.ancestry.com/%7Ecapane/'

    for original_file in tqdm(original_files):
        soup = load_soup_file(original_file)
        has_changed = False
        # print(f"Processing: {original_file.name}")
        #print("74")
        #embed()

        for anchor in soup.find_all('a'):
            # If no href attribute, skip processing this anchor
            if 'href' not in anchor.attrs:
                continue

            if not find_string in anchor['href']:
                continue

            print(f'/n{anchor}/n')
            anchor['href'] = anchor['href'].replace(find_string, '')
            has_changed = True

        # Only save if changed.  This is to make git checkin diffs more useful
        if has_changed:
            html = str(soup)
            output_file = Path(os.path.join(output_path, original_file.name))
            with open(output_file, 'w') as fp:
                fp.write(html)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("website and output directories required.")
    print("Starting...")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
    print("Finished.")