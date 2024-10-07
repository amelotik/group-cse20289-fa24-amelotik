#Alicia Melotik
#amelotik@nd.edu

import yaml
import argparse
import sys
from spire.doc import *
from spire.doc.common import *
import checktests
import concurrent.futures
import os.path

def parseYAML(yamlName):
    #open the passed YAML and read its lines into a dictionary
    try:
        with open(yamlName, 'r') as f:
            data = yaml.safe_load(f)
        #consolidate data to list of dicts because wanted data is all under 'tasks'
        tasks = data.get('tasks')
    except Exception as e:
        print("Error: " + yamlName + " could not be loaded")
        return None

    numTasks = 0
    
    #search each task's corresponding value dictionary to make sure needed parameters are present
    for currTask in tasks:
        for currDict in currTask.values():
            if not ('URL' in currDict and 'Year' in currDict and 'Month' in currDict and 'StartText' in currDict and 'Prepend' in currDict):
                print("missing parameters for task")
                return None
            if not currDict['Month'] == int(currDict['Month']):
                print("the month(s) must be integers")
                return None
            if not currDict['Year'] == int(currDict['Year']):
                print("the year(s) must be integers")
                return None
        #keep track of and print searched tasks
        numTasks += 1
        print("Task " + list(currTask.keys())[0] + " Done!")
    
    print("Completed " + str(numTasks) + " task(s)!")
    return tasks

#instantiate word doc and then convert/format into a PDF
def wordToPDF(wordDoc, pdfFile):
    document = Document()
    document.LoadFromFile(wordDoc)
    document.SaveToFile(pdfFile, FileFormat.PDF)
    document.Close()
    
def fullProcess(taskDict):
    try:
        #separate the task name (key) from its dict (value)
        taskName = list(taskDict.keys())[0]
        taskDict = list(taskDict.values())[0]
        #create word doc of all data using checktests function
        docNames = checktests.createDoc(taskDict['Year'], taskDict['Month'], taskDict['StartText'], taskDict['URL'], taskDict['Prepend'], taskName=taskName)
        if docNames[0] == None:
            print("Error: " + docNames[0] + " was not created")
        else:
            #if document creation was successful for wired data, convert it into a pdf too
            pdfName1 = docNames[0].split(".docx")[0] + ".pdf"
            if os.path.isfile(pdfName1):
                print("Warning: " + pdfName1 + " already exists. It will be overwritten if sufficient data for the period is found")
            wordToPDF(docNames[0], pdfName1)
        if docNames[1] == None:
            print("Error: " + docNames[1] + " was not created")
        else:
            #if document creation was successful for wifi data, convert it into a pdf too
            pdfName2 = docNames[1].split(".docx")[0] + ".pdf"
            if os.path.isfile(pdfName2):
                print("Warning: " + pdfName2 + " already exists. It will be overwritten if sufficient data for the period is found")
            wordToPDF(docNames[1], pdfName2)
    except Exception as e:
        print("Error processing task: " + str(e))
    
#use argparse library to get arguments
parser = argparse.ArgumentParser()
parser.add_argument("yamlName", help="the yaml file to parse")
parser.add_argument("--multi", type=int, choices=range(1,5), help="number of processors: from 1 to 4")
args = parser.parse_args()

tasksDict = parseYAML(args.yamlName)

#if data was successfully processed from YAML,
if tasksDict != None:
    if args.multi:
        #if multi invoked, use process pool with specified num of cores to run multiple processes
        with concurrent.futures.ProcessPoolExecutor(args.multi) as executor:
            for result in executor.map(fullProcess, tasksDict):
                pass
    else:
        #if not multi, iterate through tasks and run process on each
        for task in tasksDict:
            fullProcess(task)
else:
    print("Error: The YAML was not parsed successfully")
                
