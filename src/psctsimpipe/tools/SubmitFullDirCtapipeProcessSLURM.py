import argparse
import os

from psctsimpipe.CtapipeProcessCommand import create_ctapipe_process_command
from psctsimpipe.SLURMScriptGen import create_ctapipe_slurm_script, submit_job
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

    files_to_process = find_files(args.input_dir,
                                  search_pattern="*simtel.gz")

    print(f"Found {len(files_to_process)} .simtel.gz files in {args.input_dir}")

    for file in files_to_process:
        
        command = create_ctapipe_process_command(
            file,
            args.output_dir,
            args.ctapipe_cfg,
            )
        
        base_filename = os.path.basename(file)
        run_num = extract_run_number_from_simtel(base_filename)
        job_name = f"{args.particle_type}{run_num}"

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
            args.mail_type
            )
    
        submit_job(script_path)
        print(f"Job submitted! SLURM script: {script_path}")
    print("Done submitting all jobs!")

if __name__ == "__main__":
    main()