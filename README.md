# Presence-Poly NodeServer

This is the Presence-Poly for the [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)
(c) 2018 Diego Morales
MIT license.

This node server is intended to use the onboard Bluetooth support that comes in a Raspberry Pi 3 to monitor for the "presence" of other bluetooth devices. This can help determine indoor positioning with respect to your RPi. In theory, this should also work with RPi 1-2 with an external bluetooth adapter, but it has not been tested under those conditions (please let me me know if it works).

Each node will have 3 values: In Range, Proximity, and Scanning

1. In Range: True or False for easiness in determining if the monitored device is detected or not by the RPi
2. Proximity: Value from 0 (not In Range) to 5 (Full signal)
3. Scanning: True or False to allow the node to "sleep" in case you want to temporarily disable a node (the value gets reset after a restart)

### UPDATE v. 1.5! Now proximity is based on RSSI. You can check the original value in the NodeServer logs, but this is basically getting translated to a more usable value. The ranges go like this:

1. Proximity 5 -> RSSI 0 (highest value which means the device is as close as it can be to the RPi)
2. Proximity 4 -> RSSI -1 to RSSI -5
3. Proximity 3 -> RSSI -6 to RSSI -15
4. Proximity 2 -> RSSI -16 to RSSI -35
5. Proximity 1 -> RSSI -36 and beyond


One of the coolest features of Presence-Poly is that it can be installed into as many RPis (w/Polyglot) as needed in order to create a "network" of monitoring devices to allow evaluations via ISY programs such as "At Home", "Left Home", "In Kitchen", "In Bedroom". Your imagination is the limit! Please see this link for more info on this: https://forum.universal-devices.com/topic/24146-can-2-different-rpis-running-polyglot-connect-to-the-same-isy/

## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install. This step should execute the install.sh script, but if not, please see below on the Requirements section for the manual steps
3. Click Add NodeServer in the NodeServer menu of Polyglot, and choose an available slot
4. Go to the NodeServer details from the dashboard, and then click on Configuration
5. Add as many devices you need to monitor in the form
    - Key: Name of the device (accepts spaces)
    - Value: Bluetooth ID of your device (in the form of DF:34:45:D3:B1:E9)
6. Restart the NodeServer
7. Close/Open your Admin Console and you should now see a "Presence Controller" node, with all the node children you created

## Requirements

This should be covered by the install.sh script (chmod +x install.sh before you run it), but if you run into any trouble, please execute the below manually

1. sudo apt-get install -y pi-bluetooth bluez python-bluez
2. python3 -m pip install polyinterface --user
3. python3 -m pip install pybluez --user
