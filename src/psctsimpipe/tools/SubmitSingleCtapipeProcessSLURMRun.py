import argparse
import os

from psctsimpipe.CtapipeProcessCommand import create_ctapipe_process_command
from psctsimpipe.SLURMScriptGen import create_ctapipe_slurm_script, submit_job
from psctsimpipe.Helpers import extract_run_number_from_simtel


def main():
    parser = argparse.ArgumentParser(
        usage = """submit-single-ctapipe-process-SLURM-run \\
            --input-file <input_file> \\
            --output-dir <output_dir> \\
            -c <cfg> \\
            --particle_type gamma
            [OPTIONS]
            """,
        description="""Submit ctapipe-process run through SLURM 
                    for single sim_telarray file.""",
        epilog="""Example: \n 
        submit-single-ctapipe-process-SLURM-run 
        --input-file sim_telarray/gamma.simtel.gz
        --output-dir user/data  
        -c /path/to/R0toDL1.yaml
        --particle_type gamma
        --email user@domain
        """
        )
    # ctapipe-process
    parser.add_argument(
        "--input-file",
        help="path to file where sim_telarray file lives."
    )
    parser.add_argument(
        "--output-dir",
        help="""path for ctapipe-process outputs, 
                commandline standrd output and error files,
                and slurm scripts.
                """
    )
    parser.add_argument(
        "-c",
        "--ctapipe_cfg",
        help="path to ctapipe config file"
    )
    # naming options
    parser.add_argument(
        "--particle_type",
        default="gamma",
        help="particle type (gamma,proton,electron,gamma_diffuse,...)"
    )
    # SLURM options
    parser.add_argument(
        "--conda_env",
        default="ctapipe",
        help="conda environment to activate. By default ctapipe"
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
        
    command = create_ctapipe_process_command(
        args.input_file,
        args.output_dir,
        args.ctapipe_cfg,
        )
    
    print(f"Creating ctapipe-process SLURM submission script for {args.input_file}.")

    base_filename = os.path.basename(args.input_file)
    run_num = extract_run_number_from_simtel(base_filename)
    job_name = f"{args.particle_type}{run_num}"

    script_path = create_ctapipe_slurm_script(
        job_name, 
        command, 
        args.conda_env,
        args.email, 
        args.output_dir, 
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
