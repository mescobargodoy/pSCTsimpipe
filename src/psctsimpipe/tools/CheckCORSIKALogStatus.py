import argparse

from psctsimpipe.CheckSimTelArrayLogs import check_corsika_log_files

def main():
    """
    Checks whehter a sim_telarray run was successful
    or not. Status is printed out to terminal. 
    """    
    parser = argparse.ArgumentParser(
        usage = """check-corsika-logs-status \\
            --input-dir <input_dir> \\
            """,
        description="""Checks for corsika logs to see
        if  ========== END OF RUN ================================================.
        is in file.""",
        epilog="""Example: \n 
        check-corsika-logs-status 
        --input-dir /your/corsika/output_dir 
        """
        )
    
    parser.add_argument(
        "--input-dir",
        help="path to directory where all CORSIKA files live."
    )

    args = parser.parse_args()

    check_corsika_log_files(args.input_dir)

if __name__ == "__main__":
    main()