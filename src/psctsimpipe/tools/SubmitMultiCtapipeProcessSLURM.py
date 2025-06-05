import argparse
import os

from psctsimpipe.CtapipeProcessCommand import create_ctapipe_process_command
from psctsimpipe.SLURMScriptGen import create_ctapipe_slurm_script, submit_job
from psctsimpipe.Helpers import extract_run_number_from_simtel, find_files


def main():
    parser = argparse.ArgumentParser(
        usage = """submit-multi-ctapipe-process-SLURM-run \\
            --input-dir <input_dir> \\
            --output-dir <output_dir> \\
            -c <cfg> \\
            --particle_type <particle> \\
            --run-number-domain a b \\
            --file-ext <file-extension>
            [OPTIONS]
            """,
        description="""Submit ctapipe-process runs through SLURM 
                    for a selection of sim_telarray files in directory.""",
        epilog="""Example: \n 
        submit-multi-ctapipe-process-SLURM-run 
        --input-dir /gamma
        --output-dir /data  
        -c /path/to/ctapipe_config.yaml
        --particle_type gamma
        --run-number-domain 100000 100100
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
        "--run-number-domain",
        type=int,
        nargs=2,
        help="""Submit jobs corresponding to simtel files between these
                two run numbers (inclusive)""",
        default=[100000,100100]
    )
    parser.add_argument(
        "--file-ext",
        default="simtel.gz",
        help="File extension of sim_telarray output to be searched for"
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

    files_to_process = find_files(args.input_dir,
                                  search_pattern=args.file_ext)

    print(f"Found {len(files_to_process)} files in {args.input_dir} matching pattern {args.file_ext}.")
    print(f"Only processing {args.run_number_domain[1]-args.run_number_domain[0]+1} files.")

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

        low_run_num_edge=int(args.run_number_domain[0])
        high_run_num_edge=int(args.run_number_domain[1])
        
        if low_run_num_edge <= int(run_num) <= high_run_num_edge:

            script_path = create_ctapipe_slurm_script(
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
                args.qos,
                args.account,
                args.mail_type
                )
        
            submit_job(script_path)
            print(f"Job submitted! SLURM script: {script_path}")
    print("Done submitting all jobs!")

if __name__ == "__main__":
    main()