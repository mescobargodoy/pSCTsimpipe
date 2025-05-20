import argparse
import os

from psctsimpipe.pSCTSimTelArrayRun import single_sim_telarray_pSCT_run
from psctsimpipe.SLURMScriptGen import create_slurm_script, submit_job
from psctsimpipe.Helpers import extract_number, find_files


def main():
    parser = argparse.ArgumentParser(
        usage = """submit-multi-psct-simtelarray-SLURM-run \\
            --input-dir <input_dir> \\
            --output-dir <output_dir> \\
            --search-pattern <pattern> \\
            --run-number-domain a b \\
            --sim_telarray_cfg <cfg> \\
            [OPTIONS]
            """,
        description="Submit multiple sim_telarray runs through SLRUM.",
        epilog="""Example: \n 
        submit-multi-psct-simtelarray-SLURM-run
        --input-dir ~CORSIKA/Gamma_Z20 
        --output-dir miguel/data  
        --search-pattern *telescope.tar.gz
        --run-number-domain 100000 100100
        --sim_telarray_cfg pSCT.cfg 
        """
        )
    
    # sim_telarray options
    parser.add_argument(
        "--input-dir",
        help="path to directory where all CORSIKA files live."
    )
    parser.add_argument(
        "--output-dir",
        help="""path for simtelarray outputs, 
                commandline standrd output and error files,
                and slurm scripts.
                """
    )
    parser.add_argument(
        "--run-number-domain",
        type=int,
        nargs=2,
        help="""Submit jobs corresponding to CORSIKA files between these
                two run numbers (inclusive)""",
        default=[100000,100100]
    )
    parser.add_argument(
        "--search-pattern",
        default="*telescope.tar.gz",
        help="path to directory where all CORSIKA files live."
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

    corsika_files = find_files(args.input_dir,args.search_pattern)

    print(f"{len(corsika_files)} files ending with {args.search_pattern} found in {args.input_dir}")

    for corsika_f in corsika_files:
        
        red_CORISKA_input = os.path.basename(corsika_f)
        run_num = extract_number(red_CORISKA_input)
        job_name = f"{args.particle_type}{run_num}"
        
        low_run_num_edge=int(args.run_number_domain[0])
        high_run_num_edge=int(args.run_number_domain[1])
        
        if low_run_num_edge <= int(run_num) <= high_run_num_edge:

            command = single_sim_telarray_pSCT_run(
                corsika_f,
                args.output_dir,
                args.sim_telarray_cfg,
                args.particle_type,
                args.ze,
                args.az,
                args.NSB,
                args.height,
                args.telescope_name,
                args.night_type
                )
        
            script_path = create_slurm_script(
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