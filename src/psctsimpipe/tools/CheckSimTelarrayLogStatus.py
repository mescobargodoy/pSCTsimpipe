import argparse

from psctsimpipe.CheckSimTelArrayLogs import check_simtelarray_log_files

def main():
    """
    Checks whehter a sim_telarray run was successful
    or not. Status is printed out to terminal. 
    """    
    parser = argparse.ArgumentParser(
        usage = """check-sim_telarray-logs-status \\
            --input-dir <input_dir> \\
            """,
        description="""Checks for sim_telarray logs to see
        if Sim_telarray finished successfully.""",
        epilog="""Example: \n 
        check-logs-run-status 
        --input-dir /your/sim_telarray/output_dir 
        """
        )
    
    parser.add_argument(
        "--input-dir",
        help="path to directory where all sim_telarray files live."
    )

    args = parser.parse_args()

    check_simtelarray_log_files(args.input_dir)

if __name__ == "__main__":
    main()