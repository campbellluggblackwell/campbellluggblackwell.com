"""
Improve some of the link problems of WorldConnect.

This script is doing a number of things.  Essentially we have overlapping lists of relatives.
- Files on WorldConnect with "New" href addresses
- As links in our web pages with links to "Old" href addresses
- As links in our web pages with links to "New wikitree" href addresses
-- "As links" exist in both the web pages on rootsweb as well as those on Bluehost


"""


import glob
from IPython import embed
import os
import re
from pathlib import Path
import sys

import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)

from bs4 import BeautifulSoup, NavigableString, Doctype
from urllib.parse import urlparse

import tidylib
from tidylib import tidy_document

from typing import Any
from datetime import datetime


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


def load_soup_file(filename: str) -> Any:
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


def extract_from_descendancy_page(filename: str) -> pd.DataFrame:
    """ Rootsweb provides a "Descendancy_page".  Parse that"""

    soup = load_soup_file(input_descendancy_page_path)

    # From the new rootsweb page, find the new ID's by
    # examinging DescendancyPage.html of the family.
     
    new_rootsweb_from_descendancy_page = list()
    # Search DescendancyPage.html of the current rootsweb site.
    # Find New rootsweb ID, name, birth and death
    for span in soup.find_all('span', attrs = {'class': 'rwWcGreen'}):
        a_tag = span.next_sibling
        href = a_tag.attrs['href']
        i_number = href.split('/')[5][1:] # Grab only the Innnn portion of the href, then remove the 'I'
        name = a_tag.text
        dates_or_empty = a_tag.next_sibling.string  # Either a birth/death string, or nothing
        dates_str = dates_or_empty if dates_or_empty is not None else ''
        new_rootsweb_from_descendancy_page.append((i_number, name, dates_str))

    descendancy_page_with_duplicates = pd.DataFrame(new_rootsweb_from_descendancy_page)
    descendancy_page_with_duplicates.columns = ['new_rootsweb_id', 'name', 'bd_text']
    descendancy_page = descendancy_page_with_duplicates.drop_duplicates()
    return descendancy_page


def extract_a_links_from_website(input_htmls_path:str) -> pd.DataFrame:
    ### From our rootsweb site, extract all the <a> links
    ### pointing to wc.rootsweb.

    # Process each .html file
    input_htmls_path = input_htmls_path + '/'
    original_files = glob.glob(input_htmls_path + '*.html')

    links_from_old_rootsweb_site = list()
    for _original_file_as_str in original_files:

        original_file = Path(_original_file_as_str)
        original_full_filename = input_htmls_path + original_file.name
        soup = load_soup_file(original_full_filename)

        for a in soup.find_all('a'):
            if 'href' not in a.attrs:
                continue
            if 'db=capane&id=I' not in a.attrs['href']:
                continue
            if a.string is not None:
                text = re.sub('\n\s*', ' ', a.string).strip()
            else:
                text = ''

            id = a.attrs['href'].split('id=I')[1]
            try:
                _ = int(id)
            except:
                print(f'Failure parsing {a} in {original_file.name}')
                id = '0'  # Keep them as strings just in case leading 0's matter
            
            links_from_old_rootsweb_site.append((id, text, original_file.name, a.attrs['href']))

    rootsweb_a_links = pd.DataFrame(links_from_old_rootsweb_site)
    rootsweb_a_links.columns = ['old_rootsweb_id', 'name', 'source_html','href']

    return rootsweb_a_links


def exact_match(rootsweb_a_links, descendancy_page):

    rootsweb_a_links['match_type'] = np.NaN
    rootsweb_a_links['new_rootsweb_id'] = np.NaN

    # Match up exact matches where id's havent changed between
    # old and new wc web, and names match
    m = pd.merge(
        rootsweb_a_links,
        descendancy_page,
        how='left',
        left_on=['old_rootsweb_id', 'name'],
        right_on=['new_rootsweb_id', 'name']
    )
    m.index = rootsweb_a_links.index

    new_id_found = m['new_rootsweb_id_y'].notnull()
    rootsweb_a_links.loc[new_id_found, 'match_type'] = 'exact_match'
    rootsweb_a_links.loc[new_id_found, 'new_rootsweb_id'] = \
        m.loc[new_id_found, 'new_rootsweb_id_y']



def main(input_descendancy_page_path:str,
         input_rootsweb_path:str,
         output_base_path:str) -> None:

    descendancy_page = extract_from_descendancy_page(input_descendancy_page_path)

    rootsweb_a_links = extract_a_links_from_website(input_rootsweb_path)



    # Now, look for other entries which match ol rootwebs ids and assume name
    # differences are the cause of mismatches.
    _indexes = rootsweb_a_links['match_type']=='exact_match'
    exact_matches = rootsweb_a_links.loc[_indexes].drop_duplicates(
        ['old_rootsweb_id', 'name']
    )

    badee = pd.merge(
        rootsweb_a_links,
        exact_matches,
        how='left',
        on=['old_rootsweb_id']
    )
    badee.index = rootsweb_a_links.index

    # If row doesn't have a new_rootsweb_id yet, but a similar name does, then copy it.
    should_copy = badee['new_rootsweb_id_x'].isnull() & badee['new_rootsweb_id_y'].notnull()
    rootsweb_a_links.loc[should_copy, 'match_type'] = 'copied_from_exact_match'
    rootsweb_a_links.loc[should_copy, 'new_rootsweb_id'] = \
        badee.loc[should_copy, 'new_rootsweb_id_y']

    # keys = ['source_html', 'name', 'match_type','old_rootsweb_id']

    rootsweb_a_links['old_id_as_int'] = rootsweb_a_links['old_rootsweb_id'].astype(int)
    keys = ['old_id_as_int', 'match_type', 'name', 'source_html']
    rootsweb_a_links = rootsweb_a_links.sort_values(keys)
    rootsweb_a_links.drop('old_id_as_int', 1)

    # Rearrange columns to make printing better
    columns = ['old_rootsweb_id', 'new_rootsweb_id',  'name',  'match_type', 'source_html']
    rootsweb_a_links = rootsweb_a_links.reindex(columns,axis = 1)

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
        # print(rootsweb_a_links.to_string(index=False))


    rootsweb_a_links.to_csv('roots_match.csv', index=False)

    print("In main")
    embed()



    if False:
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
            str(soup),
            options= {
                "indent": 1,              # Pretty; not too much of a performance hit
                "tidy-mark": 0,           # No tidy meta tag in output
                "doctype": 'html5',
                "drop-empty-elements": 0,
                "drop-empty-paras": 0,
                "add-meta-charset": 1,
                "logical-emphasis": 1,
                "preserve-entities": 1,
                "literal-attributes": 1,
                "priority-attributes": "name,content,rel,href",
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
    main(sys.argv[1], sys.argv[2], './cleaned')
    # main('../test_cases', './cleaned')
