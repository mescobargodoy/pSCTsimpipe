import os
import errno
import re
from psctsimpipe.Helpers import extract_number

def single_sim_telarray_pSCT_run(
        CORSIKA_input,
        output_directory,
        sim_telarray_cfg,
        particle_type="proton",
        ze="20deg",
        az="180deg",
        NSB="60MHz",
        height="1270m",
        telescope_name="FLWO-pSCT",
        night_type="dark"
        ):
    """
    Generates command to run pSCT sim_telarray
    runs. 

    For a CORSIKA file named: DAT#.telescope.tar.gz
    the corresponding sim_telarray outputs will be:
    {particle_type}_{ze}_{az}_run#_{telescope_name}-{height}-{night_type}-{NSB}.simtel.gz 
    {particle_type}_{ze}_{az}_run#_{telescope_name}-{height}-{night_type}-{NSB}.hdata.gz

    Parameters
    ----------
    CORSIKA_input : string
        path to CORSIKA file
    output_directory : string
        path for simtelarray outputs, 
        commandline standrd output and error files,
        and slurm scripts
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
    
    red_CORSIKA_input = os.path.basename(CORSIKA_input)
    
    run_number = extract_number(red_CORSIKA_input)

    eventio_name = f"{particle_type}_{ze}_{az}_run{run_number}_{telescope_name}-{height}-{night_type}-{NSB}.simtel.gz "
    histo_name = f"{particle_type}_{ze}_{az}_run{run_number}_{telescope_name}-{height}-{night_type}-{NSB}.hdata.gz"
    
    output_eventio = os.path.join(output_directory,eventio_name)
    output_histo = os.path.join(output_directory,histo_name)

    command = f"{exe} -c {sim_telarray_cfg} -h {output_histo} -o {output_eventio} {CORSIKA_input}"

    return command