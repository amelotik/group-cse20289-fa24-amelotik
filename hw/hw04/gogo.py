#Alicia Melotik
#amelotik@nd.edu

import yaml
import argparse
import sys
from spire.doc import *
from spire.doc.common import *
import checktests
import concurrent.futures

def parseYAML(yamlName):
    try:
        with open(yamlName, 'r') as f:
            data = yaml.safe_load(f)
    except:
        print("Error: " + yamlName + " could not be loaded")
        return None

    tasks = data.get('tasks')
    numTasks = 0
    
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
        numTasks += 1
        print("Task " + list(currTask.keys())[0] + " Done!")
    
    print("Completed " + str(numTasks) + " task(s)!")
    return tasks

def wordToPDF(wordDoc, pdfFile):
    document = Document()
    document.LoadFromFile(wordDoc)
    document.SaveToFile(pdfFile, FileFormat.PDF)
    document.Close()
    
def fullProcess(taskDict):
    docName = checktests.createDoc(taskDict['Year'], taskDict['Month'], taskDict['StartText'], taskDict['URL'], taskDict['Prepend'])
    if docName == None:
        print("Error: No doc was created")
    else:
        pdfName = docName.split(".docx")[0] + ".pdf"
        wordToPDF(docName, pdfName)
    

parser = argparse.ArgumentParser()
parser.add_argument("yamlName", help="the yaml file to parse")
parser.add_argument("--multi", type=int, choices=range(1,5), help="number of processors: from 1 to 4")
args = parser.parse_args()

tasksDict = parseYAML(args.yamlName)
if tasksDict != None:
    #fullProcess(list(infoDict[0].values())[0])
    if args.multi:
        with concurrent.futures.ProcessPoolExecutor(args.multi) as executor:
        results = executor.map(fullProcess, tasksDict)

