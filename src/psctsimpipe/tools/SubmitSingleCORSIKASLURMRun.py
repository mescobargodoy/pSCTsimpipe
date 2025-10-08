import argparse
import os

from psctsimpipe.CORSIKACommand import cd_to_corsika_dir, exe_corsika
from psctsimpipe.CORSIKACardGen import create_psct_diffuse_corsika_card
from psctsimpipe.SLURMScriptGen import create_slurm_script, submit_job


def main():
    parser = argparse.ArgumentParser(
        usage = """submit-single-corsika-SLURM-run \\
            --run_number 103000 \\
            --output-dir <output_dir> \\
            --random_num_seed <int> \\
            [OPTIONS]
            """,
        description="""Submit CORSIKA run through SLURM""",
        epilog="""Example: \n 
        submit-single-corsika-SLURM-run 
        --run_number 103000
        --output-dir user/data  
        --email user@domain
        --random_num_seed 1012312
        """
        )
    # CORSIKA
    parser.add_argument(
        "--run_number",
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
        "--particle_type",
        help="""Particle type to be simulated.
                1 for gamma, 14 proton, ..."""
    )
    parser.add_argument(
        "--random_num_seed",
        default=None,
        help="Number to initialize random number generator. Default is current system time"
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

    # Creating CORSIKA card
    corsika_card = create_psct_diffuse_corsika_card(
        args.run_number,
        args.output_dir,
        args.random_num_seed
    )

    move_to_corsika_dir = cd_to_corsika_dir()
    execute_corsika = exe_corsika(
        corsika_card,
        args.particle_type
        )

    job_name = f"DAT{args.run_number}"

    program = f"""
    {move_to_corsika_dir}
    {execute_corsika}
    """

    script_path = create_slurm_script(
        job_name, 
        program,
        None,
        None,
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

if __name__ == "__main__":
    main()