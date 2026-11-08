# File : example_e1214.py
# Author : Sébastien Deriaz
# License : GPL
import time

from syndesi import IP

from syndesi_drivers.industrial.iologik_e1200 import IoLogikE1214

ADDRESS = "192.168.127.254"

def main() -> None:
    module = IoLogikE1214(IP(ADDRESS))
    print(f"Model : {module.get_model_name()} ({module.get_firmware_version()})")

    # Toggle relay 0
    for i in range(10):
        module.write_relay(0, i % 2 == 0)
        time.sleep(0.5)

    # Set all relays at once
    module.write_relays([True, False, True, False, True, False])
    print(f"Relays : {module.read_relays()}")
    module.write_relays([False] * 6)

    # Read digital inputs
    print(f"Digital inputs : {module.read_digital_ins()}")

if __name__ == '__main__':
    main()
