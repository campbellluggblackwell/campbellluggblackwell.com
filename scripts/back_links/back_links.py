# Comment out links to wc.rootsweb
# Description in gmail ~ 11-01-2022
#
# rlugg 2022-11-21
"""
* each footnote is a "list element",<li> ... </li>, within an ordered list <ol>...</ol>
    - A snippet needs to be inserted just before the </li> or </p></li>
        - It's content is a function of info found within the <li> clause.
* in each reference to a footnote
    - the snippet inserted there is a function of data present in the <a> tag.

## Testcase
Compare WBTMemoirCareerOld.html with WBTMemoirCareer.html

## In detail
Let's take the first footnote as an example. In the <main> section of the file, the footnote reference is:
    <p>My first job with a weekly paycheck almost killed me. The job was
              with the circulation department of a daily newspaper as a "truck
              boy.<a aria-describedby="Endnote-label" href="#TruckBoy"
                id="TruckBoy-ref"></a></p>
where the ID clause has been added. I think I'll want an additional clause added right after that, role="doc-noteref"
but I need to test that and will get back to you quickly. The pattern is that the content of the "id" clause is exactly the same as the "href" clause -- except for dropping the leading '#' and appending  "-ref".

...find <a aria- and add id and role="doc-noteref".  Check for duplicates!



In the <footer> section of the file, each footnote begins with 
         <li id="TruckBoy"> and ends with </li> or </p></li>
Note that the ID clause doesn't have a #. 
<a href="#TruckBoy-ref"
                  aria-label="Back to content">↵</a></p></li>

An additional case. Some of the endnote/footnotes  end with </figcaption></figure></li>

I also change the author's note at the beginning of the content to refer to the "backlink" special character, but that only has one occurrence per file and I can just copy and paste that.

Probably it wouldn't do any harm if the insertion was made twice, but let's not add it a 2nd time if it's already there.

How to know which files to update? I can either give you a list or you could just scan each file and ignore files that don't contain aria-.
"""



import bs4
import glob
from IPython import embed
import jinja2
from jinja2 import Template
import os
from pathlib import Path
from bs4 import BeautifulSoup, Tag
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

    for original_file in tqdm(original_files):

        soup = load_soup_file(original_file)
        has_changed = False

        # main links to footnotes
        aria_arefs = dict()
        for anchor in soup.find_all('a'):
            if 'aria-describedby' in anchor.attrs:
                href_value = anchor['href']
                if href_value[0]=='#':
                    href_value = href_value[1:]
                else:
                    raise Exception(f"No hash for {anchor.attrs}")

                anchor['id'] = f"{href_value}-ref"
                anchor['role'] = "doc-noteref"
                aria_arefs[href_value] = anchor
                has_changed = True
                continue


        # Footnote links
        aria_footnotes = dict()
        for list_item in soup.find_all('li'):
            if 'id' in list_item.attrs:
                id = list_item.attrs['id']
                if id not in aria_arefs.keys():
                    continue
                print(f"Found something! {list_item.attrs}")
                # embed()
                if 'aria-label' not in list_item.attrs:
                    aref = Tag(None, name="a", attrs={'href': f"#{id}-ref", "aria-label":"Back to content"})
                    aref.append('↵')
                    aria_footnotes[id] = aref
                    list_item.contents.append(aref)

        # Error if lists don't match
        merged_keys = set(aria_arefs.keys()).union(aria_footnotes.keys())
        if len(merged_keys) != len(aria_arefs):
            print(f"Mismatch of a structures in {original_file}")
            print(f"aria_arefs: {aria_arefs.keys()}")
            print(f"aria_footnotes: {aria_footnotes.keys()}")
        # Only save if changed.  This is to make git checkin diffs more useful
        if has_changed:
            html = str(soup)
            output_file = Path(os.path.join(output_path, original_file.name))
            with open(output_file, 'w') as fp:
                fp.write(html)
            print(f"File: {original_file.name} was changed.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("website and output directories required.")
    print("Starting...")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
    print("Finished.")