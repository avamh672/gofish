import os
import shutil
from myconfig import *

def createSubDirectories(chainNum):
  chainDirPrefix = os.path.join("/mnt/scratch/hillma54","chainSubdir_")
  chainDir = chainDirPrefix + str(chainNum)
  fullPathToChainDir = os.path.join(os.getcwd(),chainDir)
  #if os.path.exists(fullPathToChainDir):
    #shutil.rmtree(chainDir)
  if not os.path.exists(fullPathToChainDir):
    os.mkdir(chainDir)
  shutil.copy("sega.raw",chainDir)
  shutil.copy("sega.gdt",chainDir)
  shutil.copy(beamINTIinp,chainDir)
  shutil.copy(beamMAPinp,chainDir)
  shutil.copy(beamMINIinp,chainDir)
  shutil.copy(targetINTIinp,chainDir)
  shutil.copy(targetMAPinp,chainDir)
  shutil.copy(targetMINIinp,chainDir)
  shutil.copy(rawBeamYields,chainDir)
  shutil.copy(rawTargetYields,chainDir)
  shutil.copy(beam_bst,chainDir)
  shutil.copy(target_bst,chainDir)
  return chainDirPrefix
