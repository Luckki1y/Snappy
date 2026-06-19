# This is a remote 'server' that should stay active on a ssh channel to allow python to be consistently available for commands

# import for the souk tools
import souk_mkid_readout
import json
import numpy as np
import argparse

import sys

def arg_parser():
    """ Setup the arg parser to collect the config file on setup

    Returns:
        parser: The cli interface
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--configfile", "--c",
        type= str,
        default= "souk-single-pipeline-4x2.yaml",
        help= "The config file for the souk mkid readout to setup"
    )
    
    return parser.parse_args()
    

# once first run setup the initial board configurations
def setup(config_file: str):
    try:
        # setup the board
        s = souk_mkid_readout.SoukMkidReadout('localhost', configfile= config_file)
        
        s.program()
        
        s.initialize()
        
        s.fpga.print_status()
        
        s.fpga.get_fpga_clock() * 8
        
        # create a json to return to the main program
        json_dump = {
            "status" : "ready"
        }
        
    except Exception as error:
        # if an error occurs loading the board settings, print the json to the cli and raise a error to stop the python program
        json_dump = {
            "status" : "error",
            "data" : str(error)
        }
        
        print(json.dumps(json_dump))
        raise RuntimeError
        
    return s, json_dump
    
def sanity_check(s):
    """ This command will perform a sanity check by taking a single snapshot and outputting back to the cli to be collected by _stdout
    
    Args:
        s (object): This is the souk mkid readout object created from initializing the board
    
    Returns:
        json: The json to be returned to the main cli for checking the process occurred correctly
    """
    # take the snapshot
    snapshot = s.adc_snapshot.get_snapshot()
                
    # create the json 
    json_dump = {
        "status" : "ready",
        "snapshot" : snapshot
    }
                
    return json_dump

def full_snapshot(s, n: int, samples: int, filename: str):
    """ Creates a full snapshot of n x samples saved as filename. This function creates an empty array and using a loop takes a snapshot for each index assinging to the 
        empty array. After the entire array has been iterated through the data is saved as a 2d array.

    Args:
        s (object): This is the souk mkid readout object created from initializing the board
        n (int): The number of snapshots to take
        samples (int): The number of samples per n
        filename (str): The name of the file to be saved as

    Returns:
        json: The json to be returned to the main cli for checking the process occurred correctly
    """
    
    # create a new empty snapshot array that is n x samples    
    snapshot_array = np.empty((n, samples), dtype= complex)
                
    # for each index of the array, capture a snapshot
    for i in range(n):
        snapshot = s.adc_snapshot.get_snapshot()
        snapshot_array[i] = snapshot.real + 1j * snapshot.imag
                
    #
    snapshot_array_unrav = snapshot_array.ravel()
    
    # saves the data as {filename} provided by the user
    np.save(f"{filename}", 
            np.c_[snapshot_array_unrav.real, snapshot_array_unrav.imag] 
            )
    
    # create a json file to output back to the main program
    json_dump = {
        "status" : "ready"
    }
    
    return json_dump
                
def persistent_server(s):
    """ This is a persistent server that will be launched from the main program. Using this, commands can be passed back and forward to compelete any actions that
        need to be completed specifically on the RFSoc
        
        Args:
            s (object): This is the souk mkid readout object created from initalising the board
    """
    
    while True:
        try:
            # fetch the input and load the command
            line = input()
            
            request = json.loads(line)
            
            command = request["command"]
            
            # sanity check command from the main program
            if command == "sanity-check":
                json_dump = sanity_check(s)         # perform the command
                
                # package as a json and output to the cli to be collected by the ssh client
                print(json.dumps(json_dump))
                
            # full snapshot command from the main program
            elif command == "full-snapshot":  
                json_dump = full_snapshot(s, request["n"], request["samples"], request["filename"])          # perform the command
                
                # package as a json and output to the cli to be collected by the ssh client
                print(json.dumps(json_dump))
                
            # any new commands can be added as
            # elif command = "..."
            #   ...
                
            
            # kill command from the main program 
            elif command == "kill":
                json_dump = {
                    "status" : "killed"
                }
                
                print(json.dumps(json_dump))
                
                # kill the process
                sys.exit()
                
                
        # catch any exceptions, package as a json and print to the cli for the ssh client to catch
        except Exception as error:
            json_dump = {
                "status" : "error",
                "error" : str(error)
            }
            
            print(json.dumps(json_dump))         # output the json to be collected

# main
if __name__ == "__main__":
    
    args = arg_parser()
    
    config_file = args.configfile
    
    # setup the board
    s, json_dump = setup(config_file)
    
    
    # create the persistent server
    persistent_server(s)