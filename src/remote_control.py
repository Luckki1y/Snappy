# Initialise the board

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

import paramiko
import json

class RemoteControl:
    def __init__(self, client: paramiko.client.SSHClient, configfile: str) -> None:
        
        command = f"cd Snappy/src/remote && python remote.py --c {configfile}"
        
        try:
            self._stdin, self._stdout, self._stderr = client.exec_command(command)
        except paramiko.ssh_exception.SSHException:
            raise RuntimeError("An error occurred running the python remote server")
        
        response = json.loads(self._stdout.readline())
        
        # check the json for any errors and output to the cli
        if response["status"] != "ready":           
            print(response["data"])
            raise RuntimeError()            # exit the program
        
    def tone_check(self, filename: str) -> None:
        """ This is a sanity check to ensure the tone generation is not currently running

        Args:
            self (object): The ssh connection to the other program
            filename (str): The filename for the tone check to be saved to e.g. tonecheck.png
        """
        
        command = {
            "command" : "sanity-check"
        }
        
        # write the command to the cli for the remote program to read
        self._stdin.write(f"{json.dumps(command)} \n")
        self._stdin.flush()
        
        # read the json response and save in a variable
        response = json.loads(self._stdout.read())
        
        # catch any errors thrown
        if response["status"] != "ready":           
            print(response["data"])
            raise RuntimeError()  
        
        single_snapshot = response["snapshot"]
        
        # plot the snapshot on a simple graph
        plt.plot(np.arange(0, len(single_snapshot)), single_snapshot.real, label= "I")
        plt.plot(np.arange(0, len(single_snapshot)), single_snapshot.imag, label= "Q")
        
        plt.xlabel("Sample Number")
        plt.legend(loc= "best")
        
        plt.savefig(filename)           # saves to your local computer
    
    def full_snapshot(self, n: int, samples: int, filename: str) -> None:
        """_summary_

        Args:
            n (int): _description_
            samples (int): _description_
            filename (str): _description_
        """
        
        command = {
            "command" : "full-snapshot",
            "n" : n,
            "samples" : samples,
            "filename" : filename
        }
        
        # write the command to the cli for the remote program to read
        self._stdin.write(f"{json.dumps(command)} \n")
        self._stdin.flush()
        
        # read the json response
        response = json.loads(self._stdout.read())
        
         # catch any errors thrown
        if response["status"] != "ready":           
            print(response["data"])
            raise RuntimeError()  
        
        # full snapshot has run successfully
        print(f"A full snapshot has been successful, it will be saved in this directory as {filename}")
            
    def kill(self) -> None:
        """_summary_
        """
        command = {
            "command" : "kill"
        }
        
        self._stdin.write(f"{json.dumps(command)} \n")
        self._stdin.flush()
        
        # read the json response
        response = json.loads(self._stdout.read())
        
        # error catcher
        if response["status"] != "killed":
            print("Please kill the remote python environment yourself")
            print(response["data"])
            raise RuntimeError() 
            
        # process has been killed successfully
        print("The remote python script has been successfully killed")
            