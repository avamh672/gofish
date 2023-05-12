import sys
import runGosia
import parseGosiaInputs
import fileManagement
from myconfig import *
import numpy as np
import csv
import os
import multiprocessing.pool
import itertools


def setup(): #Initializes the program by reading in the matrix elements and their properties
  beamMatrixElements = parseGosiaInputs.getMatrixElements(beamINTIinp)
  targetMatrixElements = parseGosiaInputs.getMatrixElements(targetINTIinp)
  return beamMatrixElements,targetMatrixElements

def runMonteCarloSpace(chainNum,chainDir,mainDir,nSamples,beamLoBounds,beamHiBounds,targetLoBounds,targetHiBounds,previouslyInterupted=False):
  #beamSubSpace = np.zeros((len(beamLoBounds)))
  #targetSubSpace = np.zeros((len(targetLoBounds)))
  if previouslyInterupted:
    outputsSubSpace = parseGosiaInputs.read_outputs(chainNum)
    os.chdir(chainDir)
    beamSubSpace = parseGosiaInputs.read_bst(beam_bst)
    targetSubSpace = parseGosiaInputs.read_bst(target_bst)
  else:
    os.chdir(chainDir)
    runGosia.runGosia2(beamINTIinp)
    runGosia.runGosia2(targetINTIinp)
    runGosia.runGosia(beamMAPinp)
    runGosia.runGosia(targetMAPinp)
    runGosia.runGosia2(beamPOINinp)
    beamPOINout = parseGosiaInputs.getOutputFile(beamPOINinp)
    targetPOINout = parseGosiaInputs.getOutputFile(targetPOINinp)
    beam_dof = parseGosiaInputs.findDof(beamPOINinp,beamYields)
    target_dof = parseGosiaInputs.findDof(targetPOINinp,targetYields)
    total_dof = beam_dof + target_dof
    #outputsSubSpace = np.zeros((total_dof+1))
    chisqContributions = parseGosiaInputs.findChisqContributions(beamPOINout)
    chisqContributions += parseGosiaInputs.findChisqContributions(targetPOINout)
    beamChisq = parseGosiaInputs.findChisq(beamPOINout)*beam_dof
    targetChisq = parseGosiaInputs.findChisq(targetPOINout)*target_dof
    totalChisq = beamChisq + targetChisq
    chisqContributions.append(totalChisq)
    outputsSubSpace = chisqContributions
    beamSubSpace = parseGosiaInputs.read_bst(beam_bst)
    targetSubSpace = parseGosiaInputs.read_bst(target_bst)
    beamInputs = open(os.path.join(mainDir,"beamInputs_" + str(chainNum) + ".csv"),'a')
    targetInputs = open(os.path.join(mainDir,"targetInputs_" + str(chainNum) + ".csv"),'a')
    outputs = open(os.path.join(mainDir,"newGosiaOutputs_" + str(chainNum) + ".csv"),'a')
    beamInputs.write(str(beamSubSpace)+"\n")
    targetInputs.write(str(targetSubSpace)+"\n")
    outputs.write(str(chisqContributions)+"\n")
    beamInputs.close()
    targetInputs.close()
    outputs.close()
    nSamples -= 1
  for i in range(0,nSamples):
    testBeamME = []
    testTargetME = []
    for index in range(len(beamLoBounds)):
      if beamHiBounds[index] == beamLoBounds[index]:
        testme = beamSubSpace[index]
      else:
        sigma = (beamHiBounds[index]-beamLoBounds[index])/1000
        testme = np.random.normal(beamSubSpace[index],sigma)
        if testme > beamHiBounds[index]:
          testme = beamHiBounds[index]
        elif testme < beamLoBounds[index]:
          testme = beamLoBounds[index]
      testBeamME.append(testme)
    for index in range(len(targetLoBounds)):
      if targetHiBounds[index] == targetLoBounds[index]:
        testme = targetSubSpace[index]
      else:
        sigma = (targetHiBounds[index]-targetLoBounds[index])/1000
        testme = np.random.normal(targetSubSpace[index],sigma)
        if testme > targetHiBounds[index]:
          testme = targetHiBounds[index]
        elif testme < targetLoBounds[index]:
          testme = targetLoBounds[index]
      testTargetME.append(testme)
    parseGosiaInputs.make_bst(beam_bst,testBeamME)
    parseGosiaInputs.make_bst(target_bst,testTargetME)
    runGosia.runGosia2(beamINTIinp)
    runGosia.runGosia2(targetINTIinp)
    runGosia.runGosia(beamMAPinp)
    runGosia.runGosia(targetMAPinp)
    runGosia.runGosia2(beamPOINinp)
    beamPOINout = parseGosiaInputs.getOutputFile(beamPOINinp)
    targetPOINout = parseGosiaInputs.getOutputFile(targetPOINinp)
    beam_dof = parseGosiaInputs.findDof(beamPOINinp,beamYields)
    target_dof = parseGosiaInputs.findDof(targetPOINinp,targetYields)
    total_dof = beam_dof + target_dof
    chisqContributions = parseGosiaInputs.findChisqContributions(beamPOINout)
    chisqContributions += parseGosiaInputs.findChisqContributions(targetPOINout)
    beamChisq = parseGosiaInputs.findChisq(beamPOINout)*beam_dof
    targetChisq = parseGosiaInputs.findChisq(targetPOINout)*target_dof
    totalChisq = beamChisq + targetChisq
    chisqContributions.append(totalChisq)
    beamInputs = open(os.path.join(mainDir,"beamInputs_" + str(chainNum) + ".csv"),'a')
    targetInputs = open(os.path.join(mainDir,"targetInputs_" + str(chainNum) + ".csv"),'a')
    outputs = open(os.path.join(mainDir,"newGosiaOutputs_" + str(chainNum) + ".csv"),'a')
    if totalChisq <= outputsSubSpace[-1]:
      beamInputs.write(str(testBeamME)+"\n")
      targetInputs.write(str(testTargetME)+"\n")
      outputs.write(str(chisqContributions)+"\n")
      beamSubSpace = testBeamME
      targetSubSpace = testTargetME
      outputsSubSpace = chisqContributions
    else:
      acceptanceRatio = (totalChisq/outputsSubSpace[-1])**((total_dof/2)-1)*np.exp((outputsSubSpace[-1]-totalChisq)/2)
      testAccept = np.random.uniform(0,1)
      if testAccept <= acceptanceRatio:
        beamInputs.write(str(testBeamME)+"\n")
        targetInputs.write(str(testTargetME)+"\n")
        outputs.write(str(chisqContributions)+"\n")
        beamSubSpace = testBeamME
        targetSubSpace = testTargetME
        outputsSubSpace = chisqContributions
      else:
        beamInputs.write(str(beamSubSpace)+"\n")
        targetInputs.write(str(targetSubSpace)+"\n")
        outputs.write(str(outputsSubSpace)+"\n")
        outputsSubSpaces = chisqContributions
    beamInputs.close()
    targetInputs.close()
    outputs.close()
  os.chdir(mainDir)
  return 

def generateMonteCarloSpace(beamMatrixElements,targetMatrixElements,chainNum,nSamples=2,initialGuess = False): #Markov Chain Monte Carlo method to sample the parameter space
  #First we define matrices to store the successive sets of ME's
  
  beam_dof = parseGosiaInputs.findDof(beamPOINinp,beamYields)
  target_dof = parseGosiaInputs.findDof(targetPOINinp,targetYields)
  total_dof = beam_dof + target_dof
  chainDirPrefix = fileManagement.createSubDirectories(chainNum)
  chainDir = chainDirPrefix + str(chainNum)
  mainDir = os.getcwd()
  previouslyInterupted = False
  if os.path.isfile(os.path.join(mainDir,"beamInputs_" + str(chainNum) + ".csv")):
    beamInputs = open(os.path.join(mainDir,"beamInputs_" + str(chainNum) + ".csv"),'r')
    targetInputs = open(os.path.join(mainDir,"targetInputs_" + str(chainNum) + ".csv"),'r')
    lineCount = 0
    for line in beamInputs:
      lineCount += 1
    remainingSamples = nSamples - lineCount
    if remainingSamples == 0:
      exit()
    beamMCSpace = line.strip("[ ]\n").split(',')
    for line in targetInputs:
      pass
    targetMCSpace = line.strip("[ ]\n").split(',')
    previouslyInterupted = True
  else:
    remainingSamples = nSamples
    if initialGuess:
      beam_mes = parseGosiaInputs.read_bst(beam_bst)
      target_mes = parseGosiaInputs.read_bst(target_bst)
      beamMCSpace = beam_mes
      targetMCSpace = target_mes
    else:
      chainDir = chainDirPrefix + str(chainNum)
      beamMCSpace = []
      targetMCSpace = []
      for index, me in beamMatrixElements.iterrows():
        beamMCSpace.append(np.random.uniform(me["LoBound"],me["HiBound"]))
      for index, me in targetMatrixElements.iterrows():
        targetMCSpace.append(np.random.uniform(me["LoBound"],me["HiBound"]))
  os.chdir(chainDir)
  parseGosiaInputs.make_bst(beam_bst,beamMCSpace)
  parseGosiaInputs.make_bst(target_bst,targetMCSpace)
  os.chdir(mainDir)
  beamLoBounds = beamMatrixElements["LoBound"].to_numpy()
  beamHiBounds = beamMatrixElements["HiBound"].to_numpy()
  targetLoBounds = targetMatrixElements["LoBound"].to_numpy()
  targetHiBounds = targetMatrixElements["HiBound"].to_numpy()
  runMonteCarloSpace(chainNum,chainDir,mainDir,remainingSamples,beamLoBounds,beamHiBounds,targetLoBounds,targetHiBounds,previouslyInterupted)
  return










chainNum = int(sys.argv[1])
beamMatrixElements,targetMatrixElements = setup()
generateMonteCarloSpace(beamMatrixElements,targetMatrixElements,chainNum,nSamples=100,initialGuess = True)
