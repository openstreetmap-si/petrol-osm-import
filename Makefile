SHELL := /bin/bash

petrol-si.osm: requirements petrol-si-scraped.json
	# run the conflate of scraped json in the virtual environment with all the requirements met
	source venv/bin/activate; \
	conflate petrol-si-profile.py --source petrol-si-scraped.json -o petrol-si.osm --osc --osm existingdata.osm --changes petrol-si-changes.geojson --verbose

petrol-si-scraped.json: requirements
	# run the web page scraping in the virtual environment with all the requirements met
	source venv/bin/activate; \
	python scrape-petrol.py petrol-si-scraped.json

requirements: requirements.txt.out
	# install requirements if requirements.txt.out is missing or older than requirements.txt

requirements.txt.out: venv requirements.txt
	# install the requirements into virtual environments and record the action to requirements.txt.out
	source venv/bin/activate && pip install -r requirements.txt | tee requirements.txt.out

venv:
	# basic setup
	pip install virtualenv
	virtualenv venv

test: petrol-si-scraped.json
	wc -l petrol-si-scraped.json

clean:
	# clean up all generated artefacts
	rm -f existingdata.osm
	rm -f requirements.txt.out
	# rm -f webcache.sqlite
	rm -rf venv
	rm -f *.pyc
	rm -f petrol-si-scraped.json
	rm -f petrol-si.osm 
	rm -f existingdata.osm
	rm -f petrol-si-changes.geojson