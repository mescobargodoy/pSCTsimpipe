import os
import errno

from psctsimpipe.Helpers import find_files, replace_substring


def create_ctapipe_process_command(
        input_file,
        output_dir,
        config
):
    """
    Generates ctapipe-process single command

    ctapipe-process -i <input> -o <output> -c <config> \\
                    -l <log> --provenance-log <prov>

    For an input of the form
    {particle_type}_{ze}_{az}_run#_{telescope_name}-{height}-{night_type}-{NSB}.simtel.gz
    The outputs will follow the same convention with the following file types
    .dl1.h5
    .log
    .prov

    These files will be stored in output_dir

    Parameters
    ----------
    input_file : string
        sim_telarray output file
    output_dir : string
        path to store all output files
    config : string, 
        ctapipe-procecss config file
    """

    if not os.path.exists(input_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{input_file}")

    if not os.path.exists(config):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{config}")

    base_file = os.path.basename(input_file)

    output = os.path.join(output_dir,replace_substring(base_file, "simtel.gz", "dl1.h5"))        
    log = os.path.join(output_dir,replace_substring(base_file,"simtel.gz","log"))
    prov = os.path.join(output_dir,replace_substring(base_file, "simtel.gz", "provenance.log"))
    command = f"ctapipe-process -i {input_file} -o {output} -c {config} -l {log} --provenance-log {prov}"

    return command


def create_full_dir_ctapipe_process_command(
        input_dir,
        output_dir,
        config
):
    """
   Generates ctapipe-process command for multiple files

    ctapipe-process -i <input> -o <output> -c <config> \\
                    -l <log> --provenance-log <prov>


    For an input of the form
    {particle_type}_{ze}_{az}_run#_{telescope_name}-{height}-{night_type}-{NSB}.simtel.gz
    The outputs will follow the same convention with the following file types
    .dl1.h5
    .log
    .prov

    These files will be stored in output_dir

    Parameters
    ----------
    input_file : string
        sim_telarray output file
    output_dir : string
        path to store all output files
    config : string, 
        ctapipe-procecss config file

    Returns
    ----------
    list
        contains commands to execute per file
    """

    if not os.path.exists(input_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{input_file}")

    if not os.path.exists(config):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{config}")


    files_to_process = find_files(input_dir,
                                  search_pattern="*simtel.gz")
    
    commands_to_submit = []

    for input_file in files_to_process:
        
        base_file = os.path.basename(input_file)

        output = os.path.join(output_dir,replace_substring(base_file, "simtel.gz", "dl1.h5"))        
        log = os.path.join(output_dir,replace_substring(base_file,"simtel.gz","log"))
        prov = os.path.join(output_dir,replace_substring(base_file, "simtel.gz", "provenance.log"))
        command = f"ctapipe-process -i {input_file} -o {output} -c {config} -l {log} --provenance-log {prov}"

        commands_to_submit.append(command)
    
    return commands_to_submit

