import os
import argparse
import re

from psctsimpipe.Helpers import find_files
from psctsimpipe.pSCTTriggerRate import trigger_rate_command
from psctsimpipe.SLURMScriptGen import create_supp_slurm_script, submit_job

def main():
    parser = argparse.ArgumentParser(
        usage = """submit-simtelarray-trigger-rate-SLURM-run --input-dir <input_dir> \\
                --output-dir <output_dir> \\
                --sim_telarray_cfg <sim_telarray_cfg>
                """,
        description="""Submit a single sim_telarray run through SLRUM
        for trigger rate/threshold studies.
        The relevant output file is the log file. The naming scheme used for the log is
        triggthresh<trigger_threshold>pe_pixmult<n_trigger_pixels>_<job_number>.out
        SLURM writes the standard output to these .out files.""",
        epilog="""Example: \n 
        submit-simtelarray-trigger-rate-SLURM-run 
        --input-dir data/
        --output-dir output/
        --search-pattern *telescope.tar.gz 
        --sim_telarray_cfg pSCT.cfg
        --trigger_pixels 3
        --discriminator_threshold 7.5
        --fadc_bins 84
        --fadc_sum_bins 64
        --disc_bins 80
        --disc_start 0
        --trigger_current_limit 100000
        --maximum_telescopes 5
        --trigger_telescopes 1
        --night_type DARK
        --NSB 60MHZ
        --email myemail@domain
        """
        # --ignore_telescopes 2 3 4 5
        )
    # sim_telarray options
    parser.add_argument(
        "-i",
        "--input-dir",
        help="path to CORSIKA file directory"
    )
    parser.add_argument(
        "--output-dir",
        help="""path for simtelarray output log, 
                commandline standrd output and error files,
                and slurm scripts.
                """
    )
    parser.add_argument(
        "--search-pattern",
        default="*telescope.tar.gz",
        help="Search pattern for CORSIKA files."
    )
    parser.add_argument(
        "-c",
        "--sim_telarray_cfg",
        help="path to sim_telarray config file"
    )
    parser.add_argument(
        "--trigger_pixels", 
        default=3,  
        help="trigger pixel multiplicity"
        )
    parser.add_argument(
        "--discriminator_threshold", 
        default=7.45,  
        help="trigger threshold"
        )
    parser.add_argument(
        "--fadc_bins", 
        default=100,  
        help="""Number of time intervals simulated 
        for ADC."""
        )
    parser.add_argument(
        "--fadc_sum_bins", 
        default=100,  
        help="""Number of ADC time intervals 
        actually read out."""
        )
    parser.add_argument(
        "--disc_bins", 
        default=100,  
        help="""Number of time intervals simulated
        for trigger."""
        )
    parser.add_argument(
        "--disc_start", 
        default=0,  
        help="""How many intervals the trigger 
        simulation starts before the ADC."""
        )
    parser.add_argument(
        "--trigger_current_limit", 
        default=100000,  
        help="""Pixels above this limit are
        exluded from the trigger"""
        )
    parser.add_argument(
        "--maximum_telescopes", 
        default=1,  
        help="""max number of telescopes configued
        at startup. At least as large as
        the number of telescopes used in
        CORSIKA sims."""
        )
    parser.add_argument(
        "--trigger_telescopes", 
        default=1,  
        help="""Number of telescopes required 
        for the system to trigger."""
        )
    # parser.add_argument(
    #     "--ignore_telescopes",
    #     nargs="+",
    #     help="""List of telescopes ignored""",
    #     default=-1,
    #     )
    parser.add_argument(
        "--night_type", 
        default="DARK",  
        help="""For output file naming purposes
        DARK, HALF-MOON,MOON, by default "DARK"""
        )
    parser.add_argument(
        "--NSB", 
        default="60MHz",  
        help="""For output file naming purposes #MHz"""
        )
    # SLURM options
    parser.add_argument(
        "--job-name", 
        default="NSBTriggerRate", 
        help="Job/SLURM-file name (shows when running squeue)"
        )
    parser.add_argument(
        "--email", 
        default="",
        help="Email for job notifications"
        )
    parser.add_argument(
        "--mem", 
        default="8G", 
        help="Memory per node (e.g., 1G, 10G, etc.)"
        )
    parser.add_argument(
        "--nodes", 
        default=1, 
        type=int, 
        help="Number of nodes requested"
        )
    parser.add_argument(
        "--n-tasks", 
        default=1, 
        type=int, 
        help="Number of task per CPU core"
        )
    parser.add_argument(
        "--cpus-per-task", 
        default=1, 
        type=int, 
        help="Number of CPU cores to use per task"
        )
    parser.add_argument(
        "-t", 
        "--t_exp", 
        default="2:00:00", 
        help="Time allocated before job expires (e.g., HH:MM:SS)"
        )
    parser.add_argument(
        "--partition", 
        default="128x24",
        help="Partition/queue name"
        )
    parser.add_argument(
        "--mail-type", 
        default="END,FAIL",
        help="Type of email notification to receive"
        )
    args = parser.parse_args()

    corsika_files = find_files(args.input_dir,args.search_pattern)

    print(f"{len(corsika_files)} files ending with {args.search_pattern} found in {args.input_dir}")

    for corsika_f in corsika_files:

        red_CORISKA_input = os.path.basename(corsika_f)
        match = re.search(r'DATDummy10000\.seed(\d+)\.telescope\.tar\.gz', red_CORISKA_input)
        if match:
            seed_num = int(match.group(1))

        command = trigger_rate_command(
            corsika_f,
            args.sim_telarray_cfg,
            args.output_dir,
            args.trigger_pixels,
            args.discriminator_threshold,
            args.fadc_bins,
            args.fadc_sum_bins,
            args.disc_bins,
            args.disc_start,
            args.trigger_current_limit,
            args.maximum_telescopes,
            args.trigger_telescopes,
            # args.ignore_telescopes,
            args.night_type,
            args.NSB
        )

        job_name=f"seed{seed_num}_triggthresh{args.discriminator_threshold}pe_pixmult{args.trigger_pixels}_fadc_bins{args.fadc_bins}_fadc_sum_bins{args.fadc_sum_bins}_disc_bins{args.disc_bins}"
        
        script_path = create_supp_slurm_script(
            job_name, 
            command, 
            args.email, 
            args.output_dir, 
            args.mem, 
            args.nodes, 
            args.n_tasks,
            args.cpus_per_task,
            args.t_exp,
            args.partition,
            args.mail_type
        )
        
        submit_job(script_path)
        print(f"Job submitted! SLURM script: {script_path}")

if __name__ == "__main__":
    main()