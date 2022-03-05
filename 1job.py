"""
1job to schedule them all.
This tool copies template sbatch script with parameters provided by a CSV file
Then it schedules all of the jobs
"""

import os
import re
import argparse
import subprocess
import pandas as pd

from copy import deepcopy as copy

params_pattern = r"\$\$[A-Z]+(_[A-Z]+)*\$\$"
params_re = re.compile(params_pattern)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=str, required=True,
        help="Template .sbatch script")
    parser.add_argument("--params", type=str, required=True,
        help="CSV file containing different parameter combinations")
    parser.add_argument("--output_dir", type=str, required=True,
        help="Directory where temporary .sbatch scripts are stored")
    args = parser.parse_args()
    return args


def check_for_params(line):
    """ Check for parameters in line """
    params = {}
    for match in params_re.finditer(line):
        param = match.group()[2:-2]
        params[param] = {
            "start": match.start(),
            "end": match.end()
        }
    return params


def read_template(fname):
    """
    Read a template script and return its contents and parameters.
    Raises error if parameters are incorrectly encoded.
    """

    template = []
    parameter_set = set()
    with open(fname, "r") as f:
        for idx, line in enumerate(f):
            params_i = check_for_params(line)
            new_params = set(params_i.keys())
            common_params = new_params.intersection(parameter_set)
            if len(common_params) > 0:
                error_msg = f"Parameters {common_params} are defined twice!"
                raise ValueError(error_msg)

            indices = [0]
            for param, param_data in params_i.items():
                indices += [param_data["start"], param_data["end"]]
            line_split = [line[i:j] for i, j in zip(indices, indices[1:]+[None])]

            template.append(line_split)
            parameter_set = parameter_set.union(params_i.keys())

    return template, parameter_set

  
def read_params(fname):
    """ Read all parameters """
    df = pd.read_csv(fname)
    return df


def verify_parameters(params_df, parameter_set):
    df_columns = set(params_df.columns)
    return parameter_set == df_columns


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def find_num_temp_jobs(directory, format="temp_", ext="sbatch"):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    counter = 0
    for file in files:
        if file[:len(format)] == format and file[-len(ext):] == ext:
            file_num = int(file[len(format):-(1 + len(ext))])
            counter = max(file_num, counter)
    return counter


def get_sbatch_file_contents(template, parameter_dict, parameter_set):
    sbatch_lines = []
    for split_line in template:
        for idx, part in enumerate(split_line):
            if len(part) <= 4:
                continue
            param_name = part[2:-2]
            if param_name in parameter_set:
                split_line[idx] = str(parameter_dict[param_name])
        sbatch_lines.append("".join(split_line))
    return sbatch_lines


def write_file(lines, fname):
    with open(fname, "w") as f:
        for line in lines:
            f.write(line)


def create_sbatch_scripts(template, parameter_set, params_df, outdir):

    create_directory(outdir)

    start_counter = find_num_temp_jobs(outdir) + 1
    counter = start_counter

    params_dict_list = params_df.to_dict("records")
    for params_dict in params_dict_list:
        sbatch_lines = get_sbatch_file_contents(copy(template), params_dict, parameter_set)

        fname = "temp_" + str(counter).zfill(5) + ".sbatch"
        fname = os.path.join(outdir, fname)
        write_file(sbatch_lines, fname)

        counter += 1
    end_counter = counter - 1

    return (start_counter, end_counter)


def schedule_jobs(outdir, start_counter, end_counter):

    for counter in range(start_counter, end_counter + 1):
        fname = "temp_" + str(counter).zfill(5) + ".sbatch"
        fname = os.path.join(outdir, fname)

        try:
            subprocess.run(["sbatch", fname])
        except:
            print(f"Something went wrong with {fname}")


if __name__ == "__main__":

    args = parse_arguments()

    template_script = args.template
    params_csv = args.params
    output_dir = args.output_dir

    template, parameter_set = read_template(template_script)
    params_df = read_params(params_csv)

    if not verify_parameters(params_df, parameter_set):
        raise ValueError("Parameters in CSV and .sbatch do not match")


    file_indices = create_sbatch_scripts(template, parameter_set, params_df, output_dir)

    # schedule_jobs(output_dir, file_indices[0], file_indices[1])

