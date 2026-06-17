# SSH client

# import modules
import paramiko         # used for the ssh
import re           # used to confirm the specific souk server process

# import the server details from a separate file
from src.ssh_identities import host, username, password

def create_ssh(host, username, password):
    """ This function will create a new ssh client to a remote server using the paramaters passed and return a ssh object
        Note: This must be closed after using to ensure resources are kept to a minimal

    Args:
        host (string): The host ip address of the server in the form e.g. 192.168.100.100
        username (string): The username of the server e.g. Snappy
        password (string): The password of the server e.g. Snappy1234 {Please ensure your password is more secure}
        
    Raises:
        paramiko.ssh_exception.SSHException: This error will be raised during execution if any exceptions were caught

    Returns:
        Client (object): Returns a client object that encapsulates Parmikos session for controlling the auth, transport and channels
    """

    # create the connection
    client = paramiko.client.SSHClient()
    
    # sets the default policy as set out in the API docs
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # tries to create a connection to the server while catching any exceptions that arise
    try:
        client.connect(host, 
                       username= username, 
                       password= password
                       )
        
    except paramiko.ssh_exception.SSHException as error:
        print(f"An error has occurred within the ssh: {error}")         # TODO this could be a more exhaustive list to ensure the program is robust
        
    # return the client object for further commands / closing the ssh
    return client


def close_ssh(client):
    """ This function will close the client connection to the server and ensuring the resources are freed

    Args:
        client (object): The client object with the connection to the server
    """
    
    client.close()          # close the connection

def check_connection(client):
    """ A very simple connection check by running a command to show the free ram available on the system
    """
    # check the ssh connection 
    _stdin, _stdout, _stderr = client.exec_command("free -h")
    
    print(_stdout.read().decode())    
        

def open_souk_server(client):
    pass


def close_souk_server(client, password):
    # constant variables
    process_name = 'py38/bin/souk-readout-server'
    regex = '^[0-9]+ sudo py38/bin/souk-readout-server$'
    
    flag = False
    
    # runs a linux command to filter the current processes with the variable process name
    _stdin, _stdout, _stderr = client.exec_command(f"pgrep -af {process_name}")
    
    output = _stdout.read().decode().splitlines()           # decode the byte stream into a string and create an array of the lines
    
    # check to see if any processes have been captured
    if output is None:
        print("An error has occurred while fetching the process ID. You will have to kill the souk server manually")
        return
    
    # loop through each output line comparing against the regex for the correct souk process
    for line in output:
        if re.search(regex, line):
            process = line.split()          # split the line into -> 'xxxx', 'sudo', 'py38/bin/souk-readout-server'
            
            flag = True         # set a flag for error checking

    if flag == False:
        print("An error has occured while finding the correct process ID. You will have to kill the souk server manually")
        return
        
    # try to convert the PID into a integer for the kill command
    try:
        PID = int(process[0])

    except ValueError as error:
        # TODO this needs to produce a full error that ouptuts to the user ensuring they know the process has not been killed. This is logic error
        print(f"An error has occurred while converting the process id into a integer: {error}")
        return
    
    # run the kill command
    _stdin, _stdout, _stderr = client.exec_command(f"sudo -S -P kill -9 {PID}", get_pty= True)          # get_pty allows the command to use sudo
        
    _stdin.write(f"{password}\n")           # the password needs to be entered to run a sudo command *Note: this will also print to the CLI
    _stdin.flush()
        
    # print the output of the kill command to the user
    output = _stdout.read().decode()
    print(output)