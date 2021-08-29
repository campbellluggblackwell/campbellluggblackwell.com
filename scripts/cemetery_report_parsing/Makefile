
# Cemetery data from *.csv files

export source_dir?=./RM7Burials.txt
export destination_dir?=./output

all:
	export LD_LIBRARY_PATH=../tidy/;  \
	python cemetery_csv_parsing.py $(source_dir) $(destination_dir); \
