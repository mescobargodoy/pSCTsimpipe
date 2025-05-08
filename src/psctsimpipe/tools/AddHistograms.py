import argparse
import subprocess

from psctsimpipe.HESSioAddHistograms import add_histograms

def main():
    """
    Add histograms tool from HESSio library
    """

    parser = argparse.ArgumentParser(
        usage = """add-histograms \\
            --input-dir <input_dir> \\
            --output <output.hdata.gz>
            """,
        description="""Adds all the hdata.gz
        files in a directory and stores result
        int output""",
        )
    parser.add_argument(
        "--input-dir",
        help="Directory where hdata.gz files live."
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path for output file"
    )
    args = parser.parse_args()

    add_histo_command = add_histograms(
                            args.input_dir,
                            args.output
                        )
    
    subprocess.run(add_histo_command, check=True)

if __name__ == "__main__":
    main()