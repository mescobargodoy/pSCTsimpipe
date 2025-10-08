import os
import warnings
import textwrap
import random

def create_psct_diffuse_corsika_card(
        run_number,
        output_dir,
        particle_type,
        random_num_seed=None
    ):
    """
    Creates VERITAS+pSCT CORSIKA input card
    The naming convention is as follows:
    DAT{run_number}.telescope
    Parameters
    ----------
    run_number : int
        simulation run number
    output_dir : str
        path where CORSIKA card is stored
    particle_type : int
        Particle ID from PDG, 1 Gamma, 14 Proton,
    random_num_seed : int, by default None
        seed to initialize random number generator
        based on the random module. By default uses
        the current system time as the seed.

    """
    random.seed(random_num_seed)
    # first number in sequence 9 digits, second number is 3
    random_num_sequence_1 = random.randint(100000000,999999999), random.randint(100,999)
    random_num_sequence_2 = random.randint(100000000,999999999), random.randint(100,999)
    random_num_sequence_3 = random.randint(100000000,999999999), random.randint(100,999)
    random_num_sequence_4 = random.randint(100000000,999999999), random.randint(100,999)

    output_file = os.path.join(output_dir, f"DAT{run_number}.telescope")

    corsika_card_content = textwrap.dedent(f"""\
    * CORSIKA inputs file for VERITAS+pSCT simulations at 20 deg zenith angle.
    * Includes alternatives for different primaries (selected by pre-processor),
    * SEEDs need to be re-generated for each simulation run separately!!!
    *
    * =============== Corsika INPUTS =======================
    *
    * [ Job parameters ]
    *
    RUNNR   {run_number}                          // Number of run, to be auto-numbered by job submission
    EVTNR   1                               // Number of first shower event (usually 1)
    ESLOPE  -2.0          			// Slope of primary energy spectrum (-2.0 is equal CPU time per decade)
    *
    *
    * [ Random number generator: 4 sequences used in IACT mode ]
    *
    SEED   {random_num_sequence_1[0]}   {random_num_sequence_1[1]}   0              // Seed for 1st random number sequence, to be re-generated
    SEED   {random_num_sequence_2[0]}   {random_num_sequence_2[1]}   0              // Seed for 2nd random number sequence, to be re-generated
    SEED   {random_num_sequence_3[0]}   {random_num_sequence_3[1]}   0              // Seed for 3rd random number sequence, to be re-generated
    SEED   {random_num_sequence_4[0]}   {random_num_sequence_4[1]}   0              // Seed for 4th random number sequence, to be re-generated
    *
    *
    * [ Primary particle options ]
    *
    * PRIMARY_GAMMA
    PRMPAR  {particle_type}             // Particle type of prim. particle (1: gamma, 14: proton)
    ERANGE  100. 200.E3   // Energy range of primary particle (in GeV): proton
    NSHOW   1000          // number of showers to generate
    THETAP  20.  20.      // Range of zenith angles (degree)
    PHIP    180. 180.     // Range of azimuth angles (degree): 180 for south
    VIEWCONE 0. 10.       // Diffuse components (gammas, electrons, protons & nuclei)
    *
    *
    * [ Site specific options ]
    *
    ARRANG 10.4            // Rotation of array to north [D] (degree)
    ATMOD 1                //Atmospheric Model Selection, 1: U.S. standard atmosphere as parameterized by Linsley.
    MAGNET 25.2 40.88      // Magnetic field at assumed site [H, Z] (muT)
    ELMFLG F T             //Electromagnetic Interactions
    RADNKG 200.E2          //Radius of NKG Lateral Range
    ATMOSPHERE 61 T        //External Tabulated atmoshpere profile
    OBSLEV 1270.E2         // Observation level (in cm)
    *
    *
    * [ Core range ]
    *
    *CSCAT 10 750.E2 0.  // Use shower several times (gammas, point source only)
    CSCAT 20 833.E2 0.   // Use shower several times (protons+electrons+..., larger area for diffuse origin, same coefficient used as CTA prod3)
    *
    * [ Telescope positions, for IACT option ] 
    *
    * Generating telescope positions for VERITAS+pSCT
    TELESCOPE -23.7E2 37.6E2 0.E2 7.E2
    TELESCOPE -47.7E2 -44.1E2 4.4E2 7.E2
    TELESCOPE 60.1E2 -29.4E2 9.8E2 7.E2
    TELESCOPE 11.3E2 35.9E2 7.E2 7.E2
    TELESCOPE -8.61E2 -135.48E2 12.23E2 7.E2
    *
    *
    * [Interaction flags]
    *
    FIXCHI 0.            		 // Starting altitude (g/cm**2). 0. is at boundary to space.
    HADFLG 0 0 0 0 0 2               //HDPM Interaction Parameters & Fragmentation
    QGSJET T 0         		 //Default option, qgsjet-II-04
    QGSSIG T    			 // default option, qgsjet-II-04
    HILOW 100.          		 //Transition Energy between Models [GeV]
    ECUTS 0.30 0.05 0.02 0.02        // Energy cuts for particles
    MUADDI  F                        // Additional info for muons not needed
    MUMULT  T                        // Muon multiple scattering angle
    LONGI   T  20.  F  F             // Longit.distr. & step size & fit
    MAXPRT 20                        // Max. number of printed events
    ECTMAP 1.E5                      // Cut on gamma factor for printout
    *
    *3 following parameter are additional based on CTA prod3 simus
    FIXHEI  0.  0          // First interaction height & target (0. 0 for random)
    * STEPFC  1.0            // Mult. scattering step length factor
    *
    *
    * [ Cherenkov emission parameters ]
    *
    CERFIL  0                       // No old-style Cherenkov output to extra file
    CERSIZ  5.         		// Not above 10 for super/ultra-bialkali QE; 7 is fairly OK; 5 should be safe.
    CWAVLG 200. 700.                // Cherenkov wavelength band
    *
    * [ Debugging and output options ]
    *
    PAROUT F F              					//Table Output
    DEBUG   F  6  F  102999               				// Debug flag and logical unit for output
    DIRECT {output_dir}      //CORSIKA data written
    USER mescob11                           				//User name
    HOST HummingBird                           				//Host name
    TELFIL {output_file}  // Telescope photon bunch output (eventio format)
    *
    *
    *
    *
    *
    * [ This is the end, my friend ]
    *
    EXIT                                   // terminates input
    * ========================================================

    """)

    corsika_card = os.path.join(output_dir, f"DAT{run_number}.inp")
    with open(corsika_card, "w") as f:
        f.write(corsika_card_content)
        print(f"CORSIKA card written to {corsika_card}")

        return corsika_card