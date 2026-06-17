# Tone Generation

import souk_readout_tools

def setup_config(configfile: str, clock_source: str):
    """ This function allows the user to setup a board using a config file and determine wether to use a internal or external clock 
    
    Args:
        configfile (str): The config file used to setup the board e.g. 'qubit.yamal'
        clock_source (str): This is a string to determine the clock source of either the 12MHz internal or a 10MHz external clock e.g. 'internal'
        
    """
    # create a new souk readout client as c
    c = souk_readout_tools.client.ReadoutClient(config_file= configfile)
    
    # change the clock setting
    c.config['firmware']['clock_source'] = clock_source
    
    return c

def generate_tone(c, frequency: float, phase: float, amplitude: float) -> None:
    """ This function allows the user to generate a new tone from the given parameters from the RFSoc
    
    Important:
        This must only be ran after the souk server is running. This function will not work if the server is not running

    Args:
        c (_type_): This is the client for the souk readout tools
        frequency (float): This is the frequency for the tone e.g. 4e9
        phase (float): This is the phase for the tone e.g. 0
        amplitude (float): This is the amplitude for the tone where typically 0 is off and 1 is on
    """
    # set the frequency and phase
    c.set_tone_frequencies(frequency)
    c.set_tone_phases(phase)
    
    # set the amplitude
    c.set_tone_amplitudes(amplitude)