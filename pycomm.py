#! python3
# This is a script to capture some data from a machine and then send it to influx database.

from influxdb import InfluxDBClient  # type: ignore 
import os
# the above 'type: ignore' comment ignores mypy error

client = InfluxDBClient(
    host='192.168.1.250', 
    port=8086,
    user=os.environ.get('user'),
    password=os.environ.get('password'),
)

x = client.get_list_database()
print(x)
