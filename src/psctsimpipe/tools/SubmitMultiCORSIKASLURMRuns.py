import argparse
import os

from psctsimpipe.CORSIKACommand import cd_to_corsika_dir, exe_corsika
from psctsimpipe.CORSIKACardGen import create_psct_diffuse_corsika_card
from psctsimpipe.SLURMScriptGen import create_slurm_script, submit_job

def main():
    parser = argparse.ArgumentParser(
        usage = """submit-multi-corsika-SLURM-run \\
            --run-number-domain <a> <b> \\
            --output-dir <output_dir> \\
            --particle_type <int>
            [OPTIONS]
            """,
        description="""Submit CORSIKA runs through SLURM spanning run numbers
                    given by --run-number-domain.
                    Particle type assigned using PDG ID (int) assignation.
                    1 for Gamma ray and 14 for proton for example.
                    The random module is used for the generation of a unique
                    seed (using the current system time) for the random number 
                    assignment required for the SEED parameter in CORSIKA.""",
        epilog="""Example: \n 
        submit-multi-corsika-SLURM-run 
        --run-number-domain 100000 100100
        --output-dir user/data  
        --email user@domain
        --particle_type 1
        """
        )
    # CORSIKA
    parser.add_argument(
        "--run-number-domain",
        type=int,
        nargs=2,
        help="""Submit jobs corresponding to simtel files between these
                two run numbers (inclusive)""",
        default=[100000,100010]
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
    
    move_to_corsika_dir = cd_to_corsika_dir()

    for run_number in range(args.run_number_domain[0], args.run_number_domain[1]+1):
        # Creating CORSIKA card
        corsika_card = create_psct_diffuse_corsika_card(
            run_number,
            args.output_dir,
            args.particle_type
        )

        execute_corsika = exe_corsika(corsika_card)
        job_name = f"DAT{run_number}"

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
    print("Done submitting CORSIKA runs!")

if __name__ == "__main__":
    main()