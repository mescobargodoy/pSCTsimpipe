pSCTsimpipe
===========

Python library for processing of `CORSIKA <https://www.iap.kit.edu/corsika/>`_ (cherenkov light) output through `sim_telarray <https://www.mpi-hd.mpg.de/hfm/~bernlohr/sim_telarray/>`__. 
The tools in this library were developed to run sim_telarray jobs through `SLURM <https://slurm.schedmd.com/documentation.html>`_ for the production of the prototype Schwarzchild-Couder Telescope (pSCT) simulations.
These tools also work for CORSIKA outputs using different telescope(s) or array configurations besides the pSCT.

To use these tools you will need to have SLURM and sim_telarray and it's dependencies installed although it is not required. These tools have been tested and used extensively at the `HummingBird <https://hummingbird.ucsc.edu/>`_ cluster in UCSC.
To install the CORSIKA and sim_telarray versions for `CTAO <https://www.ctao.org/>`_ you can go `here <https://www.mpi-hd.mpg.de/hfm/CTA/MC/Software/>`__. Note it is password protected and only for CTAO users.

There's an extra set of tools to submit multiple `ctapipe <https://github.com/cta-observatory/ctapipe>`_ jobs to SLURM. 

* Code: GitHub
* Documentation: ReadTheDocs (coming soon hopefully)
* Contact Miguel Escobar Godoy (mescob11@ucsc.edu)

Installation
=============
I recommend installing in a conda environment.

.. code-block:: bash

    pip install git+https://github.com/mescobargodoy/pSCTsimpipe.git


Usage
=====

You will need to export the path to your sim_telarray (and HESSIO optionally) installation. sim_telarray is not a required to use this repository.

.. code-block:: bash

    export SIMTELDIR=/path/to/your/sim_telarray

    export HESSIO=/path/to/your/HESSIO

To see all the available tools run

.. code-block:: bash

    psctsimpipe-tools


Each tool has it's help message. You can run

.. code-block:: bash

    <tool-name> --help

Feel free to raise any issues, bugs or any questions. Currently in development.