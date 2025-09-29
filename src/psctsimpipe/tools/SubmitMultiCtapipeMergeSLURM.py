import argparse
import os

from psctsimpipe.CtapipeMergeCommand import create_multi_ctapipe_merge_command
from psctsimpipe.SLURMScriptGen import create_ctapipe_slurm_script, submit_job
from psctsimpipe.Helpers import find_files, extract_run_number_from_simtel

def main():
    parser = argparse.ArgumentParser(
        usage = """submit-multi-ctapipe-merge-SLURM-run \\
            --input-dir <input_dir> \\
            --output-dir <output_dir> \\
            --search-pattern '*dl1.h5' \\
            --run-number-domain a b \\
            -c <cfg> \\
            [OPTIONS]
            """,
        description="""Submit ctapipe-merge job through SLURM 
                    for ctapipe h5 files within run number domain in directory.
                    For an input directory of the form
                    {particle_type}_{ze}_{az}_run#_{telescope_name}-{height}-{night_type}-{NSB},
                    all files within this directory ending in pattern within run number [a,b] will be merged using ctapipe-merge.

                    The outputs (merged h5, log, provenance) will follow this naming convention:
                    output_dir/{input_dir}.dl1.h5
                    output_dir/{input_dir}.log
                    output_dir/{input_dir}.provenance.log
                    """,
        epilog="""Example: \n 
        submit-multi-ctapipe-merge-SLURM-run  
        --input-dir /gamma/h5/
        --output-dir /gamma/h5/  
        --search-pattern '*dl1.h5'
        --run-number-domain 100000 100100
        -c /path/to/ctapipe_config.yaml
        """
        )
    # ctapipe-merge
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
        "--run-number-domain",
        type=int,
        nargs=2,
        help="""Submit jobs corresponding to files between these
                two run numbers (inclusive)""",
        default=[100000,100100]
    )
    parser.add_argument(
        "--search-pattern",
        default="'*dl1.h5'",
        help="Give a specific file pattern for matching files in input-dir"
    )
    parser.add_argument(
        "-c",
        "--ctapipe_cfg",
        default=None,
        help="path to ctapipe config file"
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

    all_files_in_dir = find_files(args.input_dir,
                                  search_pattern=args.search_pattern)

    print(f"Found {len(all_files_in_dir)} files in {args.input_dir} matching pattern '{args.search_pattern}'.")
    print(f"Will attempt {args.run_number_domain[1]-args.run_number_domain[0]+1} files.")
    print("Check the ctapipe log file to check the actual number of files that were merged after the job is done.")

    files_to_merge = []

    for file in all_files_in_dir:
        
        base_filename = os.path.basename(file)
        run_num = extract_run_number_from_simtel(base_filename)

        low_run_num_edge=int(args.run_number_domain[0])
        high_run_num_edge=int(args.run_number_domain[1])
        
        if low_run_num_edge <= int(run_num) <= high_run_num_edge:

            files_to_merge.append(file)
    
    command = create_multi_ctapipe_merge_command(
        args.input_dir,
        files_to_merge,
        args.output_dir,
        args.ctapipe_cfg
    )
        
    base_filename = os.path.basename(os.path.normpath(args.input_dir))
    job_name = f"{base_filename}.ctapipe-merge-runs-{args.run_number_domain[0]}-{args.run_number_domain[1]}"

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
