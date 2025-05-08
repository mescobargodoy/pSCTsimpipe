import os
import errno

def single_sim_telarray_run(
        CORSIKA_input,
        output_eventio,
        output_histo,
        sim_telarray_cfg
        ):
    """
    Generates command to run sim_telarray
    given an input file, configuration and
    path to store outputs.

    Parameters
    ----------
    CORSIKA_input : string
        path to CORSIKA file
    output_eventio : string
        path for output eventio
    output_histo : string
        path for output histogram
    sim_telarray_cfg : string
        path to sim_telarray config file

    Returns
    -------
    string
        sim_telarray command to submit to queue

    """    
    
    SIMTELARRAYDIR = os.environ.get('SIMTELDIR')

    if not SIMTELARRAYDIR:
        raise EnvironmentError("SIMTELDIR environment variable is not set.")

    exe = os.path.join(SIMTELARRAYDIR, "bin", "sim_telarray")
    
    if not os.path.exists(exe):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{exe}")
    
    if not os.path.exists(CORSIKA_input):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{CORSIKA_input}")
    
    if not os.path.exists(sim_telarray_cfg):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{sim_telarray_cfg}")
    
    command = f"""{exe} -c {sim_telarray_cfg} -h {output_histo} -o {output_eventio} {CORSIKA_input}"""

    return command
