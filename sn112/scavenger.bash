#!/bin/bash
#
#SBATCH --qos=scavenger
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=11
#SBATCH --time=72:00:00
#SBATCH --mem-per-cpu=16G
#SBATCH --array=0-49
#SBATCH --job-name adaptive_particle_swarm
#SBATCH --output=/mnt/scratch/hillma54/logs/adaptiveParticleSwarm_%A_%a.out
#SBATCH --error=/mnt/scratch/hillma54/logs/adaptiveParticleSwarm_%A_%a.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=[hillma54@msu.edu](mailto:hillma54@msu.edu)
date;hostname;pwd

echo "RUNNING INDEX $SLURM_ARRAY_TASK_ID"
python /mnt/home/hillma54/gofish/src/adaptiveParticleSwarm.py "$SLURM_ARRAY_TASK_ID"

date;hostname;pwd
