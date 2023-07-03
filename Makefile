# Files for generate commands
col_raw_list=definitions/columns/raw.csv
col_head_list=definitions/columns/headers.csv
doc_file=definitions/doc.rst

target_dir=generated
rd_file=$(target_dir)/q.rd
table_file=$(target_dir)/table.sql

gen_file=src/generate.py

data_dir=../data

# Gavo directories
schema_name=observations
base_dir=/var/gavo

input_dir=$(base_dir)/inputs/$(schema_name)
web_dir=$(base_dir)/web

now := $(shell date +%Y%m%d-%H%M%S)

## Commands
reload: generate reload-rd publish-rd

# Static resources (images, templates etc.)
move-logo:
	mkdir -p $(web_dir)/nv_static/img
	cp resources/rug-logo.png  $(web_dir)/nv_static/img/logo_medium.png

# Data resources
generate: $(gen_file) $(col_head_list) $(doc_file)
	mkdir -p $(target_dir)
	python3 $(gen_file) $(col_head_list) $(doc_file) $(rd_file) $(table_file)

reload-rd:
	mkdir -p $(input_dir)
	cd $(input_dir)
	pwd
	cp $(rd_file) $(input_dir)/q.rd
	dachs imp -m $(schema_name)/q.rd

publish-rd:
	dachs pub -m $(schema_name)/q.rd

# Database stuff
# Use with care!
reload-db: create-db insert

create-db:
	# WARNING: Removes all data in the db!!!!
	psql dachs -f $(table_file)

insert:
	python3 src/insert.py $(data_dir)/headers.txt --raw $(col_raw_list) --header $(col_head_list) --use-db &> logs/$(now)-headers.log
	python3 src/insert.py $(data_dir)/processed-headers.txt --raw $(col_raw_list) --header $(col_head_list) --use-db &> logs/$(now)-processed-headers.log
	python3 src/insert.py $(data_dir)/out-2022-04-15/all-raw-headers.pickle --raw $(col_raw_list) --header $(col_head_list) --use-db &> logs/$(now)-processed-headers.log

restart:
	sudo systemctl restart dachs.service

clean:
	rm -r $(target_dir)


# Docker stuff
start-db:
	sudo docker run --restart=always -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -v postgres:/var/lib/postgresql/data postgres:14

