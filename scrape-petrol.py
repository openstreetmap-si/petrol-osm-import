# -*- coding: utf-8 -*-

import __future__
import csv, sys, json, copy, datetime, time, os, re, yaml
import requests, requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

def main(outpath):

    requests_cache.install_cache('webcache')

    # read yamls
    tag_map_dict = None
    with open("tags-mapping.yaml", 'r') as stream:
        try:
            tag_map_dict = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    # print(json.dumps(tag_map_dict, indent=2))

    openingTimesMapping = None
    with open("openingtimes.yaml", 'r') as stream:
        try:
            openingTimesMapping = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    # print(json.dumps(openingTimesMapping, indent=2))

    base_url = "https://www.petrol.si"
    url = base_url + "/bencinski-servisi/zemljevid"
    print("Scraping: " + url, file=sys.stderr)
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        exit(1)


    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    menuTags=[]

    menu = soup.select(".view-gas-station-properties a")
    if menu:
        for m in menu:
            menuTags.append(m.text)
            # for initial yaml construction
            # print(str(m.text) + ":")

    # add some tags that are not in the menu...
    if "Hrvaška" not in menuTags:
        menuTags.append("Hrvaška")

    # longest tags first to avoid partial matches
    menuTags.sort(key = len, reverse=True)
    # menuTags.sort()
    # for m in menuTags:
    #     print(str(m) + ":")

    # print(menuTags)

    patternScript = re.compile(r'createMarker\(new google.maps.LatLng\(')

    # lines:
    #    createMarker(new google.maps.LatLng(45.9814523800,14.1723632800), '<div class="mapPopUp">	<div class="title">	<span class="closed">Zaprto</span>				<h2><a href="/bencinski-servisi/podrobno/2424">BS Rovte</a></h2>		<span><div class="field-content">Rovte 20a, 1373 Rovte</div></span>	</div>	<ul class="contact">			<li>T: <strong>+386 1 75 03 051</strong></li>									<!-- <li>E: </li> -->	</ul>	<div class="image imageBaloon">	<a href="/bencinski-servisi/podrobno/2424">		<img src="http://www.petrol.si/sites/www.petrol.si/files/styles/catalog_thumb/public/bs/rovte.jpg?itok=aojx6VEf" width="147" height="110" alt="BS Rovte" title="BS Rovte" />	</a>	</div>		<span class="field-content"><a href="/bencinski-servisi/podrobno/2424" class="more">Več</a></span>	<!-- <a class="more" href="#"><span>►►</span> Več o tem servisu</a> -->	<!-- <a class="more" href="#"><span>►►</span> Pohvali, pograjaj ta servis [že 4 mnenja]</a>--></div>', ' zaprto Osrednja in severna Slovenija * Aktiven Q Max 95 Q Max Diesel Točenje kurilnega olja Plin v jeklenkah Fax WIFI ', 0);
    pattern = re.compile(r'createMarker\(new google.maps.LatLng\(([0-9\.]*),([0-9\.]*)\), \'([^\']*)\', \'([^\']*)\'')

    i = 0
    errors = 0

    script = soup.find("script", text=patternScript)
    if script:
        all_lines = script.text.splitlines()
        marker_lines = list(filter(pattern.search, all_lines))

        # https://wiki.openstreetmap.org/wiki/OSM_Conflator expects array:
        # [
        #   {
        #     "id": 123456,
        #     "lat": 1.2345,
        #     "lon": -2.34567,
        #     "tags": {
        #       "amenity": "fuel",
        #       ...
        #     }
        #   },
        #   ...
        # ]

        nodes = []
        for line in tqdm(marker_lines[:10000], unit="Nodes"):
            m = pattern.search(line)
            if m:
                i = i + 1
                lat = m.group(1)
                lon = m.group(2)
                markerHtml = m.group(3)
                markerTagsStr = m.group(4)
                markerSoup = BeautifulSoup(markerHtml, "html.parser")
                name = "Petrol " + markerSoup.select_one("h2 a").text
                website = base_url + markerSoup.select_one("h2 a")["href"]
                id = website.rpartition("/")[2]
                phone = markerSoup.select_one("ul.contact li strong").text

                # remove spaces in the last part (after area code) of the phone number
                phone = str(phone)
                phonePrefix = " ".join(phone.split(" ", 2)[:2])
                phone = phonePrefix + " " + phone.replace(phonePrefix, "").replace(" ", "")

                # basic object:
                node = { "id": int(float(id)), "lat": float(lat), "lon": float(lon), "tags": { "name": name, "contact:website": website, "brand": "Petrol", "brand:wikidata": "Q174824",  "contact:phone": phone } }

                # tags on marker:
                markerTags = []
                for t in menuTags:
                    if t in markerTagsStr:
                        markerTags.append(t)

                # Remove some time-dependant tags:
                if "Trenutno odprti" in markerTags:
                    markerTags.remove("Trenutno odprti")
                if "* Aktiven" in markerTags:
                    markerTags.remove("* Aktiven")
                if "Array" in markerTags:
                    markerTags.remove("Array")

                markerTags.sort()

                unmatchedTags = markerTags.copy()

                for kt in markerTags:
                    if kt in tag_map_dict:
                        if tag_map_dict[kt]:
                            for key in tag_map_dict[kt]:
                                if key in node["tags"] and not (tag_map_dict[kt][key] in node["tags"][key]):
                                    # append a different value
                                    # print(f"appending {tag_map_dict[kt][key]} to {node['tags'][key]}")
                                    node["tags"][key] = node["tags"][key] + ";" + tag_map_dict[kt][key]
                                else:
                                    # print(f"setting {tag_map_dict[kt][key]} to {node['tags'][key]}")
                                    node["tags"][key] = tag_map_dict[kt][key]
                            unmatchedTags.remove(kt)

                node["tags"]["petrol_si:source_tags"] = ";".join(markerTags)
                if unmatchedTags:
                    node["tags"]["petrol_si:source_tags:unmatched"] = ";".join(unmatchedTags)

                if "amenity" not in node["tags"]:
                    continue
                if not ("fuel" in node["tags"]["amenity"] or "charging_station" in node["tags"]["amenity"]):
                    continue
                if "is_in" not in node["tags"]:
                    continue
                if "SI" not in node["tags"]["is_in"]:
                    continue

                # scrape details page:
                try:
                    detailsPage = requests.get(website)
                except requests.exceptions.RequestException as e:  # This is the correct syntax
                    print(e, file=sys.stderr)
                    errors = errors + 1
                    # exit(1)

                detailsData = detailsPage.text
                detailsSoup = BeautifulSoup(detailsData, "html.parser")
                openingTimeStrings = detailsSoup.select_one(".opening-time").stripped_strings

                openingTime = ""
                for dsc, hrs in zip(openingTimeStrings, openingTimeStrings):
                    # print(dsc, hrs)
                    if dsc in openingTimesMapping:
                        openingTime = openingTime + openingTimesMapping[dsc] + " " + hrs.replace(" ", "").zfill(11) + "; "
                    elif dsc == "odprto" and hrs == "NON-STOP":
                        openingTime = "24/7"
                    else:
                        errors = errors + 1
                        print("Unknown opening time", dsc, hrs, file=sys.stderr)
                        print("Page: ", website, file=sys.stderr)

                openingTime = openingTime.strip("; ")
                # print(openingTime)

                node["tags"]["opening_hours"] = openingTime

                nodes.append(node)
            else:
                errors = errors + 1
                print("ERROR: Line not matched:", file=sys.stderr)
                print(line, file=sys.stderr)

        # sort it reasonable diffs
        nodes = sorted(nodes, key=lambda k: k['id'])

        if outpath:
            with open(outpath, 'w') as outfile:
                json.dump(nodes, outfile, indent=2, sort_keys=True)
            print("Wrote json with {} nodes to: {}".format(len(nodes), outpath), file=sys.stderr)
        else:
            json.dump(nodes, sys.stdout, indent=2, sort_keys=True)
            print()

    else:
        print("ERROR: script not found!", file=sys.stderr)
        errors = errors + 1

    print ("Scraped: {} nodes, {} errors.".format(i, errors), file=sys.stderr)

    # set the errorlevel
    exit(errors)


if __name__ == '__main__':
    print ("Running with Python version: " + sys.version)
    if len(sys.argv) > 1:
        main(outpath=sys.argv[1])
    else:
        main(outpath=None)
