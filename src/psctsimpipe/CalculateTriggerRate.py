import pandas as pd
import numpy as np
import h5py
import astropy.units as u
import importlib.resources
from scipy.interpolate import CubicSpline

# NSB functions 

def count_phrase_in_file(file_path: str, phrase: str) -> int:
    """
    Counts the number of times a specific phrase appears in a file.

    Parameters
    ----------
    file_path : str
        The path to the file to be searched.
    phrase : str
        The phrase to search for.

    Returns
    -------
    int
        The number of times the phrase appears in the file.
    """  
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content.count(phrase)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return -1
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1
    
def calculate_NSB_trigger_rate(file_path, 
                               time_window_per_pix, 
                               n_events
                               ):
    """
    Calculates NSB trigger rate by counting the number
    of "has triggered" lines in a sim_telarray log file.
    The time window is given by fadc_bins_per_pix*n_events

    Parameters
    ----------
    file_path : str
        The path to the file to be searched.
    time_window_per_pix : float
        Assummed to be in ns.
        Time covered by waveform.
        For instance for 100 samples, 1 ns per sample,
        the time window is 100 ns. 
    n_events : int
        Number of events simulated.
        Required for calculating the total time window
        per run which is given by 
        n_events*time_window_per_pix


    Returns
    -------
    float
        trigger rate [Hz]
        triggered_events/n_events*time_window_per_pix*1e-9 Hz
    """    

    triggered_events = count_phrase_in_file(file_path, "has triggered!")

    time_window = n_events*time_window_per_pix*1e-9 # Converting from ns to second

    trigger_rate = triggered_events/time_window # Hz

    return trigger_rate


# Proton trigger rate functions

def cone_solid_angle(theta):
    """
    Compute solid angle

    Parameters
    ----------
    theta : float
        angle cone in degrees
    """    
    theta=theta*np.pi/180
    solid_angle = 2*np.pi*(1-np.cos(theta))
    return solid_angle


def powlaw_integral(E1,E2,gamma=2.0, E_0=1.0):
    """
    Integral of power law

    Parameters
    ----------
    E1 : float
        lower energy bound
    E2 : float
        upper energy bound
    gamma : float, optional
        power law index, by default 2.0
    E_0 : float, optional
        pivot energy, by default 1.0
    """    
    
    numerator = (E1*E2**gamma-E2*E1**gamma)*E_0**gamma
    denominator = (E1**gamma)*(E2**gamma)*(gamma-1)

    return numerator/denominator

def read_histo_output(input_histo_output):
    """

    Parameters
    ----------
    input_histo_output : _type_
        _description_
    """    
    temp_data = pd.read_csv(
        input_histo_output, 
        sep='\t', 
        names=['LogE', 'N_frac', 'N_trigg', 'N_total'], 
        na_values=['*'], 
        skiprows=10
        )
    
    data = temp_data.dropna()

    return data


def read_DAMPE_flux(input_table):
    """
    Used to read in cosmic proton flux
    measured by DAMPE stored in
    psctsimpipe/data/

    Parameters
    ----------
    input_table : string
        table with proton fluxes
        as measured by DAMPE
    """    
    columns = ["E",         # ith energy bin center
               "Emin",      # ith lower energy bin edge
               "Emax",      # ith upper energy bin edge
               "F_invGeV_invsqmeter_inversec_invsr", 
               "F_err_stat", 
               "F_err_ana", 
               "F_err_had"
               ]

    temp_data = pd.read_csv(
        input_table, 
        sep='\s+',
        # delim_whitespace=True, # will be deprecated in future versions
        names=columns,
        dtype=float,
        skiprows=1
        )
    
    data = temp_data.dropna()

    return data

def interpolated_DAMPE_flux(Energy):
    """
    Will return a flux value for a given energy
    by interpolating the DAMPE flux measurements.
    Expected units are
    Energy [=] TeV
    Flux [=]  TeV^-1 m^-2 sr^-1 s^-1

    Parameters
    ----------
    Energy : array like
        Energy values in TeV
    
    Returns
    ----------
        numpy.array
    """

    with importlib.resources.open_binary("psctsimpipe.data", "DAMPE_proton_flux.txt") as f:
        data = read_DAMPE_flux(f)   
        DAMPE_energy = data["E"]/1000 # GeV to TeV
        DAMPE_flux = data['F_invGeV_invsqmeter_inversec_invsr']*1000 #GeV^-1 to TeV^-1 m^-2 sr^-1 s^-1

        # Interpolate in log space since relationship is linear
        logE = np.log10(DAMPE_energy)
        logF = np.log10(DAMPE_flux)
        interpolated_flux = CubicSpline(logE,logF)

        input_logE = np.log10(Energy)
        log_interp_flux = interpolated_flux(input_logE)
        # Convert back to linear space
        interp_flux = (10**log_interp_flux)*(u.m**(-2))*(u.sr**(-1))*(u.s**(-1))*(u.TeV**(-1))

        return interp_flux


def display_DAMPE_flux():
    """
    Displays the information contained in 
    psctsimpipe/data/DAMPE_proton_flux.txt
    """
    with importlib.resources.open_binary("psctsimpipe.data", "DAMPE_proton_flux.txt") as f:
        data = read_DAMPE_flux(f)    
        print("The DAMPE flux table reads as follows: \n")
        print(data.to_string())


def return_DAMPE_flux_table():
    """
    Returns the information contained in 
    psctsimpipe/data/DAMPE_proton_flux.txt
    in a pandas dataframe
    """
    with importlib.resources.open_binary("psctsimpipe.data", "DAMPE_proton_flux.txt") as f:
        data = read_DAMPE_flux(f)   
        return data
    
def calculate_proton_trigger_rate(input_file,
                           area=np.pi*(833)**2,
                           solid_angle=cone_solid_angle(10),
                        ):
    """
    Calculates trigger rate doing the following:
    Effective Area * Solid Angle * Flux * Energy-bin width

    Parameters
    ----------
    input_file : string
        Output of division of histogram 1007/1006
        y projection. In other words
        Triggered/Number-of-total-events
    area : float, optional
        area over which events were generated, by default np.pi*(833)**2
    solid_angle : float, optional
        solid angle over which events were generated, by default cone_solid_angle(10)
    Returns
    -------
    float
        trigger rate in units of Hz
    """    
    data = read_histo_output(input_file)

    deltaE=0.05

    logE = data["LogE"]
    Elow = u.TeV*10**(logE-deltaE/2)
    Ehigh = u.TeV*10**(logE+deltaE/2)
    E_bin_widths = Ehigh-Elow

    interp_flux = interpolated_DAMPE_flux(10**logE)

    trigger_rate_per_Ebin = (area*(u.m**2))*data["N_frac"]*(solid_angle*u.sr)*interp_flux*E_bin_widths

    total_trigger_rate = np.sum(trigger_rate_per_Ebin)

    return total_trigger_rate

def proton_trigger_rate_pdtable(input_file,
                              area=np.pi*(833)**2,
                              solid_angle=cone_solid_angle(10),
                              ):
    """
    Returns a pandas data frame with the
    trigger rate per energy bin as well as
    other useful parameters listed below:
    Energy bin center, edges, assumed flux
    trigger rate.

    It assumes the units used in sim_telarray.

    Parameters
    ----------
    input_file : string
        Output of division of histogram 1007/1006
        y projection. In other words
        Triggered/Number-of-total-events
    area : float, optional
        area over which events were generated, by default np.pi*(833)**2
    solid_angle : float, optional
        solid angle over which events were generated, by default cone_solid_angle(10)


    Returns
    -------
    pandas.dataframe

    """
    data = read_histo_output(input_file)

    deltaE=0.05

    logE = data["LogE"]
    Energy = u.TeV*10**logE

    Elow = u.TeV*10**(logE-deltaE/2)
    Ehigh = u.TeV*10**(logE+deltaE/2)
    E_bin_widths = Ehigh-Elow
    
    interp_flux = interpolated_DAMPE_flux(10**logE)
    integral_flux = E_bin_widths*interp_flux
    
    trigger_rate_per_Ebin = (area*(u.m**2))*data["N_frac"]*(solid_angle*u.sr)*integral_flux
    Aeff = (area*(u.m**2))*data["N_frac"]*(solid_angle*u.sr)
    
    N_frac = data['N_frac']
    N_trigg = data['N_trigg']
    N_total = data['N_total']


    table_dict = {
        "flux": interp_flux,
        "integral_flux": integral_flux,
        "Energy": Energy,
        "low_Ebin_edge":Elow,
        "high_Ebin_edge": Ehigh,
        "trigger_rate": trigger_rate_per_Ebin,
        "Aeff": Aeff,
        "N_frac": N_frac,
        "N_triggered": N_trigg,
        "N_total": N_total,
    }

    trigger_rate_table = pd.DataFrame(table_dict)
    
    print("The units for the table area:")    
    print("flux [=] TeV^-1 m^-2 sr^-1 s^-1")
    print("integral_flux [=] m^-2 sr^-1 s^-1")
    print("Energy [=] TeV")
    print("low_Ebin_edge [=] TeV")
    print("high_Ebin_edge [=] TeV")
    print("trigger_rate [=] Hz")
    print("Aeff [=] m^2 sr")
    print("N_frac [=] unitless")
    print("N_triggered [=] events")
    print("N_total [=] events")

    return trigger_rate_table

def proton_trigger_rate_to_hdf5(input_file,
                                output_file,
                              area=np.pi*(833)**2,
                              solid_angle=cone_solid_angle(10)
                              ):
    """
    Returns a pandas data frame with the
    trigger rate per energy bin as well as
    other useful parameters listed below:
    Energy bin center, edges, assumed flux
    trigger rate.

    It assumes the units used in sim_telarray.

    Parameters
    ----------
    input_file : string
        Output of division of histogram 1007/1006
        y projection. In other words
        Triggered/Number-of-total-events
    area : float, optional
        area over which events were generated, by default np.pi*(833)**2
    solid_angle : float, optional
        solid angle over which events were generated, by default cone_solid_angle(10)


    Returns
    -------
    hdf5 file

    """
    data = read_histo_output(input_file)

    deltaE=0.05

    logE = data["LogE"]
    Energy = u.TeV*10**logE

    Elow = u.TeV*10**(logE-deltaE/2)
    Ehigh = u.TeV*10**(logE+deltaE/2)
    E_bin_widths = Ehigh-Elow
    
    interp_flux = interpolated_DAMPE_flux(10**logE)
    integral_flux = E_bin_widths*interp_flux
    
    trigger_rate_per_Ebin = (area*(u.m**2))*data["N_frac"]*(solid_angle*u.sr)*integral_flux
    Aeff = (area*(u.m**2))*data["N_frac"]*(solid_angle*u.sr)
    
    N_frac = data['N_frac']
    N_trigg = data['N_trigg']
    N_total = data['N_total']

    with h5py.File(output_file, 'w') as f:
        f.create_dataset("flux", data=interp_flux)
        f.create_dataset("integral_flux", data=integral_flux)
        f.create_dataset("Energy", data=Energy)
        f.create_dataset("low_Ebin_edge", Elow)
        f.create_dataset("high_Ebin_edge", Ehigh)
        f.create_dataset("trigger_rate", trigger_rate_per_Ebin)
        f.create_dataset("Aeff", Aeff)
        f.create_dataset("N_frac", N_frac)
        f.create_dataset("N_trigg", N_trigg)
        f.create_dataset("N_total", N_total)



# def calculate_proton_trigger_rate(input_file,
#                            area=np.pi*(833)**2,
#                            solid_angle=cone_solid_angle(10),
#                            gamma=2.6
#                         ):
#     """

#     Parameters
#     ----------
#     input_file : string
#         Output of division of histogram 1007/1006
#         y projection. In other words
#         Triggered/Number-of-total-events
#     area : float, optional
#         area over which events were generated, by default np.pi*(833)**2
#     solid_angle : float, optional
#         solid angle over which events were generated, by default cone_solid_angle(10)
#     gamma : float, optional
#         spectral index, by default 2.6

#     Returns
#     -------
#     tuple
#         trigger rate and associated error
#     """    
#     data = read_histo_output(input_file)

#     deltaE=0.05
    
#     with importlib.resources.open_binary("pSCTsimpipe.data", "DAMPE_proton_flux.txt") as f:
#         flux_table = read_DAMPE_flux(f)
#     # flux_table = read_DAMPE_flux("/hb/home/mescob11/sct/pSCT_trigger_rate/DAMPE_cr_flux.txt")
#         DAMPE_emin = flux_table['Emin']/1000. # GeV to TeV
#         DAMPE_emax = flux_table['Emax']/1000. # GeV to TeV
#         DAMPE_flux = flux_table['F_invGeV_invsqmeter_inversec_invsr']*1000 #GeV^-1 to TeV^-1 m^-2 sr^-1 s^-1
    
#     integral = []

#     for logE in data['LogE']:
#         tempE = 10**logE

#         for elow,ehigh,flux in zip(DAMPE_emin,DAMPE_emax,DAMPE_flux):

#             # if tel Energy is between DAMPE energy bin
#             # multiply power law integral by corresponding
#             # flux
#             if elow <= tempE < ehigh:
                
#                 int_flux_per_Ebin = powlaw_integral(
#                     10**(logE-deltaE/2),
#                     10**(logE+deltaE/2),
#                     gamma=gamma,
#                     E_0=np.sqrt((10**(logE-deltaE/2))*(10**(logE+deltaE/2)))
#                     )
                
#                 integral.append(int_flux_per_Ebin*flux)

#                 break

#             # if tel Energy is lower than lowest DAMPE 
#             # # energy bin multuply power law integral
#             # by flux corresponding to lowest DAMPE
#             # energy bin
#             elif tempE<=DAMPE_emin.iloc[0]:

#                 int_flux_per_Ebin = powlaw_integral(
#                     10**(logE-deltaE),
#                     10**logE,
#                     gamma=gamma,
#                     E_0=np.sqrt((10**(logE-deltaE/2))*(10**(logE+deltaE/2)))
#                     )
#                 # zeroth index corresponds to lowest energy bin flux
#                 integral.append(int_flux_per_Ebin*DAMPE_flux.iloc[0])

#                 break

#             # if tel Energy is higher than highest DAMPE 
#             # energy bin multiply power law integral
#             # by flux corresponding to highest DAMPE
#             # energy bin
#             elif tempE>=DAMPE_emax.iloc[-1]:

#                 int_flux_per_Ebin = powlaw_integral(
#                     10**(logE-deltaE),
#                     10**logE,
#                     gamma=gamma,
#                     E_0=np.sqrt((10**(logE-deltaE/2))*(10**(logE+deltaE/2)))
#                     )
#                 # last index corresponds to highest energy bin flux
#                 integral.append(int_flux_per_Ebin*DAMPE_flux.iloc[-1])

#                 break
        
#     integral = np.array(integral)

#     N_frac = data['N_frac']
#     N_error = np.sqrt(data['N_trigg'])
    
#     trigger_rate_per_bin = area*solid_angle*integral*N_frac
#     trigger_rate_error_per_bin = area*solid_angle*integral*N_error

#     trigger_rate = np.sum(trigger_rate_per_bin)
#     trigger_rate_err = np.sqrt(1/np.sum(1/trigger_rate_error_per_bin**2))

#     return trigger_rate,trigger_rate_err

# def proton_trigger_rate_table(input_file,
#                            area=np.pi*(833)**2,
#                            solid_angle=cone_solid_angle(10),
#                            gamma=2.6
#                         ):
#     """

#     Parameters
#     ----------
#     input_file : string
#         Output of division of histogram 1007/1006
#         y projection. In other words
#         Triggered/Number-of-total-events
#     area : float, optional
#         area over which events were generated, by default np.pi*(833)**2
#     solid_angle : float, optional
#         solid angle over which events were generated, by default cone_solid_angle(10)
#     gamma : float, optional
#         spectral index, by default 2.6

#     Returns
#     -------
#     tuple
#         trigger rate and associated error
#     """    
#     data = read_histo_output(input_file)

#     deltaE=0.05
    
#     with importlib.resources.open_binary("pSCTsimpipe.data", "DAMPE_proton_flux.txt") as f:
#         flux_table = read_DAMPE_flux(f)
#     # flux_table = read_DAMPE_flux("/hb/home/mescob11/sct/pSCT_trigger_rate/DAMPE_cr_flux.txt")
#         DAMPE_emin = flux_table['Emin']/1000. # GeV to TeV
#         DAMPE_emax = flux_table['Emax']/1000. # GeV to TeV
#         DAMPE_flux = flux_table['F_invGeV_invsqmeter_inversec_invsr']*1000 #GeV^-1 to TeV^-1 m^-2 sr^-1 s^-1
    
#     integral = []
#     Flux = []
#     Energy = []
#     Elow = []
#     Ehigh = []

#     for logE in data['LogE']:
#         tempE = 10**logE

#         for elow,ehigh,flux in zip(DAMPE_emin,DAMPE_emax,DAMPE_flux):

#             # if tel Energy is between DAMPE energy bin
#             # multiply power law integral by corresponding
#             # flux
#             if elow <= tempE < ehigh:
                
#                 int_flux_per_Ebin = powlaw_integral(
#                     10**(logE-deltaE/2),
#                     10**(logE+deltaE/2),
#                     gamma=gamma,
#                     E_0=np.sqrt((10**(logE-deltaE/2))*(10**(logE+deltaE/2)))
#                     )
#                 integral.append(int_flux_per_Ebin*flux)

#                 break

#             # if tel Energy is lower than lowest DAMPE 
#             # # energy bin multuply power law integral
#             # by flux corresponding to lowest DAMPE
#             # energy bin
#             elif tempE<=DAMPE_emin.iloc[0]:

#                 int_flux_per_Ebin = powlaw_integral(
#                     10**(logE-deltaE),
#                     10**logE,
#                     gamma=gamma,
#                     E_0=np.sqrt((10**(logE-deltaE/2))*(10**(logE+deltaE/2)))
#                     )
#                 # zeroth index corresponds to lowest energy bin flux
#                 integral.append(int_flux_per_Ebin*DAMPE_flux.iloc[0])

#                 break

#             # if tel Energy is higher than highest DAMPE 
#             # energy bin multiply power law integral
#             # by flux corresponding to highest DAMPE
#             # energy bin
#             elif tempE>=DAMPE_emax.iloc[-1]:

#                 int_flux_per_Ebin = powlaw_integral(
#                     10**(logE-deltaE),
#                     10**logE,
#                     gamma=gamma,
#                     E_0=np.sqrt((10**(logE-deltaE/2))*(10**(logE+deltaE/2)))
#                     )
#                 # last index corresponds to highest energy bin flux
#                 integral.append(int_flux_per_Ebin*DAMPE_flux.iloc[-1])

#                 break
        
#     integral = np.array(integral)
#     Energy = 10**data['LogE']
#     Elow = 10**(data['LogE']-deltaE)
#     Ehigh = 10**(data['LogE']+deltaE)
#     Aeff = (area*(u.m**2))*data["N_frac"]*(solid_angle*u.sr)
#     trigger_rate_per_Ebin = Aeff*integral
    
#     N_frac = data['N_frac']
#     N_trigg = data['N_trigg']
#     N_total = data['N_total']


#     table_dict = {
#         "flux": Flux,
#         "integral_flux": integral,
#         "Energy": Energy,
#         "low_Ebin_edge":Elow,
#         "high_Ebin_edge": Ehigh,
#         "trigger_rate": trigger_rate_per_Ebin,
#         "Aeff": Aeff,
#         "N_frac": N_frac,
#         "N_triggered": N_trigg,
#         "N_total": N_total,
#     }

#     trigger_rate_table = pd.DataFrame(table_dict)
    
#     print("The units for the table area:")    
#     print("flux [=] TeV^-1 m^-2 sr^-1 s^-1")
#     print("integral_flux [=] m^-2 sr^-1 s^-1")
#     print("Energy [=] TeV")
#     print("low_Ebin_edge [=] TeV")
#     print("high_Ebin_edge [=] TeV")
#     print("trigger_rate [=] Hz")
#     print("Aeff [=] m^2 sr")
#     print("N_frac [=] unitless")
#     print("N_triggered [=] events")
#     print("N_total [=] events")

#     return trigger_rate_table