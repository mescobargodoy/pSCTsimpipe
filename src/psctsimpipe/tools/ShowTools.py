import argparse
import textwrap

def main():
    parser = argparse.ArgumentParser(
        usage = "psctsimpipe-tools",
        description="""Prints to terminal available tools
        in this package."""
        )
    available_tools = textwrap.dedent(f"""\
    You can get more information on the tool by running <toolname> --help
    submit-single-simtelarray-SLURM-run
    submit-single-psct-simtelarray-SLURM-run 
    submit-all-psct-simtelarray-SLURM-run 
    submit-multi-psct-simtelarray-SLURM-run 
    submit-simtelarray-trigger-rate-SLURM-run
    check-sim_telarray-logs-status 
    resubmit-psct-simtelarray-failed-SLURM-runs
    add-histograms
    submit-single-ctapipe-process-SLURM-run
    submit-all-ctapipe-process-SLURM-run"""
    )

    print(available_tools)

if __name__ == "__main__":
    main()