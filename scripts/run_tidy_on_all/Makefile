
# Find duplicate repeating tags and remove one:
#  <big><big>
#  <font><font>

export source_dir?=../../website
export destination_dir?=./cleaned

all:
	export LD_LIBRARY_PATH=../tidy/;  \
	python run_tidy_on_all.py $(source_dir) $(destination_dir); \
