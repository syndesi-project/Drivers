# File : example_adam6266.py
# Author : Sébastien Deriaz
# License : GPL
from syndesi import IP
import time

from adam6266 import Adam6266

ADDRESS = "192.168.1.219"

def main():
    module = Adam6266(IP(ADDRESS))

    # Toggle relay 0
    for i in range(10):
        module.write_relay(0, i % 2 == 0)
        time.sleep(0.1)

    # Set all relays at once
    module.write_relays([True, False, True, False])
    print(f"Relays : {module.read_relays()}")
    module.write_relays([False] * 4)

    # Read digital inputs
    print(f"Digital inputs : {module.read_digital_ins()}")

if __name__ == '__main__':
    main()
