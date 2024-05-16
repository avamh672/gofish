import sys
import pandas as pd
import numpy as np
import os
import shutil
import subprocess

class gosiaManager:


  #Initialize gosiaManager by reading in the user-specified parameters from the config file.
  def __init__(self,config):
    if os.path.isfile(config):
      f = open(config,'r')
      self.configDict = {}
      integerArguments = ["nThreads","nBeamParams","nTargetParams","annealingLayers"]
      booleanArguments = ["simulMin","parallelAnnealing"]
      line = f.readline()
      while line:
        splitline = line.split('=')
        if splitline[0].strip() in integerArguments:
          self.configDict[splitline[0].strip()] = int(splitline[1].strip())
        elif splitline[0].strip() in booleanArguments:
          if splitline[1].strip() == "True":
            self.configDict[splitline[0].strip()] = True
          elif splitline[1].strip() == "False":
            self.configDict[splitline[0].strip()] = False
          else:
            raise Exception("ERROR: %s must be True or False!" % splitline[0].strip())
        else:
          self.configDict[splitline[0].strip()] = splitline[1].strip()
        line = f.readline()
      f.close()
    else:
      raise Exception("ERROR: Config file is not readable!")
    
    #expectedFromConfig = ["gosia","beamINTIinp","beamMAPinp","beamPOINinp","beam_bst","beamYields","rawBeamYields","scratchDirectory","simulMin","nThreads","nBeamParams"]
    expectedFromConfig = ["gosia","beamINTIinp","beamPOINinp","beamYields","scratchDirectory","simulMin","nThreads","nBeamParams"]
    if "simulMin" in self.configDict.keys():
      if self.configDict["simulMin"] == True:
        #expectedFromConfig += ["targetINTIinp","targetMAPinp","targetPOINinp","target_bst","targetYields","rawTargetYields","nTargetParams"]
        expectedFromConfig += ["targetINTIinp","targetPOINinp","targetYields","nTargetParams"]
    else:
      raise Exception("ERROR: Variable simulMin not in config file! Please set to true for simultaneous beam/target minimization and false otherwise.")
    for key in expectedFromConfig:
      if key not in self.configDict.keys():
        raise Exception("ERROR: Variable %s not in config file!" % key)

    f = open(self.configDict["beamINTIinp"],'r')
    line = f.readline()
    while line[:2] != "4,":
      line = f.readline()
      if "OP,TITL" in line:
        raise Exception("ERROR: Corrected yields file not located in GOSIA input file %s" % self.configDict["beamINTIinp"])
    self.configDict["beamCorr"] = f.readline()[:-1]
    f.close()

    f = open(self.configDict["beamPOINinp"],'r')
    line = f.readline()
    while "OP,TITL" not in line:
      if line[:3] == "22,":
        self.configDict["beamPOINout"] = f.readline()[:-1]
      elif line[:2] == "7,":
        self.configDict["beamMAPinp"] = f.readline()[:-1]
      elif line[:2] == "3,":
        self.configDict["rawBeamYields"] = f.readline()[:-1]
      elif line[:3] == "12,":
        self.configDict["beam_bst"] = f.readline()[:-1]
      line = f.readline()
    f.close()
    for key in ["beamPOINout","beamMAPinp","rawBeamYields","beam_bst"]:
      if key not in self.configDict.keys():
        raise Exception("ERROR: File %s not located in GOSIA input file %s" % (key,self.configDict["beamPOINinp"]))

    if self.configDict["simulMin"] == True:
      f = open(self.configDict["targetINTIinp"],'r')
      line = f.readline()
      while line[:2] != "4,":
        line = f.readline()
        if "OP,TITL" in line:
          raise Exception("ERROR: Corrected yields file not located in GOSIA input file %s" % self.configDict["beamINTIinp"])
      self.configDict["targetCorr"] = f.readline()[:-1]
      f.close()

      f = open(self.configDict["targetPOINinp"],'r')
      line = f.readline()
      while "OP,TITL" not in line:
        if line[:3] == "22,":
          self.configDict["targetPOINout"] = f.readline()[:-1]
        elif line[:2] == "7,":
          self.configDict["targetMAPinp"] = f.readline()[:-1]
        elif line[:2] == "3,":
          self.configDict["rawTargetYields"] = f.readline()[:-1]
        elif line[:3] == "12,":
          self.configDict["target_bst"] = f.readline()[:-1]
        line = f.readline()
      f.close()
      for key in ["targetPOINout","targetMAPinp","rawTargetYields","target_bst"]:
        if key not in self.configDict.keys():
          raise Exception("ERROR: File %s not located in GOSIA input file %s" % (key,self.configDict["beamPOINinp"]))


    return

  
  #Initializes the program by reading in the matrix elements and their properties
  #def setup(self): 
    #beamMatrixElements = getMatrixElements(self.configDict["beamPOINinp"])
    #targetMatrixElements = getMatrixElements(self.configDict["targetPOINinp"])
    #return beamMatrixElements,targetMatrixElements

  """
  #Gets the output file from a given input file
  def getOutputFile(self,input_file):
    f = open(input_file,'r')
    line = f.readline()
    while line[:3] != "22,":
      line = f.readline()
      if "OP,TITL" in line:
        raise Exception("ERROR: Output file not located in GOSIA input file %s" % input_file)
    output_file = f.readline()[:-1]
    f.close()
    return output_file

  #Gets the corrected yields file from a given input file
  def getCorrFile(self,input_file):
    f = open(input_file,'r')
    line = f.readline()
    while line[:2] != "4,":
      line = f.readline()
      if "OP,TITL" in line:
        raise Exception("ERROR: Corr file not located in GOSIA input file %s" % input_file)
    output_file = f.readline()[:-1]
    f.close()
    return output_file

  #Gets the file produced by OP,MAP
  def getMapFile(self,input_file):
    f = open(input_file,'r')
    line = f.readline()
    while line[:2] != "7,":
      line = f.readline()
      if "OP,TITL" in line:
        raise Exception("ERROR: Map file not located in GOSIA input file %s" % input_file)
    output_file = f.readline()[:-1]
    f.close()
    return output_file

  #Gets the "raw" beam yields file (the version with the normal GOSIA format)
  def getRawBeamYields(self,input_file):
    f = open(input_file,'r')
    line = f.readline()
    while line[:2] != "3,":
      line = f.readline()
      if "OP,TITL" in line:
        raise Exception("ERROR: Yields file not located in GOSIA input file %s" % input_file)
    output_file = f.readline()[:-1]
    f.close()
    return output_file

  #Gets the file containing the current matrix elements
  def getBstFile(self,input_file):
    f = open(input_file,'r')
    line = f.readline()
    while line[:3] != "12,":
      line = f.readline()
      if "OP,TITL" in line:
        raise Exception("ERROR: Best fit matrix elements file not located in GOSIA input file %s" % input_file)
    output_file = f.readline()[:-1]
    f.close()
    return output_file
  """
  
  #Reads in the matrix elements, multipolarities, and bounds from the GOSIA input file
  def getMatrixElements(self,input_file):
    f = open(input_file)
    line = f.readline()
    while line != "ME\n":
      line = f.readline()
    line = f.readline()
    if "0,0,0,0\n" in line:
      mult = line.split(',')[0]
    else:
      print("Error: ME in gosia input file is not properly formatted!")
      return None
    line = f.readline()
    Multipolarity = []
    StateI = []
    StateF = []
    LoBound = []
    HiBound = []
    while line != "EXPT\n":
      if "0,0,0,0\n" in line:
        mult = int(line.split(',')[0])
      else:
        splitline = line.split(',')
        Multipolarity.append(mult)
        StateI.append(int(splitline[0]))
        StateF.append(int(splitline[1]))
        LoBound.append(float(splitline[3]))
        HiBound.append(float(splitline[4]))
      line = f.readline()
    beamMatrixElements = pd.DataFrame({"Multipolarity" : Multipolarity, "StateI" : StateI, "StateF" : StateF, "LoBound" : LoBound, "HiBound" : HiBound})
    return beamMatrixElements

  """
  #Finds the number of degrees of freedom from a given input and yields file (to get total dof, run this twice, once for the beam and once for the target)    
  def findDof(self,input_file,yields_file):
    dofcount = 0
    f = open(input_file,'r')    
    line = f.readline()
    while "!BR" not in line:
      line = f.readline()
    brcount = int(line.split(",")[0])
    dofcount += brcount
    while "!LT" not in line:
      line = f.readline()
    ltcount = int(line.split(",")[0])
    dofcount += ltcount
    while "!DL" not in line:
      line = f.readline()
    dlcount = int(line.split(",")[0])
    dofcount += dlcount
    while "!ME" not in line:
      line = f.readline()
    mecount = int(line.split(",")[0])
    dofcount += mecount
    f.close()

    f = open(yields_file,'r')
    line = f.readline()
    while line:
      splitline = line.split(",")
      if len(splitline) == 4 and splitline[2] != 0:
        dofcount += 1
      line = f.readline()
    f.close()
    return dofcount

  #Reads the chisq value from the output file
  def findChisq(self,output_file):
    f = open(output_file,'r')
    line = f.readline()
    while "*** CHISQ=" not in line:
      line = f.readline()
    chisq = float(line.strip().split("***")[1].split("=")[1])
    f.close()
    return chisq
  """

  #Makes a new .bst file using the matrix elements passed to it
  def make_bst(self,bst_file,matrixElements):
    f = open(bst_file,'w')
    for me in matrixElements:
      f.write(str(me) + "\n")
    f.close()
    return

  #Reads the .bst file and gets the matrix elements
  def read_bst(self,bst_file):
    mes = []
    f = open(bst_file,'r')
    line = f.readline()
    while line:
      mes.append(float(line.strip()))
      line = f.readline()
    f.close()
    return mes
  
  """
  def findChisqContributions(self,output_file):
    f = open(output_file,'r')
    line = f.readline()
    inResults = False
    inyields = False
    inMixing = False
    inLifetimes = False
    inBranching = False
    inLitME = False
    sigmas = []
    while line:
      if "CALCULATED AND EXPERIMENTAL YIELDS" in line and "EXPERIMENT  1" in line:
        inResults = True
      if inResults:
        if inyields:
          splitline = line.split()
          if(len(splitline) >= 9) and "UPL" not in line:
            sigmas.append(float(splitline[8]))
        elif inMixing:
          splitline = line.split()
          if(len(splitline) >= 5):
            sigmas.append(float(splitline[4]))
        elif inLifetimes:
          splitline = line.split()
          if(len(splitline) >= 5) and splitline[0] in "0123456789":
            calc = float(splitline[1])
            exp = float(splitline[2])
            if calc >= exp:
              unc = float(splitline[4])
            else:
              unc = abs(float(splitline[3]))
            sigma = abs(calc-exp)/unc
            sigmas.append(sigma)
        elif inBranching:
          splitline = line.split()
          if len(splitline) >= 9:
            sigmas.append(float(splitline[8]))
        elif inLitME:
          splitline = line.split()
          if(len(splitline) >= 5) and splitline[0] in "0123456789":
            sigmas.append(float(splitline[4]))
        if "(YE-YC)/SIGMA" in line:
          inyields = True
        elif "CHISQ" in line:
          inyields = False
        elif "EXP. AND CALCULATED BRANCHING RATIOS" in line:
          inyields = False
          inMixing = False
          inLifetimes = False
          inBranching = True
          inLitME = False
        elif "E2/M1 MIXING" in line:
          inyields = False
          inMixing = True
          inLifetimes = False
          inBranching = False
          inLitME = False
        elif "CALCULATED LIFETIMES" in line:
          inyields = False
          inMixing = False
          inLifetimes = True
          inBranching = False
          inLitME = False
        elif "CALCULATED AND EXPERIMENTAL MATRIX ELEMENTS" in line:
          inyields = False
          inMixing = False
          inLifetimes = False
          inBranching = False
          inLitME = True
        elif "MULTIPOLARITY=" in line:
          inyields = False
          inMixing = False
          inLifetimes = False
          inBranching = False
          inLitME = False
      line = f.readline()
    f.close()
    return sigmas
  """

  #Gets the relevant observables from the experiment (corrected yields and comparisons to literature)
  #Requires corrected yields and POIN input for both beam and target
  #ExptMaps store the experiment number and initial and final states for each observables as a tuple.
  #Observables that are literature constraints and not yeilds have map values of (0,0,0). This is
  #so the code knows to bypass them when applying scaling factors.
  def getExperimentalObservables(self):
  
    observables = []
    uncertainties = []
    beamExptMap = []
    targetExptMap = []
    beamDoubletMap = {}
    targetDoubletMap = {}

    expt = 0
    #parse the corrected yields file and store them, along with the exptMap
    f = open(self.configDict["beamYields"],'r')
    line = f.readline()
    while line: 
      splitline = line.split(",")
      if len(splitline) == 7:
        expt = int(splitline[0])
      elif len(splitline) == 4:
        init = int(splitline[0])
        final = int(splitline[1])
        beamExptMap.append((expt,init,final))
        """
        if init >= 10000:
          secondTransitionInit = ((init % 10000) - (init % 100))/100
          secondTransitionFinal = ((final % 10000) - (final % 100))/100
          thirdTransitionInit = init % 100
          thirdTransitionFinal = final % 100
          beamTripletMap[(secondTransitionInit,secondTransitionFinal)] = (init,final)
          beamTripletMap[(thirdTransitionInit,thirdTransitionFinal)] = (init,final)
        """
        if init >= 100:
          secondTransitionInit = init % 100
          secondTransitionFinal = final % 100
          beamDoubletMap[(secondTransitionInit,secondTransitionFinal)] = (init,final)
        observables.append(float(splitline[2]))
        uncertainties.append(float(splitline[3]))
      line = f.readline()
    f.close()

    beamCorr = self.configDict["beamCorr"]

    f = open(beamCorr,'r')
    line = f.readline()
    while line:
      splitline = line.split()
      if len(splitline) == 7:
        expt = int(splitline[0])
      elif len(splitline) == 4:
        if (expt,int(splitline[0]),int(splitline[1])) in beamExptMap:
          observables[beamExptMap.index((expt,int(splitline[0]),int(splitline[1])))] = float(splitline[2])
          uncertainties[beamExptMap.index((expt,int(splitline[0]),int(splitline[1])))] = float(splitline[3])
        elif (expt,int(splitline[1]),int(splitline[0])) in beamExptMap:
          observables[beamExptMap.index((expt,int(splitline[1]),int(splitline[0])))] = float(splitline[2])
          uncertainties[beamExptMap.index((expt,int(splitline[1]),int(splitline[0])))] = float(splitline[3])
      line = f.readline()
    f.close()

    #Read the literature constraints from the POIN file. Note that there are comments that must be included in the POIN file for this to work properly.
    lifetimes = []
    lifetime_uncs = []
    f = open(self.configDict["beamPOINinp"],'r')
    line = f.readline()
    while line:
      if "!BR" in line: #Put !BR as a comment on the line where the number of branching ratio constraints is defined
        nObs = int(line.split(',')[0])
        for i in range(nObs):
          line = f.readline()
          splitline = line.split(',')
          beamExptMap.append((0,0,0))
          observables.append(float(splitline[4]))
          uncertainties.append(float(splitline[5]))
      if "!LT" in line: #Same as BR, but comment !LT for the lifetimes
        nObs = int(line.split(',')[0])
        for i in range(nObs):
          line = f.readline()
          splitline = line.split(',')
          beamExptMap.append((0,0,0))
          lifetimes.append(float(splitline[1]))
          lifetime_uncs.append(float(splitline[2]))
      if "!DL" in line: #Comment !DL for the mixing ratios
        nObs = int(line.split(',')[0])
        for i in range(nObs):
          line = f.readline()
          splitline = line.split(',')
          beamExptMap.append((0,0,0))
          observables.append(float(splitline[2]))
          uncertainties.append(float(splitline[3]))
        observables += lifetimes
        uncertainties += lifetime_uncs
      if "!ME" in line: #Comment !ME for the matrix element constraints
        nObs = int(line.split(',')[0])
        for i in range(nObs):
          line = f.readline()
          splitline = line.split(',')
          beamExptMap.append((0,0,0))
          observables.append(float(splitline[3]))
          uncertainties.append(float(splitline[4]))
      line = f.readline()
    f.close()
    
    #Do the same thing but for the target if simulMin is true
    if self.configDict["simulMin"] == True:
      f = open(self.configDict["targetYields"],'r')
      line = f.readline()
      while line:
        splitline = line.split(",")
        if len(splitline) == 7:
          expt = int(splitline[0])
        elif len(splitline) == 4:
          init = int(splitline[0])
          final = int(splitline[1])
          targetExptMap.append((expt,int(splitline[0]),int(splitline[1])))
          """
          if init >= 10000:
            secondTransitionInit = ((init % 10000) - (init % 100))/100
            secondTransitionFinal = ((final % 10000) - (final % 100))/100
            thirdTransitionInit = init % 100
            thirdTransitionFinal = final % 100
            targetTripletMap[(secondTransitionInit,secondTransitionFinal)] = (init,final)
            targetTripletMap[(thirdTransitionInit,thirdTransitionFinal)] = (init,final)
          """
          if init >= 100:
            secondTransitionInit = init % 100
            secondTransitionFinal = final % 100
            targetDoubletMap[(secondTransitionInit,secondTransitionFinal)] = (init,final)
          observables.append(float(splitline[2]))
          uncertainties.append(float(splitline[3]))
        line = f.readline()
      f.close()

      targetCorr = self.configDict["targetCorr"]

      f = open(targetCorr,'r')
      line = f.readline()
      while line:
        splitline = line.split()
        if len(splitline) == 7:
          expt = int(splitline[0])
        elif len(splitline) == 4:
          if (expt,int(splitline[0]),int(splitline[1])) in targetExptMap:
            observables[len(beamExptMap) + targetExptMap.index((expt,int(splitline[0]),int(splitline[1])))] = float(splitline[2])
            uncertainties[len(beamExptMap) + targetExptMap.index((expt,int(splitline[0]),int(splitline[1])))] = float(splitline[3])
          elif (expt,int(splitline[1]),int(splitline[0])) in targetExptMap:
            observables[len(beamExptMap) + targetExptMap.index((expt,int(splitline[1]),int(splitline[0])))] = float(splitline[2])
            uncertainties[len(beamExptMap) + targetExptMap.index((expt,int(splitline[1]),int(splitline[0])))] = float(splitline[3])
        line = f.readline()
      f.close()

      lifetimes = []
      lifetime_uncs = []
      f = open(self.configDict["targetPOINinp"],'r')
      line = f.readline()
      while line:
        if "!BR" in line:
          nObs = int(line.split(',')[0])
          for i in range(nObs):
            line = f.readline()
            splitline = line.split(',')
            targetExptMap.append((0,0,0))
            observables.append(float(splitline[4]))
            uncertainties.append(float(splitline[5]))
        if "!LT" in line:
          nObs = int(line.split(',')[0])
          for i in range(nObs):
            line = f.readline()
            splitline = line.split(',')
            targetExptMap.append((0,0,0))
            lifetimes.append(float(splitline[1]))
            lifetime_uncs.append(float(splitline[2]))
        if "!DL" in line:
          nObs = int(line.split(',')[0])
          for i in range(nObs):
            line = f.readline()
            splitline = line.split(',')
            targetExptMap.append((0,0,0))
            observables.append(float(splitline[2]))
            uncertainties.append(float(splitline[3]))
          observables += lifetimes
          uncertainties += lifetime_uncs
        if "!ME" in line:
          nObs = int(line.split(',')[0])
          for i in range(nObs):
            line = f.readline()
            splitline = line.split(',')
            targetExptMap.append((0,0,0))
            observables.append(float(splitline[3]))
            uncertainties.append(float(splitline[4]))
        line = f.readline()
      f.close()

    return observables,uncertainties,beamExptMap,targetExptMap,beamDoubletMap,targetDoubletMap
    
  #Does the same thing as getExperimentalObservables, but for the results simulated in OP,POIN
  def getPOINobservables(self,output_file,exptMap,doubletMap):
    computedObservables = []
    
    f = open(output_file,'r')
    line = f.readline()
    while line:
      if "CALCULATED YIELDS" in line:
        line = f.readline()
        line = f.readline()
        expt = int(line.split("EXPERIMENT")[1].split("DETECTOR")[0])
      elif "NORMALIZED YIELD" in line:
        line = f.readline()
        line = f.readline()
        while line != "\n":
          splitline = line.split()
          init = int(splitline[0])
          final = int(splitline[1])

          #Check if this transition is the second listed transition in a doublet pair.
          #If it is, we will add its counts to its pair's instead of treating it as a separate observable.
          if (init,final) in doubletMap.keys() or (final,init) in doubletMap.keys():
            #The value associated with the index tuple key is the tuple that appears in exptMap for the combined doublet.
            #We will get the index of this tuple in the exptMap and then add the counts for this observable to that one.
            try:
              doubletPair = doubletMap[(init,final)]
            except:
              doubletPair = doubletMap[(final,init)]
            if (expt,doubletPair[0],doubletPair[1]) in exptMap:
              exptIndex = exptMap.index((expt,doubletPair[0],doubletPair[1]))
            elif (expt,doubletPair[1],doubletPair[0]) in exptMap:
              exptIndex = exptMap.index((expt,doubletPair[1],doubletPair[0]))
            else:
              raise Exception("Error in function getPOINobservables: the transition from %i to %i is not in the experiment map." % (init,final))
            #GOSIA removes the E from scientific notation if the exponent is 3 digits. Added this try-except block to account for that.
            try:
              computedObservables[exptIndex] += float(splitline[4])
            except:
              splitagain = splitline[4].split('+')
              withE = splitagain[0] + "E+" + splitagain[1]
              computedObservables[exptIndex] += float(withE)
          #If the transition is not the second listed transition in a doublet, we just append the observable to the list.
          else:
            try:
              computedObservables.append(float(splitline[4]))
            except:
              splitagain = splitline[4].split('+')
              withE = splitagain[0] + "E+" + splitagain[1]
              computedObservables.append(float(withE))
          line = f.readline()
      if "EXP. AND CALCULATED BRANCHING RATIOS" in line:
        for i in range(5):
          line = f.readline()
        while line != "\n" and "END" not in line:
          splitline = line.split()
          if "***" in splitline[7]:
            computedObservables.append(10000)
          else:
            computedObservables.append(float(splitline[7]))
          line = f.readline()
      elif "E2/M1 MIXING RATIOS" in line and "EXPERIMENTAL" not in line and "WEIGHT" not in line:
        for i in range(3):
          line = f.readline()
        while line != "\n" and "END" not in line:
          splitline = line.split()
          if "***" in splitline[3]:
            computedObservables.append(10000)
          else:
            computedObservables.append(float(splitline[3]))
          line = f.readline()
      elif "CALCULATED LIFETIMES" in line:
        for i in range(4):
          line = f.readline()
        while line != "\n" and "END" not in line:
          splitline = line.split()
          if(len(splitline)==5):
            computedObservables.append(float(splitline[1]))
          line = f.readline()
      elif "CALCULATED AND EXPERIMENTAL MATRIX ELEMENTS" in line:
        for i in range(4):
          line = f.readline()
        while line != "\n" and "END" not in line:
          splitline = line.split()
          computedObservables.append(float(splitline[3]))
          line = f.readline()
      line = f.readline()
    return computedObservables

  """
  #Gets the cor.f correction factors from the intiInp file
  def getCorr(self,output_file):
    corrections = []
    f = open(output_file,'r')
    line = f.readline()
    while line:
      if "COR.F" in line:
        line = f.readline()
        line = f.readline()
        while line != "\n" and "END OF EXECUTION" not in line:
          point = float(line.split()[2])
          inti = float(line.split()[3])
          corrections.append(inti/point)
          line = f.readline()
      line = f.readline()
    return corrections
  """

  #Reads the upper limits for transitions from the GOSIA input file. Requires NS and UPL flags to be set in the input file.
  def getUpperLimits(self,beamExptMap,targetExptMap,observables):
    beamUpperLimits = []
    
    f = open(self.configDict["beamPOINinp"],'r')
    line = f.readline()
    while line:
      if '!NS' in line:
        splitline = line.strip().split("!")[0].split(",")
        ynrm = (int(splitline[0]),int(splitline[1]))
      elif '!UPL' in line:
        splitline = line.strip().split("!")
        upl = float(splitline[0])
      line = f.readline()
    f.close()
    expt = 1
    for j in range(len(beamExptMap)):
      if beamExptMap[j] == (expt,ynrm[0],ynrm[1]) or beamExptMap[j] == (expt,ynrm[0],ynrm[1]):
        beamUpperLimits.append(observables[j]*upl)
        expt += 1
    
    if self.configDict["simulMin"] == True:
      targetUpperLimits = []

      f = open(self.configDict["targetPOINinp"],'r')
      line = f.readline()
      while line:
        if '!NS' in line:
          splitline = line.strip().split("!")[0].split(",")
          ynrm = (int(splitline[0]),int(splitline[1]))
        elif '!UPL' in line:
          splitline = line.strip().split("!")
          upl = float(splitline[0])
        line = f.readline()
      f.close()
      expt = 1
      for j in range(len(targetExptMap)):
        if targetExptMap[j] == (expt,ynrm[0],ynrm[1]) or targetExptMap[j] == (expt,ynrm[0],ynrm[1]):
          targetUpperLimits.append(observables[j + len(beamExptMap)]*upl)
          expt += 1
      
      upperLimits = []
      for j in range(len(beamUpperLimits)):
        upperLimits.append((beamUpperLimits[j],targetUpperLimits[j]))
    
    else:
      upperLimits = beamUpperLimits
    return upperLimits

  def createSubDirectories(self,chainNum):
    chainDirPrefix = os.path.join(self.configDict["scratchDirectory"],"chainSubdir_")
    chainDir = chainDirPrefix + str(chainNum)
    fullPathToChainDir = os.path.join(os.getcwd(),chainDir)
    if not os.path.exists(fullPathToChainDir):
      os.mkdir(chainDir)
    shutil.copy("sega.raw",chainDir)
    shutil.copy("sega.gdt",chainDir)
    shutil.copy(self.configDict["beamINTIinp"],chainDir)
    shutil.copy(self.configDict["beamMAPinp"],chainDir)
    shutil.copy(self.configDict["beamPOINinp"],chainDir)
    shutil.copy(self.configDict["rawBeamYields"],chainDir)
    shutil.copy(self.configDict["beam_bst"],chainDir)
    shutil.copy(self.configDict["beamCorr"],chainDir)
    if self.configDict["simulMin"] == True:
      shutil.copy(self.configDict["targetINTIinp"],chainDir)
      shutil.copy(self.configDict["targetMAPinp"],chainDir)
      shutil.copy(self.configDict["targetPOINinp"],chainDir)
      shutil.copy(self.configDict["rawTargetYields"],chainDir)
      shutil.copy(self.configDict["target_bst"],chainDir)
      shutil.copy(self.configDict["targetCorr"],chainDir)
    return chainDirPrefix

  def removeSubDirectories(self,chainNum):
    chainDirPrefix = os.path.join(self.configDict["scratchDirectory"],"chainSubdir_")
    chainDir = chainDirPrefix + str(chainNum)
    fullPathToChainDir = os.path.join(os.getcwd(),chainDir)
    shutil.rmtree(fullPathToChainDir) 
    return

  def runGosia(self,input_file):
    with open(input_file) as f:
        subprocess.run([self.configDict["gosia"]], stdin=f, stdout=subprocess.DEVNULL)
    return 
    
  """
  def runGosia2(self,input_file):
    with open(input_file) as f:
        subprocess.run([self.configDict["gosia2"]], stdin=f, stdout=subprocess.DEVNULL)
    return 
  """

  def runGosiaInDir(self,input_file,dir):
    with open(input_file) as f:
        subprocess.run([self.configDict["gosia"]], stdin=f, stdout=subprocess.DEVNULL, cwd=dir)
    return 

  """
  def runGosia2InDir(self,input_file,dir):
    with open(input_file) as f:
        subprocess.run([self.configDict["gosia2"]], stdin=f, stdout=subprocess.DEVNULL, cwd=dir)
    return 
  """  

  def getScalingFactors(self):
    f = open(self.configDict["beamPOINinp"])
    exptScaledTo = []
    exptScalingFactors = []
    line = f.readline()
    while "EXPT" not in line:
      line = f.readline()
    f.readline()
    line = f.readline()
    while "CONT" not in line:
      exptScaledTo.append(int(line.split(',')[10]))
      line = f.readline()
    #for j in range(len(exptScaledTo)):
      #if exptScaledTo[j] == j+1:
        #exptScaledTo[j] = 0
    while line:
      if "!SCL" in line:
        exptScalingFactors.append(float(line.split("!")[0].strip()))
      line = f.readline()
    return exptScaledTo, exptScalingFactors

  """
  def getRawYields(self):
    rawYields = []
    rawUncertainties = []
    expt = 0
    #parse the corrected yields file and store them, along with the exptMap
    f = open(self.configDict["beamYields"],'r')
    line = f.readline()
    while line: 
      splitline = line.split(",")
      if len(splitline) == 7:
        expt = int(splitline[0])
      elif len(splitline) == 4:
        rawYields.append(float(splitline[2]))
        rawUncertainties.append(float(splitline[3]))
      line = f.readline()
    f.close()

    return rawYields, rawUncertainties
  """
  """
  def getIntegratedRutherford(self):
    intiOut = self.getOutputFile(self.configDict["beamINTIinp"])
    f = open(intiOut,'r')
    integratedRutherford = []
    line = f.readline()
    while line:
      if "INTEGRATED RUTHERFORD" in line:
        integratedRutherford.append(float(line.split("=")[1].split()[0]))
      line = f.readline()

    return integratedRutherford
  """

  def getAverageAngle(self):
    f = open(self.configDict["beamPOINinp"],'r')
    averageAngle = []
    line = f.readline()
    while line:
      if "EXPT" in line:
        line = f.readline()
        nExpt = int(line.split(',')[0])
        for i in range(nExpt):
          line = f.readline()
          averageAngle.append(abs(float(line.split(',')[3])))
      line = f.readline()

    return averageAngle

  def getDsig(self,output_file):
    f = open(output_file)
    dsig = []
    line = f.readline()
    while line:
      if "DSIG VALUE" in line:
        dsig.append(float(line.split("=")[1].split()[0]))
      line = f.readline()

    return dsig