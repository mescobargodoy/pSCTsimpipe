# pSCTsimpipe
Python library for processing of [CORSIKA](https://www.iap.kit.edu/corsika/) (cherenkov light) output through [sim_telarray](https://www.mpi-hd.mpg.de/hfm/~bernlohr/sim_telarray/). 
The tools in this library were developed to run sim_telarray jobs through [SLURM](https://slurm.schedmd.com/documentation.html) for the production of the prototype Schwarzchild-Couder Telescope (pSCT) simulations.
These tools also work for CORSIKA outputs using different telescope(s) or array configurations besides the pSCT.

To use these tools you will need to have SLURM and sim_telarray and it's dependencies installed. These tools have been tested and used extensively at the [HummingBird](https://hummingbird.ucsc.edu/) cluster in UCSC.
To install the CORSIKA and sim_telarray versions for [CTAO](https://www.ctao.org/) you can go [here](https://www.mpi-hd.mpg.de/hfm/CTA/MC/Software/). Note it is password protected and only for CTAO users.

* Code: GitHub
* Documentation: ReadTheDocs
* Contact Miguel Escobar Godoy (mescob11@ucsc.edu)

## Installation
```
pip install git+<inster GitHub URL here>
```

## Usage
You will need to export the path to your sim_telarray (and HESSIO optionally) installation.
```
export SIMTELDIR=/path/to/your/sim_telarray
export HESSIO=/path/to/your/HESSIO
```

To see all the available tools run
```
psctsimpipe-tools
```

Each tool has it's help message. You can run
```
<tool-name> --help
```

The documentation is hosted at ReadTheDocs

Feel free to raise any issues, bugs or any questions.
