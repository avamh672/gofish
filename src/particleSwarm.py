import numpy as np
import pyswarms.backend asimport P
import parseGosiaInputs
import runGosia
#from pyswarms.backend.topology import VonNeumann
#from pyswarms.backend.topology import Ring
from pyswarms.backend.topology import Star
from pyswarms.backend.handlers import VelocityHandler
from myconfig import *
import threading
import fileManagement
import os
import sys

#Takes an integer as an argument. Only effects where the name of the output file and the temp 
#directories for running GOSIA by default. Useful for running many instances in parallel.
#Ensure a different batch number is used for each instance when running simultaneously.
batchNumber = int(sys.argv[1])

#Initializes the process of computing the particle chisq values, including dividing up the 
#particles between multiple threads.
def getSwarmChisq(positions,iteration,nThreads=1):
  particlesPerThread = int(np.ceil(len(positions)/nThreads))
  threadFirstLast = []
  folderStart = batchNumber*nThreads
  for j in range(nThreads):
    chainDirPrefix = fileManagement.createSubDirectories(folderStart + j)
    threadFirstLast.append((particlesPerThread*j,min(particlesPerThread*(j+1),len(positions))))
  
  chisqDict = {}
  tmpChisqArray = []
  for j in range(nThreads):
    chainDir = chainDirPrefix + str(folderStart + j)
    tmpChisqArray.append(threading.Thread(target=getParticleChisq, args=[positions,iteration,threadFirstLast[j],chainDir,chisqDict], name='t%i' % j))
    tmpChisqArray[j].start()

  for j in range(nThreads):
    tmpChisqArray[j].join()
  
  chisqArray = []
  for firstLast in threadFirstLast:
    chisqArray += chisqDict[firstLast[0]]
  chisqArray = np.array(chisqArray)
  return chisqArray
  
#Each thread calls this function once. Loops over all particles assigned to that thread and
#computes the chisq values.
def getParticleChisq(positions,iteration,threadFirstLast,chainDir,chisqDict):
  chisqArray = []
  for i in range(threadFirstLast[0],threadFirstLast[1]):
    parseGosiaInputs.make_bst(os.path.join(chainDir,beam_bst),positions[i][:nBeamParams])
    parseGosiaInputs.make_bst(os.path.join(chainDir,target_bst),positions[i][nBeamParams:])
    #if iteration % 20 == 0:
      #runGosia.runGosia2InDir(beamINTIinp,chainDir)
      #runGosia.runGosia2InDir(targetINTIinp,chainDir)
      #runGosia.runGosiaInDir(beamMAPinp,chainDir)
      #runGosia.runGosiaInDir(targetMAPinp,chainDir)
    runGosia.runGosiaInDir(beamPOINinp,chainDir)
    runGosia.runGosiaInDir(targetPOINinp,chainDir)
    beamOutputFile = os.path.join(chainDir,parseGosiaInputs.getOutputFile(beamPOINinp))
    targetOutputFile = os.path.join(chainDir,parseGosiaInputs.getOutputFile(targetPOINinp))
    beamINTIout = os.path.join(chainDir,parseGosiaInputs.getOutputFile(beamINTIinp))
    targetINTIout = os.path.join(chainDir,parseGosiaInputs.getOutputFile(targetINTIinp))
    beamCorrFile = os.path.join(chainDir,parseGosiaInputs.getCorrFile(beamPOINinp))
    targetCorrFile = os.path.join(chainDir,parseGosiaInputs.getCorrFile(targetPOINinp))
    computedObservables = parseGosiaInputs.getPOINobservables(beamExptMap,beamOutputFile,beamINTIout,beamCorrFile)
    computedObservables += parseGosiaInputs.getPOINobservables(targetExptMap,targetOutputFile,targetINTIout,targetCorrFile)
    expt = []
    scalingFactors = []
    for j in range(len(beamExptMap)):
      expt.append(beamExptMap[j][0])
    for j in range(len(targetExptMap)):
      expt.append(targetExptMap[j][0])
    nExpt = max(expt)
    for j in range(nExpt):
      tempSum1 = 0
      tempSum2 = 0
      for k in range(len(expt)):
        if expt[k] == j+1:
          tempSum1 += (observables[k]*computedObservables[k])/uncertainties[k]**2
          tempSum2 += computedObservables[k]**2/uncertainties[k]**2
      scalingFactor = tempSum1/tempSum2
      scalingFactors.append(scalingFactor)
    for j in range(nExpt):
      for k in range(len(expt)):
        if expt[k] == j+1:
          computedObservables[k] *= scalingFactors[j]
    nObservables = len(observables)
    chisq = 0
    for j in range(nObservables):
      chisq += ((computedObservables[j]-observables[j])/uncertainties[j])**2
    chisqArray.append(chisq)
  chisqDict[threadFirstLast[0]] = chisqArray
  return 

#Initializes everything
nThreads = 10 #number of threads used for particles
#nBeamParams = 17 #number of matrix elements for the sn112 beam
nBeamParams = 13 #sn116, sn120
nParticles = 350 #number of particles to be used
#nDimensions = 41 #total number of parameters
#nDimensions = 35 #sn120
nDimensions = 37 #sn116

#Gets the bounds for each matrix element from the INTI files.
beamMatrixElements = parseGosiaInputs.getMatrixElements(beamINTIinp)
targetMatrixElements = parseGosiaInputs.getMatrixElements(targetINTIinp)
beamLoBounds = beamMatrixElements["LoBound"].to_numpy()
beamHiBounds = beamMatrixElements["HiBound"].to_numpy()
targetLoBounds = targetMatrixElements["LoBound"].to_numpy()
targetHiBounds = targetMatrixElements["HiBound"].to_numpy()
loBounds = np.concatenate((beamLoBounds,targetLoBounds))
hiBounds = np.concatenate((beamHiBounds,targetHiBounds))
paramBounds = (loBounds,hiBounds)

#Run GOSIA to initialize everything. This is the only time INTI will be run, so use a
#reasonable initial guess. If you don't have one, you can always run with a bad one and 
#use this program to try to get a better initial guess. 
#runGosia.runGosia2(beamINTIinp)
#runGosia.runGosia2(targetINTIinp)
#runGosia.runGosia(beamMAPinp)
#runGosia.runGosia(targetMAPinp)
beamCorr = parseGosiaInputs.getCorrFile(beamINTIinp)
targetCorr = parseGosiaInputs.getCorrFile(targetINTIinp)

#Get experimental observables and the beam and target maps
observables,uncertainties,beamExptMap,targetExptMap = parseGosiaInputs.getExperimentalObservables(beamCorr,targetCorr,beamINTIinp,targetINTIinp,beamPOINinp,targetPOINinp)

#Initialize the particle swarm
#Papers I read suggested that VonNeumann is typically the best topology. With this many 
#dimensions, Star is equivalent to VonNeumann. Recommend running an ensemble of swarms 
#with Star topology and taking the best result.
my_topology = Star() 
#Next line only needed if running Ring topology
#my_vh = VelocityHandler(strategy='invert') 
#c1 is the cognitive parameter (velocity component towards particle's own best position)
#c2 is the social parameter (velocity component towards best position of particle it can see)
#c2 pulls towards global minimum in star topology since the graph is fully connected
#w is the inertial parameter (velocity component in direction of last iteration's velocity)
my_options = {'c1' : 1.6, 'c2' : 1.3, 'w' : 0.4}
my_swarm = P.create_swarm(n_particles=nParticles,dimensions=nDimensions,bounds=paramBounds,options=my_options)


iterations = 500
for i in range(iterations):
  #Get the chisq for each particle position
  my_swarm.current_cost = getSwarmChisq(my_swarm.position,i,nThreads)
  #initial best cost and best position for each particle 
  if i == 0:
    my_swarm.pbest_cost = my_swarm.current_cost
    my_swarm.pbest_pos = my_swarm.position
  #If it's not the first iteration, check if this position is better than particle's best
  #and update if it is.
  else:
    for j in range(len(my_swarm.current_cost)):
      if my_swarm.current_cost[j] <= my_swarm.pbest_cost[j]:
        my_swarm.pbest_pos[j] = my_swarm.position[j]
        my_swarm.pbest_cost[j] = my_swarm.current_cost[j]
  
  #Track the global best cost
  if np.min(my_swarm.pbest_cost) < my_swarm.best_cost:
    #my_swarm.best_pos, my_swarm.best_cost = my_topology.compute_gbest(my_swarm,normBatchArray[batchNumber],neighborsBatchArray[batchNumber])
    my_swarm.best_pos, my_swarm.best_cost = my_topology.compute_gbest(my_swarm)
    best_iter = i

  #If we haven't gotten better in 50 iterations, we probably are stuck in a local minimum
  if i > best_iter + 50:
    break

  print('Iteration: {} | my_swarm.best_cost: {:.4f}'.format(i+1, my_swarm.best_cost))

  
  #Update velocities and positions for the next iteration
  #my_swarm.velocity = my_topology.compute_velocity(my_swarm,clamp=None,vh=my_vh,bounds=(loBounds,hiBounds))
  #my_swarm.position = my_topology.compute_position(my_swarm,bounds=paramBounds)
  my_swarm.velocity = my_topology.compute_velocity(my_swarm)
  my_swarm.position = my_topology.compute_position(my_swarm)

f = open('particleSwarmResult_%i.csv' % batchNumber,'w')
f.write('The best cost found by our swarm is: {:.4f}\n'.format(my_swarm.best_cost))
f.write('The best position found by our swarm is: {}\n'.format(my_swarm.best_pos))
f.write('The number of iterations needed was: {}'.format(i))
f.close()