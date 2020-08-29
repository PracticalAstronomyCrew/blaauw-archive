# Files for generate commands
col_list=definitions/column-list.csv
doc_file=definitions/doc.rst

target_dir=generated
rd_file=$(target_dir)/q.rd
table_file=$(target_dir)/table.sql

gen_file=src/generate.py  

# Gavo directories
schema_name=observations
base_dir=/var/gavo

input_dir=$(base_dir)/inputs/$(schema_name)
web_dir=$(base_dir)/web

## Commands
reload: generate reload-rd publish-rd

# Static resources (images, templates etc.)
move-logo:
	mkdir -p $(web_dir)/nv_static/img
	cp resources/rug-logo.png  $(web_dir)/nv_static/img/logo_medium.png

# Data resources
generate: $(gen_file) $(col_list) $(doc_file)
	mkdir -p $(target_dir)
	python3 $(gen_file) $(col_list) $(doc_file) $(rd_file) $(table_file)

reload-rd:
	mkdir -p $(input_dir)
	cd $(input_dir)
	pwd
	cp $(rd_file) $(input_dir)/q.rd
	dachs imp -m $(schema_name)/q.rd

publish-rd:
	dachs pub $(schema_name)/q.rd

create-db:
	# WARNING: Removes all data in the db!!!!
	psql dachs -f $(table_file)

restart:
	sudo systemctl restart dachs.service

clean:
	rm -r $(target_dir)
