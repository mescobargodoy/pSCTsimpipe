import os
import warnings
import textwrap
import subprocess

def create_slurm_script(
        job_name,  
        program,
        email="", 
        output_dir=".", 
        mem="8G", 
        n_nodes=1, 
        n_tasks=1,
        cpus_per_task=1, 
        t_exp="2:00:00",
        partition="128x24",
        qos='',
        account='',
        mail_type='FAIL,END'
        ):
    """
    Generates a SLURM script.

    Parameters
    ----------
    job_name : string
        Name for job (shows when running squeue)
    email : string
        Where to send mail
    program : string
        command to submit to queue
    output_dir : str, optional
        where SLURM will send command-line output/error, by default "."
    mem : str, optional
        Amount of RAM to allocate per-task, by default "8G"
    n_nodes : int, optional
        Number of nodes requested, by default 1
    n_tasks : int, optional
        Number of tasks to run, by default 1
    cpus_per_task : int, optional
        Number of CPU cores to use per task, by default 1
    t_exp : str, optional
        Max time for job to run, by default "2:00:00"
    partition : str, optional
        Which queue the job should run on, by default "128x24"
        VERITAS/SCT node is "lab-afurniss"
    qos : str, optional
        Required to target VERITAS/SCT HB node.
        Set it to "g-veritas" if this is the case 
    account : str, optional,
        Required to target VERITAS/SCT HB node.
        Set it to "g-veritas" if this is the case
    mail_type : str, optional
        Mail events (one or more of NONE,BEGIN,END,FAIL,ALL), by default 'FAIL,END'

    Returns
    -------
    string containing path to slurm script that was just created

    """    
    # output_dir where SLURM will send command-line output/error
    if not os.path.exists(output_dir):
        warnings.warn(f"Directory '{output_dir}' does not exist. It will be created.", UserWarning)
        os.makedirs(output_dir, exist_ok=True)
    
    standard_output = os.path.join(output_dir, "%x_%j.out")
    standard_error = os.path.join(output_dir, "%x_%j.error")

    script_content = textwrap.dedent(f"""\
    #!/bin/bash 
    #SBATCH --job-name={job_name}
    #SBATCH --mail-user={email} 
    #SBATCH --mail-type={mail_type} 
    #SBATCH --nodes={n_nodes}
    #SBATCH --ntasks={n_tasks}
    #SBATCH --cpus-per-task={cpus_per_task}   
    #SBATCH --time={t_exp}
    #SBATCH --mem={mem}
    #SBATCH --partition={partition}
    #SBATCH --qos={qos}
    #SBATCH --account={account} 
    #SBATCH --output={standard_output}
    #SBATCH --error={standard_error}

    module load gnu13 
    module load gsl
    {program}
    """)

    script_path = os.path.join(output_dir, f"{job_name}.slurm")
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
        return script_path


def create_supp_slurm_script(
        job_name,  
        program,
        email="", 
        output_dir=".", 
        mem="8G", 
        n_nodes=1, 
        n_tasks=1,
        cpus_per_task=1, 
        t_exp="2:00:00",
        partition="128x24",
        qos='',
        account='',
        mail_type='FAIL,END'
        ):
    """
    Generates a SLURM script where standard
    output/error SLURM files are suppressed.

    Parameters
    ----------
    job_name : string
        Name for job (shows when running squeue)
    email : string
        Where to send mail
    program : string
        command to submit to queue
    output_dir : str, optional
        where SLURM will send command-line output/error, by default "."
    mem : str, optional
        Amount of RAM to allocate per-task, by default "8G"
    n_nodes : int, optional
        Number of nodes requested, by default 1
    n_tasks : int, optional
        Number of tasks to run, by default 1
    cpus_per_task : int, optional
        Number of CPU cores to use per task, by default 1
    t_exp : str, optional
        Max time for job to run, by default "2:00:00"
    partition : str, optional
        Which queue the job should run on, by default "128x24"
    qos : str, optional
        Required to target VERITAS/SCT HB node.
        Set it to "g-veritas" if this is the case 
    account : str, optional,
        Required to target VERITAS/SCT HB node.
        Set it to "g-veritas" if this is the case
    mail_type : str, optional
        Mail events (one or more of NONE,BEGIN,END,FAIL,ALL), by default 'FAIL,END'

    Returns
    -------
    string containing path to slurm script that was just created

    """    
    # output_dir where SLURM will send command-line output/error
    if not os.path.exists(output_dir):
        warnings.warn(f"Directory '{output_dir}' does not exist. It will be created.", UserWarning)
        os.makedirs(output_dir, exist_ok=True)
    
    script_content = textwrap.dedent(f"""\
    #!/bin/bash 
    #SBATCH --job-name={job_name}
    #SBATCH --mail-user={email} 
    #SBATCH --mail-type={mail_type} 
    #SBATCH --nodes={n_nodes}
    #SBATCH --ntasks={n_tasks}
    #SBATCH --cpus-per-task={cpus_per_task}   
    #SBATCH --time={t_exp}
    #SBATCH --mem={mem}
    #SBATCH --partition={partition}
    #SBATCH --qos={qos}
    #SBATCH --account={account} 
    #SBATCH --output=/dev/null
    #SBATCH --error=/dev/null

    module load gnu13 
    module load gsl
    {program}
    """)

    script_path = os.path.join(output_dir, f"{job_name}.slurm")
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
        return script_path


def create_ctapipe_slurm_script(
        job_name,  
        program,
        email="", 
        output_dir=".", 
        mem="8G", 
        n_nodes=1, 
        n_tasks=1,
        cpus_per_task=1, 
        t_exp="2:00:00",
        partition="128x24",
        qos='',
        account='',
        mail_type='FAIL,END'
        ):
    """
    Generates a SLURM script for ctapipe.

    Parameters
    ----------
    job_name : string
        Name for job (shows when running squeue)
    email : string
        Where to send mail
    program : string
        command to submit to queue
    output_dir : str, optional
        where SLURM will send command-line output/error, by default "."
    mem : str, optional
        Amount of RAM to allocate per-task, by default "8G"
    n_nodes : int, optional
        Number of nodes requested, by default 1
    n_tasks : int, optional
        Number of tasks to run, by default 1
    cpus_per_task : int, optional
        Number of CPU cores to use per task, by default 1
    t_exp : str, optional
        Max time for job to run, by default "2:00:00"
    partition : str, optional
        Which queue the job should run on, by default "128x24"
    qos : str, optional
        Required to target VERITAS/SCT HB node.
        Set it to "g-veritas" if this is the case 
    account : str, optional,
        Required to target VERITAS/SCT HB node.
        Set it to "g-veritas" if this is the case
    mail_type : str, optional
        Mail events (one or more of NONE,BEGIN,END,FAIL,ALL), by default 'FAIL,END'

    Returns
    -------
    string containing path to slurm script that was just created with
    ctapipe required modules loaded

    """    
    # output_dir where SLURM will send command-line output/error
    if not os.path.exists(output_dir):
        warnings.warn(f"Directory '{output_dir}' does not exist. It will be created.", UserWarning)
        os.makedirs(output_dir, exist_ok=True)
    
    standard_output = os.path.join(output_dir, "%x_%j.out")
    standard_error = os.path.join(output_dir, "%x_%j.error")

    script_content = textwrap.dedent(f"""\
    #!/bin/bash 
    #SBATCH --job-name={job_name}
    #SBATCH --mail-user={email} 
    #SBATCH --mail-type={mail_type} 
    #SBATCH --nodes={n_nodes}
    #SBATCH --ntasks={n_tasks}
    #SBATCH --cpus-per-task={cpus_per_task}   
    #SBATCH --time={t_exp}
    #SBATCH --mem={mem}
    #SBATCH --partition={partition}
    #SBATCH --qos={qos}
    #SBATCH --account={account} 
    #SBATCH --output={standard_output}
    #SBATCH --error={standard_error}

    module load miniconda3 
    conda activate ctapipe
    {program}
    """)

    script_path = os.path.join(output_dir, f"{job_name}.slurm")
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
        return script_path


def submit_job(script_path):
    """
    Submit job to queue.

    Parameters
    ----------
    script_path : string
        path to SLURM script
    """    
    # os.system(f"sbatch {script_path}")
    subprocess.run(["sbatch", script_path])
