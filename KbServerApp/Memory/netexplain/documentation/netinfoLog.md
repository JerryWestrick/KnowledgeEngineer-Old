Log of Step: netinfo : netexplain/prompts/netinfo.pe


 - I have generated the code for the `netinfo.py` program. Here is the code:

```python
import os
import socket
import subprocess

def get_program_info(pid):
    program_info = {}
    
    # Get program name
    try:
        program_info['name'] = os.path.basename(os.readlink(f'/proc/{pid}/exe'))
    except FileNotFoundError:
        program_info['name'] = 'Unknown'
    
    # Get program UID and username
    try:
        uid = os.stat(f'/proc/{pid}').st_uid
        program_info['uid'] = uid
        program_info['user'] = os.getpwuid(uid).pw_name
    except FileNotFoundError:
        program_info['uid'] = 'Unknown'
        program_info['user'] = 'Unknown'
    
    # Get program current working directory
    try:
        program_info['cwd'] = os.readlink(f'/proc/{pid}/cwd')
    except FileNotFoundError:
        program_info['cwd'] = 'Unknown'
    
    # Get program command
    try:
        with open(f'/proc/{pid}/cmdline', 'rb') as f:
            cmdline = f.read().decode().split('\x00')
            program_info['command'] = cmdline[0]
    except FileNotFoundError:
        program_info['command'] = 'Unknown'
    
    return program_info

def get_protocol_name(protocol):
    protocol_names = {
        socket.IPPROTO_TCP: 'tcp',
        socket.IPPROTO_UDP: 'udp',
        socket.IPPROTO_ICMP: 'icmp',
        socket.IPPROTO_IGMP: 'igmp',
        socket.IPPROTO_RAW: 'raw',
        socket.IPPROTO_IPV6: 'ipv6',
        socket.IPPROTO_GRE: 'gre',
        socket.IPPROTO_ESP: 'esp',
        socket.IPPROTO_AH: 'ah',
        socket.IPPROTO_ICMPV6: 'icmpv6',
        socket.IPPROTO_NONE: 'none'
    }
    return protocol_names.get(protocol, 'unknown')

def get_host_name(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return ip

def get_port_status(port):
    if port == 'None':
        return 'None'
    elif port == 'Unusual':
        return 'Unusual'
    elif port.isdigit():
        return 'Normal'
    else:
        return 'Unknown'

def get_network_info():
    network_info = []
    
    # Get list of all processes
    processes = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    
    for pid in processes:
        program_info = get_program_info(pid)
        
        # Get program listening ports
        listening_ports = []
        try:
            with open(f'/proc/{pid}/net/tcp', 'r') as f:
                for line in f.readlines()[1:]:
                    parts = line.split()
                    local_address = parts[1].split(':')[1]
                    local_port = int(local_address, 16)
                    listening_ports.append(local_port)
        except FileNotFoundError:
            pass
        
        try:
            with open(f'/proc/{pid}/net/tcp6', 'r') as f:
                for line in f.readlines()[1:]:
                    parts = line.split()
                    local_address = parts[1].split(':')[1]
                    local_port = int(local_address, 16)
                    listening_ports.append(local_port)
        except FileNotFoundError:
            pass
        
        # Get program connections
        connections = []
        try:
            output = subprocess.check_output(['ss', '-p', '-n', 'state', 'established', 'pid', f'pid={pid}'])
            lines = output.decode().split('\n')[1:-1]
            for line in lines:
                parts = line.split()
                local_address = parts[4].split(':')[0]
                local_port = int(parts[4].split(':')[1])
                remote_address = parts[5].split(':')[0]
                remote_port = int(parts[5].split(':')[1])
                protocol = get_protocol_name(int(parts[1]))
                connections.append({
                    'lport': f'{protocol} {local_port}',
                    'rhost': remote_address,
                    'rport': f'{protocol} {remote_port}'
                })
        except subprocess.CalledProcessError:
            pass
        
        # Resolve host names
        for connection in connections:
            connection['rhost'] = get_host_name(connection['rhost'])
        
        # Determine port status
        for connection in connections:
            connection['status'] = get_port_status(connection['rport'])
        
        program_info['listening_ports'] = listening_ports
        program_info['connections'] = connections
        
        network_info.append(program_info)
    
    return network_info

def print_network_info(network_info):
    for program_info in network_info:
        print(f"Program {program_info['name']} ({program_info['pid']})")
        print(f"UID: {program_info['uid']}, User: {program_info['user']}, CWD: {program_info['cwd']}, Command: {program_info['command']}")
        print("Listening Ports:")
        if len(program_info['listening_ports']) == 0:
            print("None")
        else:
            for port in program_info['listening_ports']:
                print(f"lport: {port}  rhost: None  rport: None")
        print("Connections:")
        if len(program_info['connections']) == 0:
            print("None")
        else:
            for connection in program_info['connections']:
                print(f"lport: {connection['lport']}  rhost: {connection['rhost']}  rport: {connection['rport']}  {connection['status']}")
        print()

if __name__ == '__main__':
    network_info = get_network_info()
    print_network_info(network_info)
```

I have also checked the code for syntax errors and there are no errors. I have written the code to the file `netexplain/code/netinfo.py`.