"""
AWS IoT Greengrass component for publishing Ecowitt weather data to AWS IoT Core
"""

import json
import os
import socket
import time
import traceback
from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
from awsiot.greengrasscoreipc.model import QOS

PORT = 45000
CMD_LIVEDATA = b'\xff\xff\x27\x03\x2a'
TOPIC = f'ecowitt/{os.environ.get("AWS_IOT_THING_NAME")}/livedata'

# Taken from EcoWitt Data Exchange TCP Protocol document
# Suitable for GW1000, 1100, 1900, 2000, 2001, 2680, 2650
# Tested with GW2000C_V3.0.9, 4xWH31, 1xWN36 and 3xWH51
# Solar Irradiance = Lux x 0.0079 W/m2
LIVE_DATA_ITEMS = {
    #    name                   size    divisor
    1:  ('Indoor Temperature',  2,      10),
    2:  ('Outdoor Temperature', 2,      10),
    6:  ('Indoor Humidity',     1,      1),
    7:  ('Outdoor Humidity',    1,      1),
    8:  ('Absolute Pressure',   2,      10), # hPa
    9:  ('Relative Pressure',   2,      10),
    10: ('Wind Direction',      2,      1),  # degrees
    11: ('Wind Speed',          2,      10), # m/s
    12: ('Gust Speed',          2,      10),
    21: ('Light',               4,      10), # Lux
    22: ('UV',                  2,      1),  # uW/m2
    23: ('UV Index',            1,      1),  # 0-15
    25: ('Maximum Wind Speed',  2,      10),
    26: ('Temperature 1',       2,      10),
    27: ('Temperature 2',       2,      10),
    28: ('Temperature 3',       2,      10),
    29: ('Temperature 4',       2,      10),
    30: ('Temperature 5',       2,      10),
    31: ('Temperature 6',       2,      10),
    32: ('Temperature 7',       2,      10),
    33: ('Temperature 8',       2,      10),
    34: ('Humidity 1',          1,      1),
    35: ('Humidity 2',          1,      1),
    36: ('Humidity 3',          1,      1),
    37: ('Humidity 4',          1,      1),
    38: ('Humidity 5',          1,      1),
    39: ('Humidity 6',          1,      1),
    40: ('Humidity 7',          1,      1),
    41: ('Humidity 8',          1,      1),
    44: ('Soil Moisture 1',     1,      1),
    46: ('Soil Moisture 2',     1,      1),
    48: ('Soil Moisture 3',     1,      1),
    50: ('Soil Moisture 4',     1,      1),
    52: ('Soil Moisture 5',     1,      1),
    54: ('Soil Moisture 6',     1,      1),
    56: ('Soil Moisture 7',     1,      1),
    58: ('Soil Moisture 8',     1,      1),
}

def parse_live_data(data):
    """ Parse live data from EcoWitt device """
    msg = { 'Timestamp': round(time.time()) }
    payload_length = (data[3] * 256) + data[4]
    checksum = sum(data[2:-1]) & 0xFF

    # Only proceed if the response is valid and expected
    if data[0] == 0xff and data[1] == 0xff and data[2] == 0x27 and\
        payload_length == (len(data) - 2) and checksum == data[-1]:

        index = 5

        while index < (len(data) - 1):
            if data[index] in LIVE_DATA_ITEMS:
                value_payload = data[index + 1:index + LIVE_DATA_ITEMS[data[index]][1] + 1]
                value = int.from_bytes(value_payload, byteorder='big')
                if LIVE_DATA_ITEMS[data[index]][2] != 1:
                    value /= LIVE_DATA_ITEMS[data[index]][2]
                msg[LIVE_DATA_ITEMS[data[index]][0]] = value
                index += LIVE_DATA_ITEMS[data[index]][1] + 1
            else:
                break
    else:
        print('Invalid or expected response from Ecowitt')

    return msg

ipc_client = None

while ipc_client is None:
    try:
        print('Creating IPC client')
        ipc_client = GreengrassCoreIPCClientV2()
    except Exception as error:
        print(f'Error creating IPC client: {repr(error)}.')

configuration = ipc_client.get_configuration()
print(f'Configuration: {configuration}')

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((configuration.value['gatewayAddress'], PORT))
            s.settimeout(3.0)

            s.sendall(CMD_LIVEDATA)
            live_data = s.recv(1024)
            iot_msg = parse_live_data(live_data)
            print(iot_msg)

            s.close()

            ipc_client.publish_to_iot_core(topic_name=TOPIC, qos=QOS.AT_MOST_ONCE,\
                                           payload=json.dumps(iot_msg))

    except Exception as e:
        traceback.print_exc()
        print(e)

    time.sleep(60)
