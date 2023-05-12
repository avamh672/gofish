import runGosia
import parseGosiaInputs
from myconfig import *
import numpy as np
import csv


def setup(): #Initializes the program by reading in the matrix elements and their properties
  beamMatrixElements = parseGosiaInputs.getMatrixElements(beamINTIinp)
  targetMatrixElements = parseGosiaInputs.getMatrixElements(targetINTIinp)
  return beamMatrixElements,targetMatrixElements

def generateMonteCarloSpace(beamMatrixElements,targetMatrixElements,nChains=1,nSamples=1,initialGuess = False): #Markov Chain Monte Carlo method to sample the parameter space
  #First we define matrices to store the successive sets of ME's
  beamMCSpace = np.zeros((len(beamMatrixElements.index),nSamples))
  targetMCSpace = np.zeros((len(targetMatrixElements.index),nSamples))
  MC_chisq = []
  if initialGuess:
    beam_mes = parseGosiaInputs.read_bst(beam_bst)
    target_mes = parseGosiaInputs.read_bst(target_bst)
    beamMCSpace[:,0] = beam_mes
    targetMCSpace[:,0] = target_mes
  else:
    for index, me in beamMatrixElements.iterrows():
      beamMCSpace[index,0] = np.random.uniform(me["LoBound"],me["HiBound"])
    for index, me in targetMatrixElements.iterrows():
      targetMCSpace[index,0] = np.random.uniform(me["LoBound"],me["HiBound"])
    parseGosiaInputs.make_bst(beam_bst,beamMCSpace[:,0])
    parseGosiaInputs.make_bst(target_bst,targetMCSpace[:,0])
  #runGosia.runGosia2(beamINTIinp)
  #runGosia.runGosia2(targetINTIinp)
  #runGosia.runGosia(beamMAPinp)
  #runGosia.runGosia(targetMAPinp)
  #runGosia.runGosia2(beamMINIinp)
  beamMINIout = parseGosiaInputs.getOutputFile(beamMINIinp)
  targetMINIout = parseGosiaInputs.getOutputFile(targetMINIinp)
  beam_dof = parseGosiaInputs.findDof(beamMINIinp)
  target_dof = parseGosiaInputs.findDof(targetMINIinp)
  total_dof = beam_dof + target_dof
  beamChisq = parseGosiaInputs.findChisq(beamMINIout)*beam_dof
  targetChisq = parseGosiaInputs.findChisq(targetMINIout)*target_dof
  MC_chisq.append(beamChisq + targetChisq)
  for i in range(1,nSamples):
    testBeamME = []
    testTargetME = []
    for index, me in beamMatrixElements.iterrows():
      sigma = (me["HiBound"] - me["LoBound"])/1000
      testme = np.random.normal(beamMCSpace[index,i-1],sigma)
      if testme > me["HiBound"]:
        testme = me["HiBound"]
      elif testme < me["LoBound"]:
        testme = me["LoBound"]
      testBeamME.append(testme)
    for index, me in targetMatrixElements.iterrows():
      sigma = (me["HiBound"] - me["LoBound"])/1000
      testme = np.random.normal(targetMCSpace[index,i-1],sigma)
      if testme > me["HiBound"]:
        testme = me["HiBound"]
      elif testme < me["LoBound"]:
        testme = me["LoBound"]
      testTargetME.append(testme)
    parseGosiaInputs.make_bst(beam_bst,testBeamME)
    parseGosiaInputs.make_bst(target_bst,testTargetME)
    runGosia.runGosia2(beamINTIinp)
    runGosia.runGosia2(targetINTIinp)
    runGosia.runGosia(beamMAPinp)
    runGosia.runGosia(targetMAPinp)
    runGosia.runGosia2(beamMINIinp)
    beamChisq = parseGosiaInputs.findChisq(beamMINIout)*beam_dof
    targetChisq = parseGosiaInputs.findChisq(targetMINIout)*target_dof
    totalChisq = beamChisq + targetChisq
    if totalChisq <= MC_chisq[-1]:
      beamMCSpace[:,i] = testBeamME
      targetMCSpace[:,i] = testTargetME
      MC_chisq.append(totalChisq)
    else:
      acceptanceRatio = (totalChisq/MC_chisq[-1])**((total_dof/2)-1)*np.exp((MC_chisq[-1]-totalChisq)/2)
      testAccept = np.random.uniform(0,1)
      if testAccept <= acceptanceRatio:
        beamMCSpace[:,i] = testBeamME
        targetMCSpace[:,i] = testTargetME
        MC_chisq.append(totalChisq)
      else:
        beamMCSpace[:,i] = beamMCSpace[:,i-1]
        targetMCSpace[:,i] = targetMCSpace[:,i-1]
        MC_chisq.append(MC_chisq[-1])
  with open("beamMCSpace.csv",'w',newline="") as f:
    writer = csv.writer(f)
    writer.writerows(beamMCSpace)
  with open("targetMCSpace.csv",'w',newline="") as f:
    writer = csv.writer(f)
    writer.writerows(targetMCSpace)
  




  return beamMCSpace, targetMCSpace
  











beamMatrixElements,targetMatrixElements = setup()
beamMCSpace,targetMCSpace = generateMonteCarloSpace(beamMatrixElements,targetMatrixElements,nChains=1,nSamples=3,initialGuess = True)
