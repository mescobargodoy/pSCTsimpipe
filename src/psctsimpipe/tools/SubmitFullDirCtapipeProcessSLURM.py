import argparse
import os

from psctsimpipe.CtapipeProcessCommand import create_ctapipe_process_command
from psctsimpipe.SLURMScriptGen import create_slurm_script, submit_job
from psctsimpipe.Helpers import extract_run_number_from_simtel, find_files


def main():
    parser = argparse.ArgumentParser(
        usage = """submit-all-ctapipe-process-SLURM-run \\
            --input-dir <input_dir> \\
            --output-dir <output_dir> \\
            -c <cfg> \\
            --particle_type <particle>
            [OPTIONS]
            """,
        description="""Submit ctapipe-process runs through SLURM 
                    for all sim_telarray files in directory.""",
        epilog="""Example: \n 
        submit-all-ctapipe-process-SLURM-run 
        --input-dir /gamma
        --output-dir /data  
        -c /path/to/ctapipe_config.yaml
        --particle_type gamma
        --file-ext simtel.gz
        """
        )
    # ctapipe-process
    parser.add_argument(
        "--input-dir",
        help="path to directory where all sim_telarray files live."
    )
    parser.add_argument(
        "--output-dir",
        help="""path for ctapipe-process outputs, 
                commandline standard output and error files,
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
    parser.add_argument(
        "--file-ext",
        default="simtel.gz",
        help="File extension of sim_telarray output to be searched for"
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
        default=None,
        help="Required to target VERITAS/SCT HB node. Set it to g-veritas if this is the case."
    )
    parser.add_argument(
        "--account",
        default=None,
        help="Required to target VERITAS/SCT HB node. Set it to g-veritas if this is the case"
    )
    parser.add_argument(
        "--mail-type", 
        default="END,FAIL",
        help="Type of email notification to receive"
        )
    parser.add_argument(
        "--suprres_stdout_error", 
        default=False,
        help="Whether to suppress the standard output and error of slurm report, by default False"
    )
    args = parser.parse_args()

    files_to_process = find_files(args.input_dir,
                                  search_pattern=f"*{args.file_ext}")

    print(f"Found {len(files_to_process)} *{args.file_ext} files in {args.input_dir}")

    for file in files_to_process:
        
        command = create_ctapipe_process_command(
            file,
            args.output_dir,
            args.ctapipe_cfg,
            args.file_ext
            )
        
        base_filename = os.path.basename(file)
        run_num = extract_run_number_from_simtel(base_filename)
        job_name = f"{args.particle_type}{run_num}"

        script_path = create_slurm_script(
            job_name, 
            command,
            'ctapipe',
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
            args.mail_type,
            args.suprres_stdout_error
            )
    
        submit_job(script_path)
        print(f"Job submitted! SLURM script: {script_path}")
    print("Done submitting all jobs!")

if __name__ == "__main__":
    main()