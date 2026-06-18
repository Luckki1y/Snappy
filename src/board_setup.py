# Initialise the board

import time 
import souk_mkid_readout
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

import paramiko

""" 
# Sanity check
snapB = s.adc_snapshot.get_snapshot()
#plt.figure(dpi=400)
plt.plot(np.arange(0,len(snapB)),snapB.real, label='I')
plt.plot(np.arange(0,len(snapB)),snapB.imag, label='Q')
plt.xlabel('Sample number')
#plt.ylabel('Normalised I/Q (unitless)')
plt.legend(loc='best')
#plt.xlim(0,100)


"""
def tone_check(client: paramiko.client.SSHClient, filename: str) -> None:
    """ This is a sanity check to ensure the tone generation is not currently running

    Args:
        client (paramiko.client.SSHClient): The ssh client to run the commands through
        filename (str): The filename for the tone check to be saved to e.g. tonecheck.png
    """
    snapshot_command = "souk_mkid_readout.adc_snapshot.get_snapshot()"
    
    single_snapshot = client.exec_command(snapshot_command)
    
    # plot the snapshot on a simple graph
    plt.plot(np.arrange(0, len(single_snapshot)), single_snapshot.real, label= "I")
    plt.plot(np.arrange(0, len(single_snapshot)), single_snapshot.imag, label= "Q")
    
    plt.xlabel("Sample Number")
    plt.legend(loc= "best")
    
    plt.savefig(filename)