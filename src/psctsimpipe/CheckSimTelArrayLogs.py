import os
import re
import glob
import subprocess
import textwrap

from psctsimpipe.Helpers import extract_number_from_log
from psctsimpipe.SLURMScriptGen import submit_job

def return_log_file_status(directory):
    """
    Checks all .out log files in the given directory 
    to ensure they end with "Sim_telarray finished".

    Parameters
    ----------
    directory : string
        directory where log files live

    Returns
    -------
    dict
        A dictionary where keys are filenames 
        and values are True (valid) or False (invalid).
    """   
    results = {}
    
    for filename in os.listdir(directory):
        if filename.endswith(".out"):  # Only process .out files
            file_path = os.path.join(directory, filename)
            
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    if lines and "Sim_telarray finished" in lines[-1]:  # Check last line
                        results[file_path] = True
                    else:
                        results[file_path] = False
            except Exception as e:
                results[file_path] = f"Error reading file: {e}"

    return results

def check_simtelarray_log_files(directory):
    """
    Checks all .out log files in the given directory 
    to ensure they end with "Sim_telarray finished".

    Parameters
    ----------
    directory : string
        directory where log files live

    Returns
    -------
    None
        Prints to terminal which files finished successfully
        and which ones didn't.
    """    
    success=0
    failed=0
    for filename in os.listdir(directory):
        if filename.endswith(".out"):  
            file_path = os.path.join(directory, filename)

            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    if lines and "Sim_telarray finished" in lines[-1]:  # Check last line
                        print(f"[✓] {filename} - Finished successfully")
                        success+=1
                    else:
                        print(f"[X] {filename} - Did NOT finish successfully")
                        failed+=1
            except Exception as e:
                print(f"[!] {filename} - Unable to read file: {e}")
                failed+=1
    print(f"Total runs submitted: {success+failed}")
    print(f"{success} successful runs.")
    print(f"{failed} failed runs.")

def check_corsika_log_files(directory):
    """
    Checks all .out log files in the given directory 
    to ensure they end with "Sim_telarray finished".

    Parameters
    ----------
    directory : string
        directory where log files live

    Returns
    -------
    None
        Prints to terminal which files finished successfully
        and which ones didn't.
    """
    log_ending = " ========== END OF RUN ================================================"    
    success=0
    failed=0
    for filename in os.listdir(directory):
        if filename.endswith(".out"):  
            file_path = os.path.join(directory, filename)

            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    if lines and log_ending in lines[-1]:  # Check last line
                        print(f"[✓] {filename} - Finished successfully")
                        success+=1
                    else:
                        print(f"[X] {filename} - Did NOT finish successfully")
                        failed+=1
            except Exception as e:
                print(f"[!] {filename} - Unable to read file: {e}")
                failed+=1
    print(f"Total runs submitted: {success+failed}")
    print(f"{success} successful runs.")
    print(f"{failed} failed runs.")

def extract_naming_convention_from_output_files(filename):
    """
    From an output eventio file extracts relevant parameters
    related to naming convention.

    Parameters
    ----------
    filename : string
        _description_

    Returns
    -------
    dictionary
        Outputs a dictionary with the extracted values.
    """    
    filename = os.path.basename(filename)
    pattern = (
        r"(?P<particle_type>[^_]+)_"     # particle_type
        r"(?P<ze>\d+deg)_"               # zenith angle 
        r"(?P<az>\d+deg)_"               # azimuth angle 
        r"run\d+_"                       # Skip run#
        r"(?P<telescope_name>.+?)-"      # Telescope name 
        r"(?P<height>\d+m)-"             # height 
        r"(?P<night_type>[^-]+)-"        # night type 
        r"(?P<NSB>\d+MHz)\.simtel\.gz"    # NSB value 
    )
    match = re.match(pattern, filename)
    if match:
       return match.groupdict()  # Outputs a dictionary with the extracted values
    else:
        print(f"⚠️ Warning: Could not extract details from {filename}")


def extract_simtel_run_params(directory):
    """
    Extracts relevant parameters from failed sim_telarray job log files.

    Parameters:
        log_status_dict (dict): A dictionary with log file paths as keys and 
                                True (success) or False (failure) as values.

    Returns:
        list of dict: List of dictionaries containing extracted parameters for each failed job.
    """
    failed_jobs_info = []

    # Get SIMTELDIR environment variable
    SIMTELARRAYDIR = os.environ.get('SIMTELDIR')
    if not SIMTELARRAYDIR:
        print("Warning: SIMTELDIR environment variable is not set.")

    log_status_dict = return_log_file_status(directory)

    pattern = (
        r"Starting .*?sim_telarray with the following arguments:  "  # Match start of the line
        r"\[-c\] \[(.*?)\]"  # CONFIG file
        r".*?\[-h\] \[(.*?)\]"  # Histogram output file
        r".*?\[-o\] \[(.*?)\]"  # Event output file
        r".*?\[\s*(/.*?/DAT\d+\.telescope\.tar\.gz)\s*\]"  # Full path of CORSIKA input
    )

    for file_path, status in log_status_dict.items():
        if not status:  # Only process failed jobs
            try:
                if os.path.getsize(file_path)==0:
                    
                    particle_type, run_num = extract_number_from_log(file_path)
                    
                    print(f"Warning: {file_path} is empty and cannot be processed!")
                    print("Will attempt to resubmit SLURM script if it exists.")
                    
                    # Finding SLURM script
                    slurm_file_from_empty_log = f"{particle_type}{run_num}*.slurm"
                    slurm_search_empty_log = os.path.join(directory,slurm_file_from_empty_log)
                    file_assoc_empty_log = glob.glob(slurm_search_empty_log)
                    slurm_script_to_resub = file_assoc_empty_log[0]
                    
                    if os.path.exists(slurm_script_to_resub):
                        print(f"Submitting {slurm_script_to_resub} to queue.")
                        submit_job(slurm_script_to_resub)
                        
                        # Finding standard error output associated with run to be deleted
                        std_err_out_assoc_w_empty_log = os.path.splitext(file_path)[0] + ".error"
                        if os.path.exists(std_err_out_assoc_w_empty_log):
                            print(textwrap.dedent(
                                f"""
                                Deleting the following files:
                                {file_path}
                                {std_err_out_assoc_w_empty_log}
                                """))
                            
                            subprocess.run([
                                "rm", 
                                file_path, 
                                std_err_out_assoc_w_empty_log
                                ])


                    else:
                        print("SLURM script was not found")
                        print("Make sure you resubmit this job manually.")
                        print(f"The particle type is {particle_type}")
                        print(f"The run number is {run_num} ")
                    
                    continue
                
                print(f"Extracting information from {file_path}")
                with open(file_path, "r") as f:
                    for line in f:
                            match = re.search(pattern, line)
                            if match:
                                config_file = match.group(1)  # CONFIG file path
                                histogram_output = match.group(2)  # Histogram output file
                                event_output = match.group(3)  # Event output file
                                corsika_input = match.group(4)  
                                output_dir = os.path.dirname(file_path)  # Use log file directory
                                std_err_file = os.path.splitext(file_path)[0] + ".error"
                                
                                # This part of the code extracts relevant parameters for naming
                                run_name_info = extract_naming_convention_from_output_files(event_output)
                                particle_type = run_name_info["particle_type"]
                                ze = run_name_info["ze"]
                                az = run_name_info["az"]
                                telescope_name = run_name_info["telescope_name"]
                                height = run_name_info["height"]
                                night_type = run_name_info["night_type"]
                                NSB = run_name_info["NSB"]
                                
                                # This part of the code searches for the SLURM script
                                _, run_num = extract_number_from_log(file_path)
                                slurm_file_type = f"{particle_type}{run_num}*.slurm"
                                slurm_search = os.path.join(directory,slurm_file_type)
                                slurm_files = glob.glob(slurm_search)
                                slurm_script = slurm_files[0]

                                # Store extracted values in a dictionary
                                failed_jobs_info.append(
                                    {
                                    "config_file": config_file,
                                    "histogram_output": histogram_output,
                                    "event_output": event_output,
                                    "corsika_input": corsika_input,
                                    "output_dir": output_dir,
                                    "log_file": file_path,
                                    "std_err_file": std_err_file,
                                    "slurm_script": slurm_script,
                                    "particle_type": particle_type,
                                    "ze": ze,
                                    "az": az,
                                    "telescope_name": telescope_name,
                                    "height": height,
                                    "night_type": night_type,
                                    "NSB": NSB 
                                    }
                                )
                            break  

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return failed_jobs_info