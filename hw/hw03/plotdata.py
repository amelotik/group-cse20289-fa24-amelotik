#Alicia Melotik
#amelotik@nd.edu

import argparse
import json
import matplotlib.pyplot as plt
import numpy as np

def dailyAverage(data, numDays):
    totalsDict = {day: {'totaltput': 0, 'countDays': 0} for day in range(1, numDays+1)}

    for elem in data:
        #split year-month-day from first part of timestamp, then narrow down to just day
        date = elem['timestamp'].split('T')[0].split('-')[2]
        if date.startswith('0'):
            intDate = int(date[1])
        else:
            intDate = int(date)
        totalsDict[intDate]['totaltput'] += elem['tput_mbps']
        totalsDict[intDate]['countDays'] += 1

    avgDict = {day: 0 for day in range(1, numDays+1)}
    for day in avgDict:
        avgDict[day] = totalsDict[day]['totaltput']/totalsDict[day]['countDays']
    return avgDict

def createPlot(dataDict, outputFile):
    dates = list(dataDict.keys())
    averages = list(dataDict.values())
    plt.bar(dates, averages, color='blue', width = 0.4)

    plt.xlabel("Day")
    plt.ylabel("Average Throughput (Mb/s)")
    plt.title("Average Daily Throughput")

    plt.savefig(outputFile)
     

if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    parser.add_argument("JSON", help="JSON file to be read in")
    parser.add_argument("numDays", type=int, help="the number of days in the month")
    parser.add_argument("outputFile", help="the name of the file to output the plot to")
    #use the parser to get the entered arguments
    args = parser.parse_args()

    dataset = json.loads(open(args.JSON).read())
    avg = dailyAverage(dataset, args.numDays)
    print(avg)
    createPlot(avg, args.outputFile)
