
# Find duplicate repeating tags and remove one:
#  <big><big>

#export source_dir?=../test_cases
export source_dir?=../../website

export destination_dir?=./cleaned

multi_tag_clean:
	export LD_LIBRARY_PATH=./;  \
	python big_tag_clean.py $(source_dir) $(destination_dir); \
