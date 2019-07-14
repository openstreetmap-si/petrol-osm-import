# Petrol.si gas stations for OpenStreetMap.org

Scrapes the [map on petrol.si](https://www.petrol.si/bencinski-servisi/zemljevid) for their fuel and charging station data and converts it to a format suitable for importing into [OpenStreetMap](https://www.openstreetmap.org), while preserving existing data.

[![Build Status](https://travis-ci.org/openstreetmap-si/petrol-osm-import.svg?branch=master)](https://travis-ci.org/openstreetmap-si/petrol-osm-import)
[![Requirements Status](https://requires.io/github/openstreetmap-si/petrol-osm-import/requirements.svg?branch=master)](https://requires.io/github/openstreetmap-si/petrol-osm-import/requirements/?branch=master)

Note: this is currently broken due to sourece website changes. New source starting point could be a [JSON endpoint](https://www.petrol.si/restservices/sales-service/filterStores?lngFrom=13.261230157575028&lngTo=16.702697442731278&latFrom=45.36648596761669&latTo=46.919187463685276&types=).

[OpenStreetMap wiki about gas stations in Slovenia](https://wiki.openstreetmap.org/wiki/WikiProject_Slovenia/Storitve#Bencinske_.C4.8Drpalke)

## Result preview
Full-screen preview of the derived changes is available [here](https://openstreetmap-si.github.io/petrol-osm-import/)

## Running
Requirements: python and pip

Run via GNU `make`, using the included [Makefile](Makefile), which:
1. Prepares the python virtual environment
2. Installs all needed dependencies as defined in [requirements.txt](requirements.txt)
3. Executes scraping using [scrape-petrol.py](scrape-petrol.py), which
    * Fetches [https://www.petrol.si/bencinski-servisi/zemljevid](https://www.petrol.si/bencinski-servisi/zemljevid) 
    * Tags the nodes as defined in  [tags-mapping.yaml](tags-mapping.yaml)
    * filters the nodes to Slovenia only (via the is_in tag) - it can easily be adapted for other countries
    * Fetches all the individual gas station pages for exact opening times (using mapping in [openingtimes.yaml](openingtimes.yaml))
      Requests are cached aggressively in webcache.sqlite, so make sure to delete it when you want to scrape fresh data, typically the last time before import
    * generates file `petrol-si-scraped.json`


4. Executes [OSM conflator](https://wiki.openstreetmap.org/wiki/OSM_Conflator) with [petrol-si-profile.py](petrol-si-profile.py) and generates 
    * `existingdata.osm` - existing data from OpenStreetMap
    * `petrol-si.osm` - osmChange file for import (do **NOT** import anything until community approval!!!)
    * [petrol-si-changes.geojson](petrol-si-changes.geojson) - proposed changes preview, in git only for easy preview and diff history



Scraper is expecting javascript lines with data in format:

    createMarker(new google.maps.LatLng(45.1234567800,15.8765432100), '<div>marker html</div>', ' tag one tag two tag three ', 1);

## Status
This **exercise** is a work in progress, not yet fully ready for use.
Still **TODO**:
* [x] add leading zeros to opening_hours
* [ ] scrape phone, fax and address
* [ ] get approval from data owners (they do publish simpler datasets for gps devices) they will most likely be ok with it, as it is in their best interest to be on the map
* [ ] get community approval 
    * [ ] list the possible import in the OSM import catalogue
    * [ ] global imports@ mailing list, 
    * [ ] local forum, 
    * [ ] review
* [ ] review the proposed changes with [OSM conflator audit system](https://github.com/mapsme/cf_audit)
* [ ] import the reviewed data into the OSM using JSON

