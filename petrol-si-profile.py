# Available modules: codecs, logging, requests, json, etree. But importing these helps catch other errors
import json
import logging


# What will be put into "source" tags. Lower case please
source = 'petrol.si'
# A fairly unique id of the dataset to query OSM, used for "ref:mos_parking" tags
# If you omit it, set explicitly "no_dataset_id = True"
dataset_id = 'petrol_si'
# Tags for querying with overpass api
query = [('amenity', '~fuel|charging_station')]
# Use bbox from dataset points (default). False = query whole world, [minlat, minlon, maxlat, maxlon] to override
bbox = True
# How close OSM point should be to register a match, in meters. Default is 100
max_distance = 100
# Delete objects that match query tags but not dataset? False is the default
delete_unmatched = False
# If set, and delete_unmatched is False, modify tags on unmatched objects instead
# Always used for area features, since these are not deleted
tag_unmatched = {
    'fixme': 'Проверить на местности: в данных ДИТ отсутствует. Вероятно, демонтирован',
    'amenity': None,
    'was:amenity': 'vending_machine'
}
# Actually, after the initial upload we should not touch any existing non-matched objects
tag_unmatched = None
# A set of authoritative tags to replace on matched objects
master_tags = ('ref', 'opening_hours', 'contact:phone', 'contact:website', 'operator')


