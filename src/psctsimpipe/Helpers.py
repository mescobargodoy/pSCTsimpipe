import re
import os
import glob

def extract_number(filename):
    """
    Given a CORSIKA file, extract run number
    For a CORSIKA file named: DAT#.telescope.tar.gz
    The # will be returned


    Parameters
    ----------
    filename : string
        CORSIKA input file

    Returns
    -------
    _type_
        _description_
    """    
    match = re.search(r'DAT(\d+)', filename)  
    if match:
        return int(match.group(1)) 
    return None  


def extract_run_number_from_simtel(filename):
    """
    For a given sim_telarray-naming-based file
    {particle_type}_{ze}_{az}_run#_{telescope_name}-{height}-{night_type}-{NSB}.simtel.gz
    {particle_type}_{ze}_{az}_run#_{telescope_name}-{height}-{night_type}-{NSB}.dl1.h5
    It extracts the number after run

    Parameters
    ----------
    filename : string
        sim_telarray output file

    Returns
    -------
    string
        Run number
    """
    match = re.search(r'run(\d+)', filename)
    return match.group(1) if match else None

def extract_number_from_log(filename):
    """
    Given a CORSIKA file, extract run number
    For a CORSIKA file named: DAT#.telescope.tar.gz
    The # will be returned


    Parameters
    ----------
    filename : string
        log file

    Returns
    -------
    _type_
        _description_
    """    
    filename = os.path.basename(filename)
    match = re.search(r'(\D+)(\d{6})', filename) 
    if match:
        particle_type, run_number =  match.groups()
        return particle_type, run_number
    return None, None

def find_files(dir, search_pattern="*telescope.tar.gz"):
    """
    Finds all the files in a given directory with specific
    pattern in name.

    Parameters
    ----------
    dir : string
        path to search files in
    search_pattern : str, optional
        file extension for instance, by default "*telescope.tar.gz"

    Returns
    -------
    list
        returns a list with absolute paths of files with
        given search_pattern found in dir
    """
    
    files_to_search = os.path.join(dir,search_pattern)
    files = glob.glob(files_to_search)
    files = sorted(files)

    return files

def replace_substring(
        input_string,
        pattern_to_replace,
        replacement
):
    """
    Replaces a substring with user-specified string.

    Parameters
    ----------
    input_string : string
        original string
    pattern_to_replcae : string
        piece to be removed 
        from original string
    replacement : string
        new string piece
    """
    return input_string.replace(pattern_to_replace,replacement)