#Alicia Melotik
#amelotik@nd.edu

import argparse
import json
from urllib.request import urlopen
from urllib.error import HTTPError
import statistics
import numpy
import os
import sys
import os.path
import plotdata
import createreport

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
    statDict = {'period': "", 'interface': interface, 'num points': 0, 'min': 0, 'max': 0, 
                'mean': 0, 'median': 0, 'std dev': 0, '10th percentile': 0, '90th percentile': 0}
    if not filteredData:
        return statDict

    dataPts = []
    first = 1
    numPts = 0
    #for each dictionary data pt, track data
    for currDict in filteredData:
        numPts += 1
        dataPts.append(currDict['tput_mbps'])
        #keep track of highest and lowest dates included
        currDate = currDict['timestamp'].split("-")
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
    #add the period based on earliest and latest month/year pair (or if there's only one, use that)
    if (lowYear == highYear and lowMonth == highMonth):
        statDict['period'] = str(lowYear) + "-" + str(lowMonth)
    else:
        statDict['period'] = str(lowYear) + "-" + str(lowMonth) + " to " + str(highYear) + "-" + str(highMonth)
    
    #use libraries to populate statistics dictionary
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

def createDoc(year, month, textFile, JSON_URL, prepend="", all=False):
    #open and load JSON data, unless url cannot be found
    try:
        jsonData = urlopen(JSON_URL)
    except HTTPError:
        print("HTTPError: " + JSON_URL + "could not be found")
        sys.exit(1) 
    #if error occurs with JSON, let user know and exit
    try:
        data = json.loads(jsonData.read())
    except json.JSONDecodeError:
        print("JSONDecodeError: The URL did not fetch any data")
        sys.exit(1)
    #test is textFile for word doc is valid
    if not os.path.isfile(textFile):
        print("Error: " + textFile + " cannot be found")
        sys.exit(1)
    #use a dictionary to find the number of days in specified month
    numDays = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    #make the file names, always with 2 nums for month
    if (month < 10):
        strMonth = "0" + str(month)
    else:
        strMonth = str(month)

    #filter unwanted data and sort by ascending timestamp for each wired and wireless interfaces
    filteredData = filterAndSort(data)
    #if --all arg invoked, subset uses data from all year/months
    if (all):
        wiredSubset = [x for x in filteredData if x['interface'] == "eth0"]
        wifiSubset = [x for x in filteredData if x['interface'] == "wlan0"]
        wiredFileName = prepend + "All-Wired.docx"
        wifiFileName = prepend + "All-WiFi.docx"
    else:
        wiredSubset = filterSubset(filteredData, month, year, "eth0")
        wifiSubset = filterSubset(filteredData, month, year, "wlan0")
        wiredFileName = prepend + str(year) + "-" + strMonth + "-Wired.docx"
        wifiFileName = prepend + str(year) + "-" + strMonth + "-WiFi.docx"

    #check if the files already exist and inform user if so
    if os.path.isfile(wiredFileName):
        print("Warning: " + wiredFileName + " already exists. It will be overwritten if sufficient data for the period is found")
    if os.path.isfile(wifiFileName):
        print("Warning: " + wifiFileName + " already exists. It will be overwritten if sufficient data for the period is found")

    #if the subset is not empty, continue on creating the stats and doc
    if wiredSubset:
        #create png
        wiredPNGName = "wiredAvg.png"
        if (all):
            wiredAvg = plotdata.dailyAverage(wiredSubset, 31)
        else:
            wiredAvg = plotdata.dailyAverage(wiredSubset, numDays[month])
        plotdata.createPlot(wiredAvg, wiredPNGName)
        #make stat dictionary for doc table
        wiredStats = calcStats(wiredSubset, "eth0")
        #put it all together in the word doc
        createreport.combineDocParts(textFile, wiredStats, wiredPNGName, wiredFileName)
        #clean up, delete created png
        os.remove(wiredPNGName)
        return wiredFileName
    else: #if there was no data for the year/month pair
        print(wiredFileName + " was not created because there is no data for the specified period")

    if wifiSubset:
        #create PNG for daily average data
        wifiPNGName = "wifiAvg.png"
        if (all):
            wifiAvg = plotdata.dailyAverage(wifiSubset, 31)
        else:
            wifiAvg = plotdata.dailyAverage(wifiSubset, numDays[month])
        plotdata.createPlot(wifiAvg, wifiPNGName)
        #create stat dictionary for doc table
        wifiStats = calcStats(wifiSubset, "wlan0")
        #call the function to create the document
        createreport.combineDocParts(textFile, wifiStats, wifiPNGName, wifiFileName)
        #delete created pngs
        os.remove(wifiPNGName)
        return wifiFileName
    else:
        print(wifiFileName + " was not created because there is no data for the specified period")
    return None


if __name__ == "__main__":
    #use argpase to get necessary arguments from user
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int, help="the year to filter data to")
    parser.add_argument("month", type=int, help="the month to filter data to")
    parser.add_argument("textFile", help="the text file for the start of the doc")
    parser.add_argument("JSON_URL", help="JSON to be fetched")
    parser.add_argument("--all", help="ignore month/year and enumerate across all times", action="store_true", default=False)
    #get the entered arguments
    args = parser.parse_args()

    createDoc(args.year, args.month, args.textFile, args.JSON_URL, args.all)

