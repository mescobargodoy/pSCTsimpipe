import os
import errno
import re

def cd_to_corsika_dir():
    """
    Returns
    -------
    string
        command to switch directory to $CORSIKA/run

    Raises
    ------
    EnvironmentError
        If CORSIKA installed directory not exported 
    FileNotFoundError
        If no CORSIKA executable is found
    """

    CORSIKA = os.environ.get('CORSIKA')

    if not CORSIKA:
        raise EnvironmentError("SIMTELDIR environment variable is not set.")

    exe = os.path.join(CORSIKA, "run", "corsika")
    
    if not os.path.exists(exe):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{exe}")
    
    corsika_run_dir = os.path.join(CORSIKA, "run")

    command = f"cd {corsika_run_dir}"

    return command

def exe_corsika(corsika_card):
    """
    Returns
    -------
    string
        ./corsika < corsika_card

    Parameters
    ----------
    corsika_card : path
        path to CORSIKA input card
    """

    command = f"./corsika < {corsika_card}"

    return command