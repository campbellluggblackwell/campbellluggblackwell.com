"""

Parse burial .CSV file to populate database

NOTE: Currently tab separation.  May change to , or not
"""

from IPython import embed
import numpy as np
import pandas as pd
import sys

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

*** Doesn't run now


def main(input_filename, output_directory):

    # Read in all columns.
    data = pd.read_csv(input_filename, sep='\t')

    # Split 'Burial Loc.' column and create new columns from it.
    bl = pd.DataFrame(data['Burial  Loc.'].str.split(','), columns=['Burial  Loc.'])

    # bl['Burial  Loc.'] now looks something like:
    # [Slate Run,  Brown Twp.,  Lycoming Co.,  PA]

    embed()
    # Handle USA case.  Parse State and country
    maybe_state = bl['Burial  Loc.'].apply(lambda x:x[-1])
    maybe_state = maybe_state.str.strip()
    is_a_state = maybe_state.apply(lambda x:x in states)

    # For states, the last column will be state and the next to last will be county
    burial_loc_in_usa = pd.DataFrame(bl['Burial  Loc.'][is_a_state])
    burial_loc_in_usa['country'] = 'USA'
    burial_loc_in_usa['state'] = burial_loc_in_usa['Burial  Loc.'].apply(lambda x:x[-1])
    burial_loc_in_usa['county'] = burial_loc_in_usa['Burial  Loc.'].apply(lambda x:x[-2])
    qq = burial_loc_in_usa['Burial  Loc.'].apply(lambda x:x[:-2])

    # Print warning message if the above state, country parsing didn't work
    country_is_na = bl['country'].isna()
    if country_is_na.sum() > 0:
        print("WARNING Parsing 'Burial  Loc.")
        print("Could not figure out how to parse some lines:")
        print(data[country_is_na])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("Must specify an input *.CSV and an output directory.")
    print("Starting...")

    # Pandas prints all rows during debugging.  Sometimes useful
    pd.set_option('display.max_rows', None)

    main(sys.argv[1], sys.argv[2])
    print("Finished.")