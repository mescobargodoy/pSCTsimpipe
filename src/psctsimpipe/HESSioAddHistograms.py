import subprocess
import os
import glob

def add_histograms(input_directory,output):
    """
    Wrapper around hessio/bin/add_histograms

    Parameters
    ----------
    input_directory : string
        directory where hdata.gz files live
    output : string
        Path for output file

    Returns
    -------
    list
        command to be submitted for queue

    Raises
    ------
    EnvironmentError
        Set CTA_PATH in your bashrc.
        This is where sim_telarray, corsika, 
        hessio are installed.
    """    
    CTA_PATH = os.environ.get("CTA_PATH")  

    if not CTA_PATH:
        raise EnvironmentError("CTA_PATH environment variable is not set.")
    
    executable = os.path.join(CTA_PATH, "hessioxxx/bin/add_histograms")

    hdata_files = glob.glob(os.path.join(input_directory, "*.hdata.gz"))

    command = [executable] + hdata_files + ["-o", output]

    return command