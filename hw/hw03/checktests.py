#Alicia Melotik
#amelotik@nd.edu

import argparse
import json
from urllib.request import urlopen

#first filters the data down to downlink and iperf only, then sorts remaining data by timestamp
def filterAndSort(dataset):
    filteredData = list(filter(lambda elem: (elem['direction'] == 'downlink') and (elem['type'] == 'iperf'), dataset))


    return filteredData

parser = argparse.ArgumentParser()
parser.add_argument("JSON_URL", help="JSON to be fetched")

#get the entered arguments and get JSON data
args = parser.parse_args()

jsonURL = urlopen(args.JSON_URL)
data = json.loads(jsonURL.read())

newData = filterAndSort(data)
print(newData)

