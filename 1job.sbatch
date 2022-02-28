#!/bin/bash
#SBATCH --job-name 1job 
#SBATCH --partition short                  # Slurm partition to use
#SBATCH --ntasks 1                       # Number of tasks to run. By default, one CPU core will be allocated per task
#SBATCH --time 0-01:00                       # Wall time limit in D-HH:MM
#SBATCH --mem-per-cpu=1024              # Memory limit for each tasks (in MB)
#SBATCH -o ~/slurm_logs/%x_%j.out      # File to which STDOUT will be written
#SBATCH -e ~/slurm_logs/%x_%j.err      # File to which STDERR will be written
#SBATCH --mail-type=ALL                            # Type of email notification- NONE,BEGIN,END,FAIL,ALL
#SBATCH --mail-user=hpotter@hogwarts.edu                  # Email to which notifications will be sent

module load R/4.1.0-foss-2021a

cd ~/Code

Rscript sims.R --n $$SIZE$$ --p $$PROB$$ --latent $$L$$ --edges $$EDGES$$ --start $$SEED_START$$ --end $$SEED_END$$
