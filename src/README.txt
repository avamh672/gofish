GosiaParticleSwarm is an external minimizer for GOSIA2 that relies on Particle Swarm 
Optimization, or PSO. PSO is a metaheuristic optimization scheme, meaning that it optimizes 
without regard to the gradient of the function being minimized. This can be advantageous for 
GOSIA2 minimization, where there are many parameters that are all correlated with each other. 
It tends to be more robust with regard to local minima than gradient-based optimization in 
such cases. However, PSO is a random algorithm, and is not guaranteed to ever converge to the 
global minimum, though through extensive testing I have found that it generally does for this 
problem. Still, I recommend that you run multiple instances (I typically run 20) of this 
program and take the overall best result. Further, with metaheuristics it is advisable to 
perform "polishing" on the result, meaning in this case using the GOSIA2 gradient-based
optimization to fine-tune the PSO solution. 

PSO works by initializing a number of "particles" randomly in the parameter space, and giving
them random initial velocities in this space based on the bounds. Reasonable bounds for all
matrix elements are important to achieving a good PSO result, otherwise it may return an
unphysical solution. GOSIA's OP,POIN is evaluated for the matrix elements of each particle,
and a chi-squared value is computed. The particles velocities are then updated based on three 
components: the inertial component, the cognitive component, and the social component. The 
inertial component is a velocity component along the direction of the particle's previous 
velocity. The cognitive component is a component in the direction of the best position that 
the particle has previously visited. The social component is the most complex. All particles
are connected to some other particles by a mathematically graph, also called the topology of
the swarm. The social component is in the direction of the best position that any particle
that shares a graph connection with the particle in question has found. For this program,
I performed a hyperparameter search to optimize the coefficients for these components, as
well as the topology. The coefficients can also be specified by the user, if you prefer. The
topology used in this program is adaptive; it starts with a limited number of connections
for each particle and slowly expands as the number of iterations increases until every
particle is connected to every other particle. GosiaParticleSwarm performs 500 iterations
of this process and then terminates and writes to an output file the best position it found
and the chi-squared value associated with that position. 

Before running GosiaParticleSwarm, you must first run the OP,INTI and OP,MAP input files for
both the beam and target if you are performing simultaneous minimization. If you are 
performing beam-only minimization, you must instead run the OP,INTI, OP,MAP, and OP,POIN input
files for the beam. The additional requirement of OP,POIN for the beam-only minimization is
to get the DSIG parameter GOSIA uses to get the scaling of the experimental yields. It is
recommended that you use the GOSIA version included in this github repository, which prints
the yields at a higher precision than standard GOSIA. If you are performing beam-only
minimization, than you must use this GOSIA version, since it has an additional print
statement that writes the DSIG parameter for each GOSIA experiment to the OP,POIN output. This
is needed for the common normalization.

GosiaParticleSwarm takes two inputs from the command line, both required. The first is a 
config file which defines important parameters. The second argument is the batch number, 
which should be an integer and is used for ensuring that multiple simultaneous instances of 
the program don't write to the same files. Thus the batch number should be different for each
instance. A sample config file is included in the github repository. The required arguments
are:

gosia - The path to the GOSIA installation you want the program to use. A slightly modified
version of GOSIA, which prints certain outputs with higher precision, is included in this
github repository. It is recommended that you use this installation. 

beamINTIinp - The OP,INTI input file for the beam nucleus.

beamMAPinp - The OP,MAP input file for the beam nucleus.

beamPOINinp - The OP,POIN input file for the beam nucleus. 

beam_bst - The .bst file (file12 in GOSIA) that contains the matrix elements for the beam. 
    The matrix elements in the file aren't actually used, it just needs to know the name of 
    the file.

rawBeamYields - The .yld file (file3 in GOSIA) that contains the beam yields. 

beamYields - A modified version of the yields file requried for this program. It must include
    every transition that will have yields output by OP,POIN, in the order in which they will
    be output. Transitions that are not observed should have their yield and uncertainty 
    listed as 0. 

nBeamParams - Number of matrix elements for the beam nucleus. 

targetINTIinp, targetMAPinp, targetPOINinp, target_bst, rawTargetYields, targetYields, 
    nTargetParams - Same as above, but for the target.

simulMin - Must be True or False. Specifies whether simultaneous minimization of the beam and 
    target is to be performed. If set to False, target inputs do not need to be provided.

scratchDirectory - The directory where the program will create temporary subdirectories to
    run GOSIA in. It does this so that it can run multiple instances of GOSIA simultaneously 
    to parallelize the process of computing the chi-squared for each particle.

nThreads - Integer. Specifies the number of threads the program will use. I typically run with
    20, and the program takes several hours to run in that case. This program can be 
    parallelized up to the number of particles, which by default is 600. I recommend using a 
    number of threads that divides evenly into the number of particles, otherwise some threads 
    will have a lot of downtime as they wait for others to finish. 

There are also some optional inputs for the hyperparameters. I performed a hyperparameter
search to tune the default values, but they can be user specified. The optional parameters 
are:

nParticles - Integer. Number of particles to be used in the optimization. Defaults to 600.

nIterations - Integer. Number of iterations of PSO to run. Defaults to 500.

inertialCoeff - Float. Sets the value of the inertial coefficient. Defaults to 0.7.

cognitiveCoeff - Float. Sets the value fo the cognitive coefficient. Defaults to 1.75.

socialCoeff - Float. Sets the value of the social coefficient. Defaults to 1.0.

velocityStrategy - String. Sets the strategy for the velocity handler. For more information,
    see the documentation for the pyswarms python package. Defaults to 'invert'.

boundaryStrategy - String. Sets the strategy for what to do if particles try to leave the 
    parameter bounds. For more information, see the documentation for the pyswarms python
    package. Defaults to 'reflect'. 

----------------------------------------------------------------------------------------------

In addition to the config file, this program reads some important information from the GOSIA
input files you pass it. The parameter bounds will be taken from the bounds set in the ME
section in the beamPOINinp and targetPOINinp files. Additionally, constraints on branching
ratios, lifetimes, mixing ratios, and matrix elements, and the upper bound for unobserved
transitions, are read from the OP,YIEL section of the same fle. These lines must be commented
as follows:

NS1,NS2 - comment this line with !NS
UPL - comment this line with !UPL
NBRA - comment this line with !BR
NL - comment this line with !LT
NDL - comment this line with !DL
NAMX - comment this line with !ME

Additionally, if simulMin is set to False, each YNRM line must be commented with !SCL1, !SCL2,
etc. where the number corresponds to the associated experiment.

----------------------------------------------------------------------------------------------

GosiaParticleSwarm uses the gosiaManager class, defined in gosiaManager.py, to handle input
and output from GOSIA. I wrote this as a class so that it can be used with other programs
that need to interface with GOSIA. gosiaManager takes the same config file as 
gosiaParticleSwarm when it is initalized, so this would likely need to be changed if running
it with another program, but otherwise I tried to write the functions in a general way. The
functions are as follows:

setup() - Calls the getMatrixElements function for both beam and target from the POIN input 
    files and returns the pandas dataframes.

getOutputFile(input_file) - Gets the GOSIA output file for a given input file. It assumes that
    the output file is file22 in the input file.

getCorrFile(input_file) - Gets the corrected yields file, file4, from the input file.

getMapFile(input_file) - Gets the map file, file7, from the input file.

getMatrixElements(input_file) - Reads the input file and returns a pandas dataframe with the
    multipolarity, initial and final state, and lower and upper bound for each matrix element.

make_bst(bst_file,matrixElements) - Makes file12 using the given matrix elements and stores it
    as the bst_file.

read_bst(bst_file) - Reads a file12 and returns the matrix elements.

getExperimentalObservables - Reads the experimental observables. First it opens the
    uncorrected yields file and creates a "map" of the yield observables, containing the 
    experiment number and the initial and final state. It also stores the yield and 
    uncertainty, but only as placeholders. Then it opens the corrected yields file and reads 
    the yields and uncertainties, assigning them in the observable list based on the map. 
    Yields that do not appear in the corrected yields file (for unobserved transitions) will
    keep the 0 values for yield and uncertainty from the uncorrected file. It then reads the
    OP,POIN input file and reads the branching ratio, lifetime, mixing ratio, and matrix
    element constraints from there. For each of these constraints, the map file entry is 0,0,0
    to indicate that it is a constraint and not a yield. The function does this process first
    for the beam and then for the target, and then returns the beam and target maps
    (separately), and the observables and uncertainties as a single list. 

getPOINobservables(output_file) - Reads from a POIN output file the calculated observables.
    It reads them in order, which is why the special yields file for gosiaParticleSwarm is 
    required to have the transitions in the same order as the POIN output. 

getUpperLimits(beamExptMap,targetExptMap,observables) - Sets the upper limits for unobserved
    transitions by reading from the POIN input file. Requires the normalizing transition to
    be flagged with !NS and the upper limit ratio to be flagged with !UPL. Note that these
    flags should only be applied once, as this function does not support different upper limit
    ratios for different experiments. The normalizing transition must be observed in each
    experiment, otherwise the length of the upper limits will not match the number of 
    experiments. 

createSubDirectories(chainNum) - Creates a subdirectory in the scratch directory defined by
    the user in the config file, and then copies all of the files necessary to run GOSIA into
    that subdirectory. The created directory will have the name chainSubdir_"chainNum", where
    chainNum is the variable passed to the function. This is to ensure that multiple instances
    of gosiaParticleSwarm running in parallel can create different subdirectories and not
    overwrite each other. 

removeSubDirectories(chainNum) - Removes the subdirectory created by the previous function.

runGosia(input_file) - Runs GOSIA in the current working directory with the provided input
    file.

runGosia2(input_file) - Runs GOSIA2 in the current working directory with the provided input
    file.

runGosiaInDir(input_file,dir) - Runs GOSIA in directory dir with the provided input file.

runGosia2InDir(input_file,dir) - Runs GOSIA2 in directory dir with the provided input file.

getScalingFactors() - Gets the common normalization factors from beamPOINinp. Requires the
    YNRM lines to be flagged with !SCL1, !SCL2, etc. for experiments 1, 2, etc. 

getDsig() - Gets the DSIG value from the POIN output. OP,POIN to be run with the version of 
    GOSIA in this github repository.