"""
Process all through tidy-html5

"""


import glob
from IPython import embed
import os
from pathlib import Path
### REMEMBER
# set LD_LIBRARY_PATH to this directory so libtidy.so can be found
# ln -s from libtidy.so to libtidy.so.5 so that this can find it.
from tidylib import tidy_document

def load_html_file(filename):
    """
        Load .html file.
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
        
        html = load_html_file(original_full_filename)
        document, errors = tidy_document(html)


        output_file = Path(os.path.join(output_directory, original_file.name))
        with open(output_file, 'w') as fp:
            fp.write(document)

if __name__ == "__main__":
    main('../website', '../cleaned_website')
    # main('./test_cases', './cleaned_test_cases')
