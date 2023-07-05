# Files for generate commands
target_dir=definitions
rd_file=$(target_dir)/blaauw.rd

data_dir=../data
logs_dir=./logs

# Gavo directories
schema_name=blaauw
base_dir=/var/gavo

input_dir=$(base_dir)/inputs/$(schema_name)
web_dir=$(base_dir)/web

now := $(shell date +%Y%m%d-%H%M%S)

## Commands
reload: reload-rd publish-rd

# Static resources (images, templates etc.)
move-logo:
	mkdir -p $(web_dir)/nv_static/img
	cp resources/rug-logo.png  $(web_dir)/nv_static/img/logo_medium.png

# Data resources
reload-rd:
	mkdir -p $(input_dir)
	cd $(input_dir)
	pwd
	cp $(rd_file) $(input_dir)/q.rd
	dachs imp -m $(schema_name)/q.rd

publish-rd:
	dachs pub -m $(schema_name)/q.rd

restart:
	sudo systemctl restart dachs.service


# Database stuff
# Use with care!
reload-db: create-db insert

create-db:
	# WARNING: Removes all data in the db!!!!
	# psql dachs -f $(table_file)
	mkdir -p $(logs_dir)
	python3 insert.py --reload-db &> $(logs_dir)/$(now)-create-db.log

insert:
	mkdir -p $(logs_dir)
	python3 insert.py --file $(data_dir)/latest-headers.txt &> $(logs_dir)/$(now)-insert.log
	python3 insert.py --file $(data_dir)/processed-headers.txt &>> $(logs_dir)/$(now)-insert.log


# Docker stuff
start-db:
	sudo docker run --restart=always -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -v postgres:/var/lib/postgresql/data postgres:14
	# docker exec -it postgres psql -U postgres
