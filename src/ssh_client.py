# ssh client module

import paramiko
import re

class SSHClient():
    def __init__(self, host: str, username: str, password: str) -> None:
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
        
        # create a new ssh object
        self.client = paramiko.client.SSHClient()
        
        # set the key policy -> Should upgrade this to use keys instead of passwords
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # try to connect to the rfsoc
        try:
            self.client.connect(host,
                                username= username,
                                password= password
                                )
        
        # catch any errors
        except paramiko.SSHException as error:
            raise RuntimeError(f"An error within paramiko (SSH module occurred): {error}")
        
        except Exception as error:
            raise RuntimeError(f"An error general error occurred: {error}")
        
    def close_ssh(self) -> None:
        """ This function will close the client connection to the server and ensuring the resources are freed

        Args:
            client (object): The client object with the connection to the server
        """
        
        self.client.close()
        
    def exec_command(self, command: str, sudo_password: str = None) -> dict:
        """ This function will allow any commands to be run including the nessecairy code to catch any exceptions

        Args:
            command (str): The command to be ran
            sudo_password (str, optional): A password for a sudo command. Defaults to None.

        Returns:
            dict: A dictionary of the values returned from the command
        """
        # try to execute the command
        try:
            if sudo_password:
                _stdin, _stdout, _stderr = self.client.exec_command(command, get_pty = True)            
                
                _stdin.write(f"{sudo_password}\n")          # the password needs to be entered to run a sudo command *Note: this will also print to the CLI
                _stdin.flush()
                
            else:
                _stdin, _stdout, _stderr = self.client.exec_command(command)
        
        # catch any errors from the paramiko module
        except paramiko.SSHException as error:
            command_result = {
                "result" : False,
                "message" : "Errors caught from the ssh module",
                "stderr" : _stderr.read().decode(),
                "stdout" : _stdout.read().decode(),
                "error" : str(error)
            }
            
            return command_result
        
        # check exit code
        exit_code = _stdout.channel.recv_exit_status()
        
        if exit_code == 0:          # command ran successfully
            command_result = {
                "result" : True,
                "message" : "Command executed successfully",
                "stdout" : _stdout.read().decode(),
                "stderr" : _stderr.read().decode()
            }
            
            return command_result         # create a dictionary and return the data
        
        else:           # command failed
            command_result = {
                "result" : False,
                "message" : "Command failed after reading the stderr",
                "stderr" : _stderr.read().decode(),
                "stdout" : _stdout.read().decode()
            }
            
            return command_result
            
    # wrappers
     
    def check_connection(self) -> tuple[bool, str]:
        """ A very simple connection check by running a command to show the free ram available on the system.
    
        Returns:
            tuple [bool, str]: Wether the command was succesfully created
        """
        
        command_dict = self.exec_command("free -h")
    
        if command_dict["result"] == True:
            return (True, command_dict["stdout"])
        
        elif command_dict["result"] == False:
            return (False, command_dict["stderr"])
            
        
    def open_souk_server(self, password: str) -> tuple[bool, str, str | None]:
        """ This function will open the souk server allowing for measurements to be taken. The subroutine will also return a value which needs to be handled within the main
        code.

        Args:
            password (str): The password for the user, enabling sudo commands to be run

        Returns:
            tuple[bool, str, str | None]: This function returns TRUE for a successful souk server startup and FALSE for an exception being raised
        """
        
        command = "sudo py38/bin/souk-readout-server"
        
        command_result = self.exec_command(command, password)
        
        if command_result["result"] == True:
            return (True, command_result["message"], None)
        
        elif command_result["result"] == False:
            return (False, command_result["message"], command_result.get("error") or command_result.get("stderr"))
    
    
    def close_souk_server(self, password: str) -> tuple[bool, str, str | None]:
        """ This function closes the souk server by using the kill command with the process ID. This is achieved through first finding all processes that match a similar 
        name and then using a regex to ensure the correct one is chosen. With the process id found, the kill command can be executed, forcefully killing the souk 
        server.

        Args:
            password (str): The password for the server enabling sudo commands to be run
            
        Returns:
            tuple[bool, str, str | None]: Returns true for closing the server succesfully and false for a fail
        """
        
         # constant variables
        process_name = 'py38/bin/souk-readout-server'
        regex = '^[0-9]+ sudo py38/bin/souk-readout-server$'
        
        flag = False
        
        command_result = self.exec_command(f"pgrep -af {process_name}")
        
        output = command_result["stdout"]         # decode the byte stream into a string and create an array of the lines

        # check to see if any processes have been captured
        if not output:
            return (False, "An error has occurred while fetching the process ID. You will have to kill the souk server manually", None)
        
        # loop through each output line comparing against the regex for the correct souk process
        for line in output:
            if re.search(regex, line):
                process = line.split()          # split the line into -> 'xxxx', 'sudo', 'py38/bin/souk-readout-server'
                
                flag = True         # set a flag for error checking

        if flag == False:
            return (False, "An error has occurred while finding the correct process ID. You will have to kill the souk server manually", None)
        
        # try to convert the PID into a integer for the kill command
        try:
            PID = int(process[0])

        except ValueError as error:
            return (False, "Process could not be converted into a integer\n Process will need to be killed manually", str(error))
        
        # run the kill command
        command_result = self.exec_command(f"sudo -S -P kill -9 {PID}", password)
        
        # return the messages
        if command_result["result"] == True:
            return (True, command_result["message"], None)
        
        elif command_result["result"] == False:
            return (False, command_result["message"], command_result.get("error") or command_result.get("stderr"))
        
        