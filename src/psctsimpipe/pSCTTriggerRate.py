import os
import re
import errno
import warnings

def trigger_rate_command(
        CORSIKA_input,
        sim_telarray_cfg,
        output_dir,
        trigger_pixels,
        discriminator_threshold,
        fadc_bins=84,
        fadc_sum_bins=64,
        disc_bins=80,
        disc_start=0,
        trigger_current_limit=100000,
        maximum_telescopes=1,
        trigger_telescopes=1,
        # ignore_telescopes=-1,
        night_type="DARK",
        NSB="60MHz"
        ):
    """
    Generates command to run sim_telarray
    on CORSIKA dummy file.

    Parameters
    ----------
    CORSIKA_input : string
        path to CORSIKA file
    sim_telarray_cfg : string
        path to sim_telarray config file
    output_dir : string
        path for simtelarray outputs, 
        commandline standrd output and error files
    trigger_pixels : int
        trigger pixel multiplicity
    discriminator_threshold : float
        trigger threshold
    fadc_bins : int, optional
        Number of time intervals simulated 
        for ADC, by default 84
    fadc_sum_bins : int, optional
        Number of ADC time intervals 
        actually read out, by default 64
    disc_bins : int, optional
        Number of time intervals simulated
        for trigger, by default 80
    disc_start : int, optional
        How many intervals the trigger 
        simulation starts before the 
        ADC, by default 0
    trigger_current_limit : int, optional
        Pixels above this limit are
        exluded from the trigger, by default 100000
    maximum_telescopes : int, optional
        max number of telescopes configued
        at startup. At least as large as
        the number of telescopes used in
        CORSIKA sims, by default 1
    trigger_telescopes : int, optional
        Number of telescopes required 
        for the system to trigger, by default 1
    ignore_telescopes : list, optional
        List of telescopes ignored
    night_type : str, optional
        For output file naming purposes
        DARK, HALF-MOON,MOON, by default "DARK"
    NSB : str, optional
        For output file naming purposes        
        #MHz, by default "60MHz"

    Returns
    -------
    string
        SimTelarray command 

    Raises
    ------
    EnvironmentError
        Requires environment variable SIMTELDIR
        path where compiled sim_telarray is.
    """
    
    SIMTELARRAYDIR = os.environ.get('SIMTELDIR')
    if not SIMTELARRAYDIR:
        raise EnvironmentError("SIMTELDIR environment variable is not set.")
    
    if not os.path.exists(CORSIKA_input):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{CORSIKA_input}")
    
    if not os.path.exists(sim_telarray_cfg):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{sim_telarray_cfg}")
    
    if not os.path.exists(output_dir):
        warnings.warn(f"Directory '{output_dir}' does not exist. It will be created.", UserWarning)
        os.makedirs(output_dir, exist_ok=True)

    red_CORISKA_input = os.path.basename(CORSIKA_input)
    match = re.search(r'DATDummy10000\.seed(\d+)\.telescope\.tar\.gz', red_CORISKA_input)
    if match:
        seed_num = int(match.group(1))

    log_trig_info = f"TriggPixMult{trigger_pixels}_DiscrimThresh{discriminator_threshold}_"
    log_fadc_info = f"fadc_bins{fadc_bins}_fadc_sum_bins{fadc_sum_bins}_disc_bins{disc_bins}_"
    log_base = f"pSCT-1270m-{night_type}-{NSB}.seed{seed_num}.log"
    log_base = "".join([log_trig_info, log_fadc_info, log_base])


    log_file = os.path.join(output_dir, log_base)

    simtel_base = log_base.replace("log", "simtel.gz")
    simtel_file = os.path.join(output_dir, simtel_base)

    command = " ".join([
        f"{SIMTELARRAYDIR}bin/sim_telarray",
        f"-o {simtel_file}",
        f"-c {sim_telarray_cfg}",
        f"-C trigger_current_limit={trigger_current_limit}",
        "-C iobuf_maximum=20000000",
        f"-C maximum_telescopes={maximum_telescopes}",
        f"-C trigger_telescopes={trigger_telescopes}",
        # f"-C ignore_telescopes={' '.join(map(str, ignore_telescopes))}",
        "-C min_photons=0",
        "-C min_photoelectrons=0",
        f"-C fadc_bins={fadc_bins}",
        f"-C fadc_sum_bins={fadc_sum_bins}",
        f"-C disc_bins={disc_bins}",
        f"-C disc_start={disc_start}",
        "-C default_trigger=Majority",
        f"-C discriminator_threshold={discriminator_threshold}",
        f"-C trigger_pixels={trigger_pixels}",
        "-C nsb_scaling_factor=2",
        "-C output_format=0",
        "-C Random_State=none",
        "-C histogram_file=/dev/null",
        "-C list=all",
        f"{CORSIKA_input}",
        f"> {log_file} 2>&1"
    ])

    return command
