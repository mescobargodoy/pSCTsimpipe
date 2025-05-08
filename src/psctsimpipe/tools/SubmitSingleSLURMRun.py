import argparse

from psctsimpipe.SingleSimTelArrayRun import single_sim_telarray_run
from psctsimpipe.SLURMScriptGen import create_slurm_script, submit_job


def main():
    parser = argparse.ArgumentParser(
        usage = """submit-single-simtelarray-SLURM-run -i <CORSIKA> \\
            [OPTIONS] \\   
            -o <output> \\ 
            -hist <histo> \\ 
            --sim_telarray_cfg <cfg> \\
            --job-name <job_name> \\
            --email <myemail@domain> \\
            """,
        description="Submit a single sim_telarray run through SLRUM.",
        epilog="""Example: \n 
        submit-single-simtelarray-SLURM-run 
        -i telescope.tar.gz 
        -o gamma.simtel.gz  
        -hist histogram.hdata.gz 
        --sim_telarray_cfg pSCT.cfg 
        --job-name gamma10000 
        --email myemail@domain 
        """
        )
    
    # sim_telarray options
    parser.add_argument(
        "-i",
        "--CORSIKA_input",
        help="path to CORSIKA file"
    )
    parser.add_argument(
        "-o",
        "--output_eventio",
        help="path for output eventio"
    )
    parser.add_argument(
        "-hist",
        "--output_histo",
        help="path for output histogram"
    )
    parser.add_argument(
        "-c",
        "--sim_telarray_cfg",
        help="path to sim_telarray config file"
    )

    # SLURM options
    parser.add_argument(
        "--job-name", 
        required=True, 
        help="Job/SLURM-file name (shows when running squeue)"
        )
    parser.add_argument(
        "--email", 
        default="",
        help="Email for job notifications"
        )
    parser.add_argument(
        "--output-dir", 
        default=".", 
        help="Directory to store commandline standrd output and error files"
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

    command = single_sim_telarray_run(
        args.CORSIKA_input,
        args.output_eventio,
        args.output_histo,
        args.sim_telarray_cfg
    )
    
    script_path = create_slurm_script(
        args.job_name, 
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