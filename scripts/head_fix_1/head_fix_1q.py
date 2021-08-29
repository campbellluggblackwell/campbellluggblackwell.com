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


def get_viewport_metas(soup):
    # TODO: Simplify logic
    meta_tags = [meta for meta in soup.find_all('meta')]
    meta_tags = [meta for meta in meta_tags if "name" in meta.attrs.keys()]
    meta_tags = [meta for meta in meta_tags if meta.attrs['name'] == "viewport"]
    return meta_tags


def get_charset_metas(soup):
    meta_tags = [meta for meta in soup.find_all('meta')]
    meta_tags = [meta for meta in meta_tags if "http-equiv" in meta.attrs.keys()]
    meta_tags = [meta for meta in meta_tags if "charset" in meta.attrs['content']]
    return meta_tags

def html_text_spaces_clean(in_string):
    return re.sub('\n\s+', ' ', in_string).strip()


def main(input_base_path:str, output_base_path:str) -> None:
    # Process each .html file
    embed()
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

        # META charset
        # Delete any that exist.  Put in a correct one.
        charset_metas = get_charset_metas(soup)
        for _cs in charset_metas:
            _cs.decompose()
        new_meta = soup.new_tag('meta')
        new_meta.attrs['http-equiv'] = "content-type"
        new_meta.attrs['content'] = "text/html; charset=UTF-8"
        newline = NavigableString('\n')
        soup.head.insert(0, new_meta)
        soup.head.insert(0, newline)

        # META Viewports
        # Leave alone if already one there.  Otherwise, put in a correct one.
        viewport_metas = get_viewport_metas(soup)
        if not viewport_metas:
            new_meta = soup.new_tag('meta')
            new_meta.attrs['name'] = 'viewport'
            new_meta.attrs['content'] = "width=device-width, initial-scale=1.0"
            newline = NavigableString('\n')
            soup.head.insert(0, new_meta)
            soup.head.insert(0, newline)

        # Delete: <meta content="OpenOffice.org 3.3 (Win32)" name="GENERATOR"/>
        open_office = soup.find_all('meta', {
            'content':"OpenOffice.org 3.3 (Win32)",
            'name': "GENERATOR"
        })
        for tag in open_office:
            tag.decompose()

        # Add lang="en" to <html>
        for tag in soup.find_all('html'):
            tag['lang'] = 'en'

        # Remove: <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        for item in soup.contents:
            if isinstance(item, Doctype):
                item.extract()

        # Add <!DOCTYPE html> to top of file
        tag = Doctype('html')
        soup.insert(0, tag)
        # Remove any added space just below doctype html
        if soup.contents[1].string == '\n':
            soup.contents[1].extract()


        # Run through tidy
        html, errors = tidy_document(
            soup,
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
    print("Starting...")
    # Disable base options
    tidylib.BASE_OPTIONS = {}
    # main('../../website', './cleaned')
    main('../test_cases', './cleaned')
