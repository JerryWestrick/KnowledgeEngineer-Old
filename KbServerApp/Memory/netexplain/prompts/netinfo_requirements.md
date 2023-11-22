# netinfo.py 
netinof.py is a program that gathers network information about the current state of the network.

The idea is to present information about what the computer is doing on the network in a way the user can easily understand.

For each program that is currently using the network show:
```
Program chrome (3674)  
UID: 1000, User: jerry, CWD: /home/jerry, Command: /opt/google/chrome/chrome 
Listening Ports:  None 
lport: tcp 45176  rhost: 65.8.178.50 (server-65-8-178-50.mia3.r.cloudfront.net) rport: tcp 443 (https) Normal
lport: tcp6 60200 rhost: 2607:f8b0:4012:820:                                    rport: tcp6 443 (https)Normal
lport: tcp 38398  rhost: 142.250.113.188 (rs-in-f188.1e100.net)                 rport: tcp 5228        Unusual
```

Comments: 
- The Command is large only show the actual program full path.
- all ports should also show the protocol names where possible.
- All hosts should have the names resolved if possible
- Unusual is a port usage that does not conform with the standard protocol.

