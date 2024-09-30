#Alicia Melotik
#amelotik@nd.edu

import argparse
import json
from urllib.request import urlopen
import statistics
import numpy

#first filters the data down to downlink and iperf only, then sorts remaining data by timestamp
def filterAndSort(dataset):
    filteredData = list(filter(lambda elem: (elem['direction'] == 'downlink') and (elem['type'] == 'iperf'), dataset))
    filteredData.sort(key=lambda elem: elem['timestamp'])

    return filteredData

#filter data to a subset from specified year/month/interface
#default month = 5, year = 2024, interface = eth0
def filterSubset(dataset, month, year, interface):
    filteredData = []
    for currDict in dataset:
        if currDict['interface'] == interface:
            date = currDict['timestamp'].split("-")
            if (year == int(date[0])) and (month == int(date[1])):
                filteredData.append(currDict)
    return filteredData

#calculate statistics for requested interface in dataset
def calcStats(dataset, interface):
    filteredData = [data for data in dataset if data['interface'] == interface]
    statDict = {'period': 0, 'interface': interface, 'num points': 0, 'min': 0, 'max': 0, 
                'mean': 0, 'median': 0, 'std dev': 0, '10th percentile': 0, '90th percentile': 0}
    if not filteredData:
        return statDict

    dataPts = []
    first = 1
    numPts = 0
    for currDict in filteredData:
        numPts += 1
        currDate = currDict['timestamp'].split("-")
        dataPts.append(currDict['tput_mbps'])
        if (first == 1):
            lowYear = currDate[0]
            highYear = currDate[0]
            lowMonth = currDate[1]
            highMonth = currDate[1]
            first = 0
        else:
            if (currDate[0] <= lowYear) and (currDate[1] < lowMonth):
                lowYear = currDate[0]
                lowMonth = currDate[1]
            elif (currDate[0] >= highYear) and (currDate[1] > highMonth):
                highYear = currDate[0]
                highMonth = currDate[1]
    print(str(lowYear) + "-" + str(lowMonth) + " to " + str(highYear) + "-" + str(highMonth))
    
    
    statDict['num points'] = numPts
    statDict['min'] = min(dataPts)
    statDict['max'] = max(dataPts)
    statDict['mean'] = statistics.mean(dataPts)
    statDict['median'] = statistics.median(dataPts)
    if numPts > 1:
        statDict['std dev'] = statistics.stdev(dataPts)

    statDict['10th percentile'] = numpy.percentile(dataPts, 10)
    statDict['90th percentile'] = numpy.percentile(dataPts, 90)
    return statDict

#output dictionary info to string
def dictToString(dictionary):
    string = ""
    for key, value in dictionary.items():
        if key == 'interface':
            if value == 'eth0':
                string = string + "interface: wired\n"
            else:
                string = string + "interface: wireless\n"
        elif key == 'period':
            string = string + "period: all\n"
        else:
            string = string + str(key) + ": " + str(value) + "\n"
    return string


parser = argparse.ArgumentParser()
parser.add_argument("JSON_URL", help="JSON to be fetched")
#get the entered arguments and get JSON data
args = parser.parse_args()

jsonURL = urlopen(args.JSON_URL)
data = json.loads(jsonURL.read())

newData = filterAndSort(data)
#for item in newData:
   # for key, value in item.items():  
 #       print(str(key) + ": " + str(value))
  #  print()

subset = filterSubset(newData, 5, 2024, "eth0")
stats = calcStats(newData, "eth0")
result = dictToString(stats)
print(result)
#print("SUBSET:")
#for item in subset:
 #   for key, value in item.items():  
  #      print(str(key) + ": " + str(value))
   # print()

