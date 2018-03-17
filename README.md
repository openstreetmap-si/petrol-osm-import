# Preparation of gas station data from Petrol.si for import into OpenStreetmap.org

Scrapes the Petrol fuel and charging station data from http://www.petrol.si/bencinski-servisi/zemljevid into a format suitable for importing into [OpenStreetMap](https://www.openstreetmap.org).

OpenStreetMap wiki about gas stations in Slovenia: https://wiki.openstreetmap.org/wiki/WikiProject_Slovenia/Storitve#Bencinske_.C4.8Drpalke

Output in format for [OSM Conflator](https://wiki.openstreetmap.org/wiki/OSM_Conflator)

Requirements: python and pip

Run via GNU `make`, using the included [Makefile](Makefile), which:
1. Prepares the python virtual environment
2. Installs all needed dependencies as defined in [requirements.txt](requirements.txt)
3. Executes scraping using [scrape-petrol.py](scrape-petrol.py), which
    * Fetches http://www.petrol.si/bencinski-servisi/zemljevid 
    * Tags the nodes as defined in  [tags-mapping.yaml](tags-mapping.yaml)
    * filters the nodes to Slovenia only (via the is_in tag) - it can easily be adapted for other countries
    * Fetches all the individual gas station pages for exact opening times (using mapping in [openingtimes.yaml](openingtimes.yaml))
      Requests are cached aggressively in webcache.sqlite, so make sure to delete it when you want to scrape fresh data, typically the last time before import


4. Executes [OSM conflator](https://wiki.openstreetmap.org/wiki/OSM_Conflator) with [petrol-si-profile.py](petrol-si-profile.py)



Scraper is expecting javascript lines with data in format:

    createMarker(new google.maps.LatLng(45.1234567800,15.8765432100), '<div>marker html</div>', ' tag one tag two tag three ', 1);

This **exercise** is a work in progress, not yet fully ready for use.
Still **TODO**:
* add leading zeros to opening_hours
* scrape phone, fax and address
* get approval from data owners (they do publish simpler datasets for gps devices) they will most likely be ok with it, as it is in their best interest to be on the map
* get community approval 
    * list the possible import in the OSM import catalogue
    * global imports@ mailing list, 
    * local forum, 
    * review
* review the proposed changes with [OSM conflator audit system](https://github.com/mapsme/cf_audit)
* import the reviewed data into the OSM using JSON

