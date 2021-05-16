# Program to create redirection pages for each existing .html page
#
# Uses jinja2, BeautifulSoup4
#
# rlugg 2021-04-12

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


def main(old_site_path, new_site_path, redirects_out_path):

    # embed()
    original_files = old_site_path.glob('*.html')
    try:
        redirects_out_path.mkdir()
    except FileExistsError:
        pass

    with open('redirect_template.jinja2', 'r') as fp:
        template_text = fp.read()

    template = Template(template_text)

    for original_file in tqdm(original_files):
        # print(f"{original_file}")
        soup = load_soup_file(original_file)

        try:
            page_title = soup.title.string
        except AttributeError:
            page_title = ""

        # Confirm that there is a new file on the new site otherwise, report and point to index.html
        new_website_site_name = 'https://www.campbellluggblackwell.com'
        new_page_link = f'{new_website_site_name}/{original_file.name}'
        if not is_a_webpage(new_page_link):
            print(f'{original_file.name} does not exist on the new site.  Setting to index.html')
            new_page_link = f'{new_website_site_name}/index.html'
        
        # print("line48")
        # embed()

        # Render the redirect webpage
        output_html = template.render(page_title=page_title, filename=new_page_link)


        # Run through tidy
        options = load_tidy_options()
        html, errors = tidy_document(
            str(output_html),
            options= options)

        # embed()
        # Write redirect page
        output_file = Path(os.path.join(redirects_out_path, original_file.name))
        with open(output_file, 'w') as fp:
            fp.write(html)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise ValueError("old, new, and output redirects directories required.")
    print("Starting...")
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    print("Finished.")