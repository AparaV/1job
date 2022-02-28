# 1job

The one job to schedule all jobs.

## Typical use case
You want to run simulations using several sets of parameters. And you want each set of parameters to have its own dedicated memory, but you don't want to manually create all of those `.sbatch` scripts.

Enter `1job`.
1. Create a template for your `.sbatch` where each of the parameters you want to change have a unique name. This unique name should be enclosed with `$$` on either side. This name should be in all capital letters. Underscores `_` are allowed _between_ these letters.
2. Create a `.csv` file. The first row should contain these unique parameter names. Every subsequent row will contain the parameters used for each simulation.
3. Schedule `1job.sbatch` on the cluster. This will create an `.sbatch` for each set of parameters and schedule them.
4. Profit.
