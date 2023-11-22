import pwd
import subprocess
import socket
import os


def execute_command(command_list):
    try:
        result = subprocess.check_output(command_list, universal_newlines=True)
        return result.strip()
    except Exception as e:
        return str(e)


def resolve_domain(ip_address):
    """Resolve domain name from IP address."""
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.gaierror):  # Handling the gaierror exception as well
        return None  # No resolution


# Modifying the get_active_connections and get_listened_ports functions to handle the PID/ProgramName parsing

def get_listened_ports():
    result = execute_command(['netstat', '-tuln'])
    lines = result.split("\n")[2:]
    data = []
    for line in lines:
        parts = line.split()
        if parts:
            protocol = parts[0]
            local_address = parts[3]
            pid_program = "N/A"
            if len(parts) == 7:
                pid = parts[6].rsplit("/", 1)[0]
                program = parts[6].rsplit("/", 1)[1]
                pid_program = f"{program} ({pid})"
            data.append((protocol, local_address, pid_program))
    return data


def get_active_connections():
    result = execute_command(['netstat', '-tupn'])
    lines = result.split("\n")[2:]
    data = []
    for line in lines:
        parts = line.split()
        if parts:
            protocol = parts[0]
            local_address = parts[3]
            foreign_address = parts[4]
            pid_program = "N/A"
            if len(parts) >= 7 and "/" in parts[6]:
                pid = parts[6].rsplit("/", 1)[0]
                program = parts[6].rsplit("/", 1)[1]
                pid_program = f"{program} ({pid})"
            data.append((protocol, local_address, foreign_address, pid_program))
    return data


# The rest of the code in network_info.py remains unchanged. These are just the updated functions.

def analyze_connections(active_connections, standard_protocols):
    program_data = {}

    for connection in active_connections:
        protocol, local_addr, foreign_addr, program = connection
        local_port = int(local_addr.split(":")[-1])
        remote_host, remote_port = foreign_addr.rsplit(":", 1)
        remote_port = int(remote_port)

        domain_name = resolve_domain(remote_host)
        remote_host_info = f"{remote_host} ({domain_name})" if domain_name else remote_host

        if program not in program_data:
            program_data[program] = {
                "listening_ports": [],
                "connections": []
            }

        connection_data = {
            "local_port": local_port,
            "protocol": protocol,
            "remote_host": remote_host_info,
            "remote_port": remote_port,
            "analysis": "usual" if local_port in standard_protocols[protocol] or remote_port in standard_protocols[
                protocol] else "unusual"
        }
        program_data[program]["connections"].append(connection_data)

    return program_data


def get_process_details(pid):
    """Get details of a process given its PID using the /proc filesystem."""
    try:
        # Extracting details from /proc/[PID]/status
        with open(f"/proc/{pid}/status") as status_file:
            status_data = status_file.read()

        # Extracting UID and GID
        uid_line = [line for line in status_data.split("\n") if "Uid:" in line][0]
        uid = uid_line.split()[1]

        # Extracting User name
        user_name = None
        user_name = pwd.getpwuid(int(uid)).pw_name
        # Extracting current working directory (cwd)
        cwd = os.readlink(f"/proc/{pid}/cwd")

        # Extracting the command used to start the process
        with open(f"/proc/{pid}/cmdline", "r") as cmdline_file:
            cmd = cmdline_file.read().replace("\0", " ").strip()

        return {
            "UID": uid,
            "User": user_name if user_name else "N/A",
            "CWD": cwd,
            "Command": cmd
        }

    except:
        return {
            "UID": "N/A",
            "User": "N/A",
            "CWD": "N/A",
            "Command": "N/A"
        }


def print_color(text, color):
    """Print text in the specified color."""
    color_codes = {
        "green": "\033[92m",
        "orange": "\033[93m",
        "reset": "\033[0m"
    }
    return f"{color_codes[color]}{text}{color_codes['reset']}"


def generate_network_info():
    standard_protocols = {
        "tcp": [80, 443, 21, 22, 25, 110, 143, 3306, 5432],
        "udp": [53],
        "tcp6": [80, 443, 21, 22, 25, 110, 143, 3306, 5432],
        "udp6": [53]
    }

    active_connections = get_active_connections()
    program_analysis = analyze_connections(active_connections, standard_protocols)

    output_lines = []

    for program, data in program_analysis.items():
        pid = program.rsplit("(", 1)[-1].rsplit(")", 1)[0] if "(" in program and ")" in program else None
        details = get_process_details(pid) if pid else None

        # Program name
        output_lines.append(('P', f"Program: {program}"))

        # Program details
        if details:
            cmd_first_portion = details['Command'].split(' ', 1)[0]
            output_lines.append(('P Info',
                                 f"UID: {details['UID']}, User: {details['User']}, CWD: {details['CWD']}, Command: {cmd_first_portion}"))

        # Listening ports
        output_lines.append(('L',
                             f"Listening Ports: {', '.join([f'{port[0]} {port[1]}' for port in data['listening_ports']]) if data['listening_ports'] else 'None'}"))

        # Connections
        for connection in data["connections"]:
            conn_type = "C Usual" if connection['analysis'] == "usual" else "C Unusual"
            output_line = f"Local Port: {connection['protocol']} {connection['local_port']}, Remote Host: {connection['remote_host']}, Remote Port: {connection['protocol']} {connection['remote_port']} ({connection['analysis']})"
            output_lines.append((conn_type, output_line))

    return output_lines


def main():
    import sys
    import os

    # Colors for terminal output
    LINE_TYPE_COLOR = {
        'P': "\033[97m",  # White for 'P'
        'P Info': "\033[97m",  # White for 'P Info'
        'L': "\033[97m",  # White for 'L'
        'C Usual': "\033[92m",  # Green for 'C Usual'
        'C Unusual': "\033[93m",  # Orange for 'C Unusual'
    }
    BOX_COLOR = "\033[94m"  # Blue for box characters
    RESET = "\033[0m"

    # Get terminal width
    terminal_width = os.get_terminal_size().columns

    output = generate_network_info()

    formatted_output = []

    if "-b" in sys.argv:
        for line_type, line_content in output:
            # Format the line content to ensure it fits within the box and fills the entire width
            formatted_line = f"{BOX_COLOR}│{RESET} {LINE_TYPE_COLOR.get(line_type, '')}{line_content.ljust(terminal_width - 5)}{RESET} {BOX_COLOR}│{RESET}"

            if line_type == "P":
                if len(formatted_output) != 0:
                    formatted_output.append(f"{BOX_COLOR}└" + "─" * (terminal_width - 3) + f"┘{RESET}")
                formatted_output.append(f"{BOX_COLOR}┌" + "─" * (terminal_width - 3) + f"┐{RESET}")

            formatted_output.append(formatted_line)

        formatted_output.append(f"{BOX_COLOR}└" + "─" * (terminal_width - 3) + f"┘{RESET}")  # Use BOX_COLOR for box
    else:  # Default to -t
        for line_type, line_content in output:
            formatted_line = f"{LINE_TYPE_COLOR.get(line_type, '')}{line_content}{RESET}"
            formatted_output.append(formatted_line)

    # Print the formatted output
    for line in formatted_output:
        print(line)


if __name__ == "__main__":
    main()
