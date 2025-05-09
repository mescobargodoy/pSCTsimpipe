import os
import argparse
import textwrap
import subprocess

from psctsimpipe.pSCTSimTelArrayRun import single_sim_telarray_pSCT_run
from psctsimpipe.SLURMScriptGen import create_slurm_script, submit_job
from psctsimpipe.CheckSimTelArrayLogs import extract_simtel_run_params
from psctsimpipe.Helpers import extract_number

def main():
    parser = argparse.ArgumentParser(
        usage = """resubmit-psct-simtelarray-failed-SLURM-runs --input-dir <inputdir> \\
            [OPTIONS]
            """,
        description="Resubmit all failed sim_telarray runs in a directory through SLRUM.",
        epilog="""Example: \n 
        resubmit-psct-simtelarray-failed-SLURM-runs 
        --iput-dir /your/sim_telarray/output_dir
        --email email@domain
        """
        )
    
    # sim_telarray options
    parser.add_argument(
        "--input-dir",
        help="path to directory"
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

    failed_runs = extract_simtel_run_params(args.input_dir)
    resubmitted_run = 0
    for run in failed_runs:

        config_file=run["config_file"]
        histogram_output=run["histogram_output"]
        event_output=run["event_output"]
        corsika_input=run["corsika_input"]
        output_dir=run["output_dir"]
        log_file=run["log_file"]
        std_err_file=run["std_err_file"]
        slurm_script=run["slurm_script"]
        particle_type=run["particle_type"]
        ze=run["ze"]
        az=run["az"]
        telescope_name=run["telescope_name"]
        height=run["height"]
        night_type=run["night_type"]
        NSB=run["NSB"]

        # Deleting files associated to failed run        
        print(textwrap.dedent(f"""
            Deleting the following files:
            {log_file}
            {std_err_file}
            {slurm_script}
            {histogram_output}
            {event_output}""")
            )

        subprocess.run([
            "rm", 
            log_file, 
            std_err_file, 
            slurm_script, 
            event_output, 
            histogram_output
            ])

        # Creating sim_telarray command
        command = single_sim_telarray_pSCT_run(
            corsika_input,
            output_dir,
            config_file,
            particle_type,
            ze,
            az,
            NSB,
            height,
            telescope_name,
            night_type
            )

        red_CORISKA_input = os.path.basename(corsika_input)
        run_num = extract_number(red_CORISKA_input)
        job_name = f"{particle_type}{run_num}"        

        # creating SLURM script
        script_path = create_slurm_script(
            job_name, 
            command, 
            args.email, 
            output_dir, 
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

        # Submitting job to queue
        submit_job(script_path)
        print(f"Job submitted! SLURM script: {script_path}")
        resubmitted_run+=1
    print(f"\n{resubmitted_run} runs were resubmitted.")

if __name__ == "__main__":
    main()