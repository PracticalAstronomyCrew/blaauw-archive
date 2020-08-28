col_list=definitions/column-list.csv
doc_file=definitions/doc.rst

target_dir=generated
rd_file=$(target_dir)/q.rd
table_file=$(target_dir)/table.sql

gen_file=src/generate.py  

generate: $(gen_file) $(col_list) $(doc_file)
	mkdir -p $(target_dir)
	python3 $(gen_file) $(col_list) $(doc_file) $(rd_file) $(table_file)

clean:
	rm -r $(target_dir)
