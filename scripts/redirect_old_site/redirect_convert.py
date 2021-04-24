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

base_path = 'sites.rootsweb.com/~capane/'
original_files = glob.glob(base_path + '*.html')
output_directory = Path("./capane_redirects")
try:
    output_directory.mkdir()
except:
    pass

with open('redirect_template.jinja2', 'r') as fp:
    template_text = fp.read()

template = Template(template_text)

for _original_file_as_str in original_files:
    original_file = Path(_original_file_as_str)

    print(f"{base_path + original_file.name}")
    try:
        with open(base_path + original_file.name, 'r', encoding='cp1252') as fp:
            original_html = fp.read()
    except Exception as e:
        print(f"Can't process file: {base_path + original_file.name}")
        print("  Adding a generic title in that case.")
        original_html = ""
    soup = BeautifulSoup(original_html, features="html.parser")
    try:
        page_title = soup.title.string
    except AttributeError:
        page_title = ""
    output_html = template.render(page_title=page_title, filename=original_file.name)

    # Just to make the HTML a bit prettier before writing
    soup = BeautifulSoup(output_html, features="html.parser")
    output_pretty_html = soup.prettify()
    output_file = Path(os.path.join(output_directory, original_file.name))
    with open(output_file, 'w') as fp:
        fp.write(output_pretty_html)