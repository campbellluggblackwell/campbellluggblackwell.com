
# Find duplicate repeating tags and remove one:
#  <big><big>
#  <font><font>

export source_dir?=../../website
export destination_dir?=./cleaned

all:
	export LD_LIBRARY_PATH=../tidy/;  \
	python dup_tag_clean.py $(source_dir) $(destination_dir); \
