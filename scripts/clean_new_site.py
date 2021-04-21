"""
Program to clean campbellLuggBlackwell web pages.

Tasks:
 - delete all old viewport meta data and add a new one
 - delete all old charset meta data and add new one
rlugg 2021-04-12
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

        # META robots
        # If one exists, leave it alone.  Otherwise add one
        robots = soup.find_all('meta', {
            'name': "robots"
        })
        if not robots:
            new_meta = soup.new_tag('meta')
            new_meta.attrs['name'] = "robots"
            new_meta.attrs['content'] = "index,follow"
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

        # Delete any empty titles
        for tag in soup.find_all('title'):
            if not tag.contents:
                tag.decompose()

        # Remove any <font></font> that is identical to its parent
        for tag in soup.find_all('font'):
            if tag.parent.name == tag.name:
                if tag.parent.attrs.keys() == tag.attrs.keys():
                    tag.parent.unwrap()

        # Remove any <big></big> that is identical to its parent
        for tag in soup.find_all('big'):
            if tag.parent.name == tag.name:
                if tag.parent.attrs.keys() == tag.attrs.keys():
                    tag.parent.unwrap()

        # Modify freepages links to local if possible.
        # Is it from rootsweb?  Does it have the same filename locally?
        for tag in soup.find_all('a'):
            try:
                parsed = urlparse(tag['href'])
            except:
                print(f"Strange tag: {tag}\n")
                continue
            if parsed.netloc != 'freepages.genealogy.rootsweb.ancestry.com':
                continue
            filename = Path(parsed.path).name
            full_filename = Path(input_base_path + filename)
            if full_filename.is_file():
                # Everything is OK to change link.
                tag['href'] = filename

        # Clean spaces inside of <a> </a> strings
        for tag in soup.find_all('a'):
            if len(tag.contents) == 1:
                tag.string = html_text_spaces_clean(tag.string)

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

        # remove spaces around text several tags:
        for tag in soup.find_all(['title', 'h1', 'h2', 'h3', 'h4']):
            if len(tag.contents) == 1:
                tag.string = html_text_spaces_clean(tag.string)

        # <head> reduce blank lines
        for tag in soup.head.contents[1:]:
            if tag.string == '\n' and tag.previous_sibling.string == '\n':
                tag.extract()

        # <head> indent each tag inside 4 spaces
        # Note the two passes.  Its required because inserting in .contents
        # while looping will cause an infinite loop.
        head_tags = list()
        for tag in soup.head.contents:
            if tag.string == '\n':
                continue
            head_tags.append(tag)
        for tag in head_tags:
            indent = NavigableString('    ')
            tag.insert_before(indent)
        
        # Add a newline after </head> for .html readability
        newline = NavigableString('\n')
        soup.head.insert_after(newline)

        # fix html checker:
        # "The type attribute for the style element is not needed and should be omitted.""
        for tag in soup.find_all('style'):
            del tag['type']

        ## Table Cleaning

        # <td> </td> try to keep to one line
        for tag in soup.find_all('td'):
            if len(tag.contents) > 1:
                if tag.contents[-1].string == '\n':
                    tag.contents[-1].extract()
            if len(tag.contents) > 1:
                if tag.contents[0].string == '\n':
                    tag.contents[0].extract()

        print("At end")
        #embed()

        # ! Remember to use soup.prettify() ONLY for visuals.  Always write as str(soup)
        # ! Otherwise whitespace and other formatting is gone.
        output_file = Path(os.path.join(output_directory, original_file.name))
        with open(output_file, 'w') as fp:
            fp.write(str(soup))

if __name__ == "__main__":
    #main('./campbell_new_website_20210417', './cleaned')
    main('./test_cases', './cleaned_test_cases')