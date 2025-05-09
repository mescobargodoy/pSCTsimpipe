import argparse
import os

from psctsimpipe.pSCTSimTelArrayRun import single_sim_telarray_pSCT_run
from psctsimpipe.SLURMScriptGen import create_slurm_script, submit_job
from psctsimpipe.Helpers import extract_number


def main():
    parser = argparse.ArgumentParser(
        usage = """submit-single-psct-simtelarray-SLURM-run -i <CORSIKA> \\
            -dir <output> \\
            --sim_telarray_cfg <cfg> \\
            [OPTIONS]
            """,
        description="Submit a single sim_telarray run through SLRUM.",
        epilog="""Example: \n 
        submit-single-psct-simtelarray-SLURM-run
        -i telescope.tar.gz 
        -dir miguel/data  
        --sim_telarray_cfg pSCT.cfg 
        --particle_type gamma
        """
        )
    
    # sim_telarray options
    parser.add_argument(
        "-i",
        "--CORSIKA_input",
        help="path to CORSIKA file"
    )
    parser.add_argument(
        "-dir",
        "--simtel_dir_output",
        help="""path for simtelarray outputs, 
                commandline standrd output and error files,
                and slurm script
                """
    )
    parser.add_argument(
        "-c",
        "--sim_telarray_cfg",
        help="path to sim_telarray config file"
    )
    # sim_telarray naming options
    parser.add_argument(
        "--particle_type",
        default="gamma",
        help="particle type (gamma,proton,electron,gamma_diffuse,...)"
    )
    parser.add_argument(
        "--ze",
        default="20deg",
        help="zenith angle"
    )
    parser.add_argument(
        "--az",
        default="180deg",
        help="azimuth angle"
    )
    parser.add_argument(
        "--NSB",
        default="60MHz",
        help="Night sky background rate"
    )
    parser.add_argument(
        "--height",
        default="1270m",
        help="Height of telescope or observatory"
    )
    parser.add_argument(
        "--telescope_name",
        default="FLWO-pSCT",
        help="Name of telescope or array"
    )
    parser.add_argument(
        "--night_type",
        default="dark",
        help="Oberving conditions (dark, half_moon, full_moon,...)"
    )
    # SLURM options
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
        "--qos",
        default="",
        help="Required to target VERITAS/SCT HB node. Set it to g-veritas if this is the case."
    )
    parser.add_argument(
        "--account",
        default="",
        help="Required to target VERITAS/SCT HB node. Set it to g-veritas if this is the case"
    )
    parser.add_argument(
        "--mail-type", 
        default="END,FAIL",
        help="Type of email notification to receive"
        )
    args = parser.parse_args()

    command = single_sim_telarray_pSCT_run(
        args.CORSIKA_input,
        args.simtel_dir_output,
        args.sim_telarray_cfg,
        args.particle_type,
        args.ze,
        args.az,
        args.NSB,
        args.height,
        args.telescope_name,
        args.night_type
        )
    
    red_CORISKA_input = os.path.basename(args.CORSIKA_input)
    run_num = extract_number(red_CORISKA_input)
    job_name = f"{args.particle_type}{run_num}"

    script_path = create_slurm_script(
        job_name, 
        command, 
        args.email, 
        args.simtel_dir_output, 
        args.mem, 
        args.nodes, 
        args.n_tasks,
        args.cpus_per_task,
        args.t_exp,
        args.partition,
        args.qos,
        args.account,
        args.mail_type
        )
    
    submit_job(script_path)
    print(f"Job submitted! SLURM script: {script_path}")

if __name__ == "__main__":
    main()