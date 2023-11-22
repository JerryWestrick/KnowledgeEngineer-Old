import csv
import http.server
import socketserver
import os
import sys
import time

# Define the templates

endpoint_template = """
; {name} ==> {email}
[{desk_no}]
type = endpoint
context = internal
auth = {desk_no}
aors = {desk_no}

[{desk_no}]
type = auth
auth_type = userpass
password = {desk_pwd}
username = {userid}

[{desk_no}]
type = aor
max_contacts = 1

[{tel_no}]
type = endpoint
context = external
auth = {tel_no}
aors = {tel_no}

[{tel_no}]
type = auth
auth_type = userpass
password = {tel_pwd}
username = {userid}

[{tel_no}]
type = aor
max_contacts = 1

"""

conf_template: str = """
[misc]
version_check_url_root=https://linphone.org/releases
log_collection_upload_server_url=
prefer_basic_chat_room=1
config-uri=file://{filename}
file_transfer_server_url=

[sip]
contact="{extension_name}" <sip:{ext}@192.168.1.88:55060>
media_encryption=none
sip_identity=sip:{ext}@18.191.115.60:55060
sip_server=sip:{ext}@18.191.115.60:55060
sip_port=55060
sip_tcp_port=55060
sip_tls_port=-1
default_proxy=0
ipv6_migration_done=1
use_ipv6=0

[rtp]
audio_rtp_port=7078
video_rtp_port=9078
text_rtp_port=11078
audio_jitt_comp=60
video_jitt_comp=60
nortp_timeout=30
audio_adaptive_jitt_comp_enabled=1
video_adaptive_jitt_comp_enabled=1

[auth_info_0]
username={ext}
userid={ext}
passwd={password}
realm=phone.shmerida.mx
domain=18.191.115.60
algorithm=md5

[proxy_0]
reg_proxy=<sip:18.191.115.60:55060;transport=udp>
reg_identity=sip:{ext}@18.191.115.60:55060
realm=phone.shmerida.mx
quality_reporting_enabled=0
"""


def generate_pjsip_sections(ext, name, secret):
    """Generate the pjsip.conf sections for the given values."""
    return (endpoint_template.format(ext=ext, name=name))


def write_to_file(filename, content):
    """Write the given content to a file."""
    with open(f'{filename}', 'w') as f:
        f.write(content)


def generate_desktop_config_file(row: dict[str, str]) -> None:
    # Generate configuration file
    x: str = row['email'].split('@')[0]
    extension_name: str = f"{x.split('.')[0]} Desktop"
    x = x.replace('.', '_')
    filename: str = f'config/{x}_desktop.conf'
    file_contents: str = conf_template.format(ext=row['desk_ext'],
                                              filename=filename,
                                              password=row['desk_pwd'],
                                              extension_name=extension_name)
    write_to_file(filename=filename, content=file_contents)


def generate_phone_config_file(row: dict[str, str]) -> None:
    # Generate configuration file
    x: str = row['email'].split('@')[0]
    extension_name: str = f"{x.split('.')[0]} Phone"
    x = x.replace('.', '_')
    filename: str = f'config/{x}_phone.conf'
    file_contents: str = conf_template.format(ext=row['tel_ext'],
                                              filename=filename,
                                              password=row['tel_pwd'],
                                              extension_name=extension_name)
    write_to_file(filename=filename, content=file_contents)


def generate_endpoints_from_csv(csv_path):
    endpoints = []

    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        row: dict[str, str]
        for row in csv_reader:
            # Generate endpoint for desk
            desk_name = f"{row['email']}s Desk"
            endpoints.append(generate_pjsip_sections(row['desk_ext'], desk_name, row['desk_pwd']))
            generate_desktop_config_file(row=row)

            # Generate endpoint for telephone
            tel_name = f"{row['email']}s Telephone"
            endpoints.append(generate_pjsip_sections(row['tel_ext'], tel_name, row['tel_pwd']))
            generate_phone_config_file(row=row)

    return "\n".join(endpoints)


def generate_from_csv(csv_file_path: str = "EmployeeTelephoneList.csv") -> None:
    # Read values from the provided CSV
    config_content = generate_endpoints_from_csv(csv_file_path)

    # Write the generated content to the desired configuration file
    config_filename = "generated_endpoints.conf"
    write_to_file(content=config_content, filename=config_filename)

    print(f"Configuration written to {config_filename}")


def start_web_server(port:int=8765, duration:int=60):
    """Starts a simple web server."""

    # Change the current working directory to the directory you want to serve
    os.chdir("config")

    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port} for {duration} seconds")

        # Serve for the specified duration
        start_time = time.time()
        httpd.timeout = 15
        while time.time() - start_time < duration:
            httpd.handle_request()


if __name__ == '__main__':
    # python shm.py generate [csv="EmployeeTelephoneList.csv"]
    if 'generate' in sys.argv:
        csv_file_path = "EmployeeTelephoneList.csv"

        # Check if 'Seconds' argument is provided
        if 'Csv=' in ' '.join(sys.argv):
            for arg in sys.argv:
                if arg.startswith('Csv='):
                    csv_file_path = arg.split('=')[1]

        generate_from_csv(csv_file_path=csv_file_path)

    # python shm.py webserver [seconds=60]
    elif 'webserver' in sys.argv:
        port = 8765
        duration = 60

        # Check if 'Seconds' argument is provided
        if 'seconds=' in ' '.join(sys.argv):
            for arg in sys.argv:
                if arg.startswith('seconds='):
                    duration = int(arg.split('=')[1])

        start_web_server(port=port, duration=duration)

    else:
        print('python shm.py generate [csv="EmployeeTelephoneList.csv"]\n'
              'python shm.py webserver [seconds=60]'
              )
