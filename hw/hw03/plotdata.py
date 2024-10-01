#Alicia Melotik
#amelotik@nd.edu

import argparse
import json
import os.path
import sys
import matplotlib.pyplot as plt
import numpy as np

#find the average tput for each day based on the passed data
def dailyAverage(data, numDays):
    totalsDict = {day: {'totaltput': 0, 'countDays': 0} for day in range(1, numDays+1)}

    for elem in data:
        #split year-month-day from first part of timestamp, then narrow down to just day
        date = elem['timestamp'].split('T')[0].split('-')[2]
        if date.startswith('0'):
            intDate = int(date[1])
        else:
            intDate = int(date)
        #accumulate the total throughput for each date
        totalsDict[intDate]['totaltput'] += elem['tput_mbps']
        totalsDict[intDate]['countDays'] += 1

    #create the dictionary with each days avg
    avgDict = {day: 0 for day in range(1, numDays+1)}
    for day in avgDict:
        #if there were no days of that date, leave avg=0
        if totalsDict[day]['countDays'] > 0:
            #otherwise calc avg with total/count
            avgDict[day] = totalsDict[day]['totaltput']/totalsDict[day]['countDays']
    return avgDict

#make bar graph for data (daily averages) and save to passed outputFile
def createPlot(dataDict, outputFile):
    dates = list(dataDict.keys())
    averages = list(dataDict.values())

    fig, ax = plt.subplots()
    ax.grid()
    ax.bar(dates, averages, color='blue', width = 0.4)
    #make labels for graph
    plt.xlabel("Day")
    plt.ylabel("Average Throughput (Mb/s)")
    plt.title("Average Daily Throughput")

    plt.savefig(outputFile)

     
#test cases to run for only this file
if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument("JSON", help="JSON file to be read in")
    parser.add_argument("numDays", type=int, help="the number of days in the month")
    parser.add_argument("outputFile", help="the name of the file to output the plot to")
    #use the parser to get the entered arguments
    args = parser.parse_args()
    #check for invalid arguments
    if not os.path.isfile(args.JSON):
        print("Error: " + args.JSON + " could not be found")
        sys.exit(1)
    if os.path.isfile(args.outputFile):
        print("Warning: " + args.outputFile + " already exists. It will be overwritten.")
        sys.exit(1)
    #read the data and call the functions to create the plot
    try:
        dataset = json.loads(open(args.JSON).read())
    except json.JSONDecodeError:
        print("JSONDecodeError: The JSON did not have any data")
    avg = dailyAverage(dataset, args.numDays)
    createPlot(avg, args.outputFile)
