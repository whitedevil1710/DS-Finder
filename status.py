import cmd
import requests
from termcolor import colored
from tqdm import tqdm
import subprocess
import socket
import argcomplete
import argparse
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import sys
import csv
from termcolor import colored

def animate_banner(text):
    colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']
    delay = 0.001

    for i in range(len(banner)):
        char = banner[i]
        color = colors[i % len(colors)]
        colored_char = colored(char, color, attrs=['bold'])
        print(colored_char, end='', flush=True)
        time.sleep(delay)

    print()

banner = """
██████╗ ███████╗      ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗ 
██╔══██╗██╔════╝      ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
██║  ██║███████╗█████╗█████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
██║  ██║╚════██║╚════╝██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
██████╔╝███████║      ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║
╚═════╝ ╚══════╝      ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
--------------c̶o̶d̶e̶d̶ b̶y̶ w̶h̶i̶t̶e̶d̶e̶v̶i̶l̶----------------------------------                                                                 
"""

animate_banner(banner)


class MyCmd(cmd.Cmd):
    prompt = colored(">>>>", "blue")

    def __init__(self):
        super().__init__()
        self.ip = []
        self.status = []
        self.domain = []
        self.errors = []
        self.default_filename = "output.csv" 

    def do_quit(self, arg):
        return True


    def help_find_status(self):
        print("Detailed help for find_status command:")
        print("Usage: find_status")
        print("Description: This command finds the status codes for each IP address.")
        print("")

    def help_print_status(self):
        print("Detailed help for print_status command:")
        print("Usage: print_status")
        print("Description: This command prints the list of IP addresses and their corresponding status codes.")
        print("")

    def help_save_status(self):
        print("Detailed help for save_status command:")
        print("Usage: save_status [filename]")
        print("Description: This command saves the IP addresses and their corresponding status codes into a CSV file.")
        print("If [filename] is not provided, a default file name will be used.")
        print("")


    def help_quit(self):
        print("Detailed help for quit command:")
        print("Usage: quit")
        print("Description: This command exits the program.")
        print("")
        
    def help_cls(self):
        print("Detailed help for cls command:")
        print("Usage: cls")
        print("Description: This command clears the IP, status, and domain lists.")
        print("")

    def help_print(self):
        print("Detailed help for print command:")
        print("Usage: print")
        print("Description: This command prints the list of IP addresses and their corresponding status codes.")
        print("")

    def help_print_ip(self):
        print("Detailed help for print_ip command:")
        print("Usage: print_ip")
        print("Description: This command prints the list of IP addresses.")
        print("")

    def help_read(self):
        print("Detailed help for read command:")
        print("Usage: read <filename>")
        print("Description: This command reads IP addresses from the specified file and adds them to the IP list.")
        print("")
        

    def do_save_status(self, arg):
        filename = arg.strip()
        if not filename:
            filename = self.default_filename

        try:
            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["IP", "Status Code"])
                for ip, status in zip(self.ip, self.status):
                    writer.writerow([ip, status])
            print(colored(f"[+] Status codes saved to '{filename}'","green"))
        except IOError as e:
            print(colored(f"Error saving status codes: {str(e)}","red"))

    def check_port(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0

    def find_status_code(self, ip):
        if self.check_port(ip, 443):
            url = "https://" + ip + ":443"
        elif self.check_port(ip, 80):
            url = "http://" + ip + ":80"
        else:
            return "X"

        try:
            response = requests.get(url, timeout=2, verify=False)
            return response.status_code
        except requests.exceptions.RequestException:
            return "X"

    def do_find_status(self, arg):
        try:
            with tqdm(total=len(self.ip), desc=colored("Finding Status Codes", "yellow"),
                      unit=colored("IP", "cyan"), ncols=80, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
                for i in self.ip:
                    status = self.find_status_code(i)
                    self.status.append(status)
                    pbar.update(1)
        except Exception as e:
            self.errors.append(str(e))

    def do_print_status(self, args):
        try:
            print(colored("[+] FOUND STATUS CODES", "yellow"))
            print("-" * 50)
            print(",".join(map(str, self.status)))
        except IndexError:
            print(colored("[!] Error: No Status codes found yet :(", "red"))

    def do_print(self, args):
        try:
            print(colored("[+] STATUS CODE AND IP LIST", "yellow"))
            print("-" * 50)
            for ip, status in zip(self.ip, self.status):
                print(colored(ip, "cyan") + " : " + colored(str(status), "magenta"))
        except IndexError:
            print(colored("[!] Error: No IP and Status codes found yet :(", "red"))

    def do_print_ip(self, arg):
        try:
            print(colored("[+] IPs FOUND", "yellow"))
            print("-" * 50)
            print(",".join(self.ip))
        except IndexError:
            print(colored("[!] Error: No IPs found yet :(", "red"))

    def do_read(self, line):
        filename = line.strip()
        try:
            with open(filename, "r") as f:
                print(colored(f"[+] Reading file: {filename}", "green"))
                lines = [line.rstrip('\n') for line in f]
                self.ip.extend(lines)
        except FileNotFoundError:
            self.errors.append("File not found!")

    def complete_read(self, text, line, begidx, endidx):
        current_dir = os.getcwd()
        files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))]
        return [f for f in files if f.startswith(text)]

    def do_cls(self, arg):
        self.ip = []
        self.status = []
        self.domain = []
        self.errors = []
        print(colored("[+] Cleared IP, status, domain, and errors", "yellow"))

    def default(self, line):
        try:
            subprocess.run(line, shell=True, check=True)
        except FileNotFoundError:
            print(colored(f"Command not found: {line}", "red"))
        except KeyboardInterrupt:
            print(colored("\n[!] Execution interrupted by user", "red"))
        except Exception as e:
            self.errors.append(str(e))

    def postcmd(self, stop, line):
        if self.errors:
            print(colored("[!] Exception Errors:", "red"))
            print("-" * 50)
            for error in self.errors:
                print(colored(error, "red"))
            self.errors = []

        return stop


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        argcomplete.autocomplete(parser)
        MyCmd().cmdloop()
    except KeyboardInterrupt:
        print(colored("[!] User Interrupt", "red"))
    except Exception as e:
        print(colored(f"[!] Error: {str(e)}", "red"))

