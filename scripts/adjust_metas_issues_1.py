"""
Clean meta

"""


import glob
from IPython import embed
#import jinja2
#from jinja2 import Template
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Doctype
from urllib.parse import urlparse


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

def load_soup_file(filename):
    """
            # Load in .html file into beautiful soup
        # Some files are utf-8 and others are cp1252.  Need to load them differently.
    """
    print(f"{filename}")
    try:
        with open(filename, 'r', encoding='utf8') as fp:
            original_html = fp.read()
    except UnicodeDecodeError as e:
        try:
            with open(filename, 'r', encoding='cp1252') as fp:
                original_html = fp.read()
        except Exception as e:
            raise Exception(f"Can't process file: {filename}\n{e}\n")
    soup = BeautifulSoup(original_html, features="html.parser")
    return soup


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

        has_changed = False

        original_file = Path(_original_file_as_str)
        original_full_filename = input_base_path + original_file.name
        soup = load_soup_file(original_full_filename)


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
            has_changed = True

        # Before the viewport, add the charset line
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
        has_changed = True

        # Delete: <meta content="OpenOffice.org 3.3 (Win32)" name="GENERATOR"/>
        open_office = soup.find_all('meta', {
            'content':"OpenOffice.org 3.3 (Win32)",
            'name': "GENERATOR"
        })
        for tag in open_office:
            tag.decompose()
            has_changed = True


        print("At end")
        #embed()

        # ! Remember to use soup.prettify() ONLY for visuals.  Always write as str(soup)
        # ! Otherwise whitespace and other formatting is gone.
        if has_changed:
            output_file = Path(os.path.join(output_directory, original_file.name))
            with open(output_file, 'w') as fp:
                fp.write(str(soup))

if __name__ == "__main__":
    main('../website', '../cleaned_website')
    # main('./test_cases', './cleaned_test_cases')