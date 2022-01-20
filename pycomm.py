#! python3
# This is a script to capture some data from a machine and then send it to influx database.
# This program written in Python 3.9
# This program only works with InfluxDBv2 (v1 'InfluxDBClient' will not work)

import influxdb_client  # type: ignore
from influxdb_client.client.write_api import SYNCHRONOUS  # type: ignore
import os 
import subprocess 
import platform
# the above 'type: ignore' comment ignores mypy error

# CONFIGURE - establishing variables to use later
#
#
username = os.environ.get('user')
password = os.environ.get('token')
token = os.environ.get('INFLUX_TOKEN')
bucket = 'pybucket'
org = 'org1'
influx_instance = 'http://192.168.1.250:8086'  # the influxdb server

# influxdb_client takes three named parameters: url, org, and token
# write_api method configures the writer object
client = influxdb_client.InfluxDBClient(url=influx_instance, token=token, org=org,)
write_api = client.write_api(write_options=SYNCHRONOUS)


# INPUT DATA - capture data
#
#
# ip_list = {
#     'rPiNetCont': '192.168.1.203',
#     'rPieKids': '192.168.1.247',
# }


def ping(host_or_ip, packets=1, timeout=1000):
    ''' Calls system "ping" command, returns True if ping succeeds.
    Required parameter: host_or_ip (str, address of host to ping)
    Optional parameters: packets (int, number of retries), timeout (int, ms to wait for response)
    Does not show any output, either as popup window or in command line.
    Python 3.5+, Windows and Linux compatible
    '''
    # The ping command is the same for Windows and Linux, except for the "number of packets" flag.
    if platform.system().lower() == 'windows':
        command = ['ping', '-n', str(packets), '-w', str(timeout), host_or_ip]
        # run parameters: capture output, discard error messages, do not show window
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            creationflags=0x08000000,
        )
        # 0x0800000 is a windows-only Popen flag to specify that a new process will not create a window.
        # On Python 3.7+, you can use a subprocess constant:
        #   result = subprocess.run(command, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # On windows 7+, ping returns 0 (ok) when host is not reachable; to be sure host is responding,
        # we search the text "TTL=" on the command output. If it's there, the ping really had a response.
        return result.returncode == 0 and b'TTL=' in result.stdout
    else:
        command = ['ping', '-c', str(packets), '-W', str(timeout), host_or_ip]
        # run parameters: discard output and error messages
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0


# TODO: Have python query db for last ping time and then give output (like a warning) if time since last ping reply
#       is above a certian time. 


# for ip in ip_list.values():
#     response = subprocess.Popen(f"ping {ip}").read()
#     if "Received = 4" in response:
#         print(f"UP {ip} Ping Successful")
#     else:
#         print(f"DOWN {ip} Ping Unsuccessful")

host = '192.168.1.250'

if ping(host) is True: 
    status_boole = 'UP'
else:
    status_boole = 'DOWN'


# OUTPUT DATA - outputs to Influxdb
#
#
# a point represents a single data record, like a row in a SQL database table
# can add multiple .tag('key', 'value') items
p = (
    influxdb_client.Point('sg_measure45')
    .tag('location', 'prague')
    .tag('tickle', 'time')
    .field('Status', status_boole)
)

write_api.write(bucket=bucket, org=org, record=p)
