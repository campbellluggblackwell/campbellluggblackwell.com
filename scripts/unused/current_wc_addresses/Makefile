
export descendency_page_path?=../../old_rootsweb_descendancy_page/DescendancyPage.html
export rootsweb_path?=../../old_rootsweb_website/

all:
	export LD_LIBRARY_PATH=../tidy;  \
	python current_wc.py $(descendency_page_path) $(rootsweb_path); \
	# cp -ru cleaned/* ../../website/  # copy only modified files

