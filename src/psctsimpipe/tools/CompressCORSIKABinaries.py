import argparse
import subprocess
import os

from psctsimpipe.Helpers import find_files

def main():
    parser = argparse.ArgumentParser(
        usage = """compress-corsika-binaries \\
            --input-dir <input_dir> \\
            --file-ext <ext>
            --output-dir <output_dir>
            """,
        description="""Tool to compress CORSIKA binaries in 
        a given directory using tar.
        """,
        epilog="""Example: \n 
         compress-corsika-binaries
        --input-dir /your/corsika/binaries/directory
        --file-ext telescope
        --output-dir my/directory/
        """
        )
    parser.add_argument(
        "--input-dir",
        help="path to directory where all CORSIKA files live."
    )
    parser.add_argument(
        "--file-ext",
        default="telescope",
        help="File extension of sim_telarray output to be searched for"
    )
    parser.add_argument(
        "--output-dir",
        help="""path for ctapipe-process outputs, 
                commandline standard output and error files,
                and slurm scripts.
            """
    )

    args = parser.parse_args()

    files_to_compress = find_files(
        args.input_dir,
        search_pattern=f"*{args.file_ext}"
    )

    print(f"Found {len(files_to_compress)} *{args.file_ext} files in {args.input_dir} to be compressed.")

    for binary in files_to_compress:
        
        basename = os.path.basename(binary)
        output_file = os.path.join(args.output_dir, f"{basename}.tar.gz")
    
        print(f"Compressing file {basename}")
    
        subprocess.run(['tar', '-C', f"{args.input_dir}", '-czvf', f'{output_file}', basename])
    
        print(f"Compressed file written to {output_file}")
    
    print("Done with CORSIKA binaries compression!")

if __name__ == "__main__":
    main()