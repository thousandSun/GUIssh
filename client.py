import socket

import paramiko
from scp import SCPClient


class Client:
    def __init__(self, host: str = '', username: str = '', password: str = '', port: int = 0):
        self.__host = host
        self.__username = username
        self.__password = password
        self.__port = port
        self.__local_path = None
        self.__remote_path = None
        self.__recursive = False
        self.__set_client()

    def __set_client(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__client = client

    def connect(self):
        try:
            self.__client.connect(self.__host, port=self.__port, username=self.__username,
                                  password=self.__password, timeout=5)
        except paramiko.BadHostKeyException:
            return 1
        except paramiko.AuthenticationException:
            return 2
        except paramiko.SSHException:
            return 3
        except socket.error:
            return 4
        else:
            return 0

    def run_command(self, command: str):
        return self.__client.exec_command(command)

    def set_local_path(self, local_path: str):
        self.__local_path = local_path

    def set_remote_path(self, remote_path: str):
        self.__remote_path = remote_path

    def set_recursive(self, recurse):
        self.__recursive = recurse

    def upload(self):
        # self.__client.connect(self.__host, port=self.__port, username=self.__username, password=self.__password,
        # timeout=10)
        with SCPClient(self.__client.get_transport()) as scp:
            scp.put(self.__local_path, self.__remote_path, recursive=self.__recursive)

    def download(self):
        # self.__client.connect(self.__host, port=self.__port, username=self.__username, password=self.__password,
        # timeout=10)
        with SCPClient(self.__client.get_transport()) as scp:
            scp.get(self.__remote_path, self.__local_path, recursive=self.__recursive)

    def close_client(self):
        self.__client.close()

    def get_host(self):
        return self.__host

    def get_username(self):
        return self.__username

    def get_port(self):
        return self.__port
