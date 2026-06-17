# SSH client

# import modules
import paramiko

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


def close_souk_server(client):
    # run a command to pull the relevant process ids
    # strip the data that is pulled to its relevant parts
    # kill the process id 
    
    # runs a linux command to filter the current processes with "readout-server"
    _stdin, _stdout, _stderr = client.exec_command("ps aux | grep readout-server")
    
    # 
