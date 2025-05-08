import os
import errno

def create_ctapipe_merge_command(
        input_dir,
        output_dir,
        pattern='*dl1.h5',
        config=None
):
    """
    Generates ctapipe-merge  command

    ctapipe-merge --input-dir <input> --output-dir <output_dir> --pattern '*.dl1.h5'\\
                    -c <config.yaml> -l <log> --provenance-log <prov>

    For an input directory of the form
    {particle_type}_{ze}_{az}_run#_{telescope_name}-{height}-{night_type}-{NSB},
    all files within this directory ending in pattern will be merged using ctapipe-merge.

    The outputs (merged h5, log, provenance) will follow this naming convention:
    output_dir/{input_dir}.dl1.h5
    output_dir/{input_dir}.log
    output_dir/{input_dir}.provenance.log

    Parameters
    ----------
    input_dir : string
        sim_telarray output file
    output_dir : string
        path to store all output files
    pattern : string
        files having this pattern will be merged 
        into single file
    config : string, 
        ctapipe-merge config file
    """

    if not os.path.exists(input_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{input_dir}")

    base_name = os.path.basename(input_dir)

    merged_output_file = f"{base_name}.merged.dl1.h5"
    log_output_file = f"{base_name}.merged.log"
    prov_output_file = f"{base_name}.merged.provenance.log"

    output = os.path.join(output_dir,merged_output_file)        
    log = os.path.join(output_dir,log_output_file)
    prov = os.path.join(output_dir,prov_output_file)
    
    if config is not None: 
        command = f"ctapipe-merge --input-dir {input_dir} -o {output} -c {config} -l {log} --provenance-log {prov} --pattern {pattern}"
        return command
    else:
        command = f"ctapipe-merge --input-dir {input_dir} -o {output} -l {log} --provenance-log {prov} --pattern {pattern}"
        return command