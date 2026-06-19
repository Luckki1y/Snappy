#
# package imports
import sshclient
import ssh_identities

import tone_generation
from remote_control import RemoteControl

# import modules
import argparse

def arg_parser():
    """
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--board_config_file", "--sc",
        type= str,
        default= "souk-single-pipeline-4x2.yaml",
        help= "The config file for the souk mkid readout module to setup the server"
    )
    parser.add_argument(
        "--local_config_file", "--lc",
        type= str,
        default= "qubit.yamal",
        help= "The config file for the souk readout tools module"
    )
    parser.add_argument(
        "--clock_setting", "--c",
        type= str,
        default= "internal",
        choices= ["internal", "external"],
        help= "The clock setting for the RFSoc, this can be the internal 12MHz or an external 10MHz clock. You need to input 'internal' or 'external'"
    )
    parser.add_argument(
        "--frequency", "--f",
        type= float,
        default= 4e9,
        help= "The frequency of the wave generated e.g. 4e9"
    )
    parser.add_argument(
        "--phase", "--p",
        type= float,
        default= 0.0,
        help= "The phase of the wave generated e.g. "         # TODO add the phase e.g.
    )
    parser.add_argument(
        "--amplitude", "--a",
        type= float,
        default= 1.0,
        help= "The amplitude of the wave generated. This should range from 0 to 1 with 0 being off and 1 being on"
    )
    parser.add_argument(
        "--n",
        type= int,
        default= 7500,
        help= ""            # TODO add the help section
    )
    parser.add_argument(
        "--samples", "--s",
        type= int,
        default= 4500,
        help= ""            # TODO add the help section
    )
    parser.arg_argument(
        "--single_snapshot_filename", "--ssfn",
        type= str,
        default= "SanityCheck.png",
        help= "The file name for a figure created by the program to ensure no signal is currently running"
    )
    parser.add_argument(
        "--full_snapshot_filename", "--fsfn",
        required= True,
        type= str,
        help= "The file name for the full snapshot being run to be saved as. This typically should be a .npy extension"
    )
    
    return parser

def main(args, host, username, password):
    
    # create the SSHs
    print("Creating SSH's")
    server_client = sshclient.create_ssh(host, username, password)          # souk server ssh
    tools_client = sshclient.create_ssh(host, username, password)           # tools ssh
    
    # create the remote control instance, initializing the board
    print("Initialsing the board")
    tools_control = RemoteControl(tools_client, f"{args.board_config_file}")
    
    # complete a sanity check
    print("Completing a sanity check")
    tools_control.tone_check(f"{args.single_snapshot_filename}")
    
    # ensure the user wishes to continue
    response = input("Sanity check has been completed and saved as {args.single_snapshot_filename}. Please respond with Yes to continue")
    if response not in ["Yes", "yes", "Y", "y"]:
        print("Starting shutdown sequence")
        # close remote python instance
        tools_control.kill()
        
        # close the souk server
        sshclient.close_souk_server(tools_client, password)
        
        # close both ssh connections
        sshclient.close_ssh(tools_client)
        sshclient.close_ssh(server_client)
        print("Program exiting")
        return
    
    # start the souk readout server
    print("Start the souk readout server")
    souk_server_flag = sshclient.open_souk_server(server_client, password)
    if souk_server_flag == False:            # the server has errored out, exiting the program
        return
    
    # setup the RFSoc board for tone generation
    print("Setting up the RFSoc for tone generation")
    c = tone_generation.setup_config(f"{args.local_config_file}", f"{args.clock_setting}")
    
    # start the tone generation
    print("Starting tone generation")
    tone_generation.generate_tone(c, args.frequency, args.phase, args.amplitude)
    
    # complete a full snapshot
    print("Completing a full snapshot")
    tools_control.full_snapshot(args.n, args.sample, f"{args.full_snapshot_filename}")
    
    # cli info 
    print("Stopping all process and shutting down")
    
    # stop any tone currently being generated
    tone_generation.generate_tone(c, args.frequency, args.phase, 0)
    
    # close remote python instance
    tools_control.kill()
    
    # close the souk server
    sshclient.close_souk_server(tools_client, password)
    
    # close both ssh connections
    sshclient.close_ssh(tools_client)
    sshclient.close_ssh(server_client)

# Main program
if __name__ == "__main__":
    # gather the arguments
    args = arg_parser()
    
    # ssh variables
    host, username, password = ssh_identities.host, ssh_identities.username, ssh_identities.password
    
    main(args, host, username, password)
    
    
    