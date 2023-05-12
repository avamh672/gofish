import sys
import subprocess
import parseGosiaInputs
from myconfig import *

def runGosia(input_file):
  outputFile = parseGosiaInputs.getOutputFile(input_file)
  with open(input_file) as f:
    subprocess.run([gosia], stdin=f, stdout=subprocess.DEVNULL)
  return outputFile
  
def runGosia2(input_file):
  outputFile = parseGosiaInputs.getOutputFile(input_file)
  with open(input_file) as f:
    subprocess.run([gosia2], stdin=f, stdout=subprocess.DEVNULL)
  return outputFile

def runGosiaInDir(input_file,dir):
  outputFile = parseGosiaInputs.getOutputFile(input_file)
  with open(input_file) as f:
    subprocess.run([gosia], stdin=f, stdout=subprocess.DEVNULL, cwd=dir)
  return outputFile

def runGosia2InDir(input_file,dir):
  outputFile = parseGosiaInputs.getOutputFile(input_file)
  with open(input_file) as f:
    subprocess.run([gosia2], stdin=f, stdout=subprocess.DEVNULL, cwd=dir)
  return outputFile
