# Presence-Poly NodeServer

This is the Presence-Poly for the [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)
(c) 2018 Diego Morales
MIT license.

## IMPORTANT NOTE - Upgrading from 1.x to 2.0
### If you are upgrading from any previous version of Presence-Poly, please proceed to "Update" normally, and then make sure to delete any existing node from the NodeServer Nodes section, followed by a NodeServer and Admin Console "Restart" (in that order). The changes on this version include the addition/redefinition of node types.

There are 2 node types on Presence-Poly: Presence and Network

## Bluetooth Node:
This node type is intended to use the onboard Bluetooth support that comes in a Raspberry Pi 3 to monitor for the "presence" of other bluetooth devices. This can help determine indoor positioning with respect to your RPi. In theory, this should also work with RPi 1-2 with an external bluetooth adapter, but it has not been tested under those conditions (please let me me know if it works).

Each node will have 3 values: In Range, Proximity, and Scanning

1. In Range: True or False for easiness in determining if the monitored device is detected or not by the RPi
2. Proximity: Value from 0 (Out of range) to 5 (Full signal)
3. Scanning: True or False to allow the node to "sleep" in case you want to temporarily disable a node (the value gets reset after a restart)

Proximity is based on RSSI. You can check the original value in the NodeServer logs, but this is basically getting translated to a more usable value. The ranges go like this:

1. Proximity 5 -> RSSI 0 (highest value which means the device is as close as it can be to the RPi)
2. Proximity 4 -> RSSI -1 to RSSI -5
3. Proximity 3 -> RSSI -6 to RSSI -15
4. Proximity 2 -> RSSI -16 to RSSI -35
5. Proximity 1 -> RSSI -36 and beyond
6. Proximity 0 -> Out of range

## Network Node:
This node type is intended to monitor for the "presence" of a device inside of the same network the RPi is connected to. It does this by sending 1 ICMP Ping package to the IP of the monitored device.

Each node will have 3 values: On Network, Strength, and Scanning

1. On Network: True or False for easiness in determining if the monitored device is detected or not by the RPi
2. Strength: Value from 0 (Out of network) to 5 (No Faults)
3. Scanning: True or False to allow the node to "sleep" in case you want to temporarily disable a node (the value gets reset after a restart)

Strength is based on the number of consecutive successful pings. It will decrease with each dropped ping package until it reaches 0, which means the device is off the network. It could also be seen as an "inverted fault counter".

## Multiple RPis:
One of the coolest features of Presence-Poly is that it can be installed into as many RPis (w/Polyglot) as needed in order to create a "network" of monitoring devices to allow evaluations via ISY programs such as "At Home", "Left Home", "In Kitchen", "In Bedroom". Your imagination is the limit! Please see this link for more info on this: https://forum.universal-devices.com/topic/24146-can-2-different-rpis-running-polyglot-connect-to-the-same-isy/

## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install. This step should execute the install.sh script, but if not, please see below on the Requirements section for the manual steps
3. Click Add NodeServer in the NodeServer menu of Polyglot, and choose an available slot
4. Go to the NodeServer details from the dashboard, and then click on Configuration
5. Add as many devices you need to monitor in the form
    Bluetooth:
        - Key: Name of the device (accepts spaces)
        - Value: Bluetooth ID of your device (in the form of DF:34:45:D3:B1:E9)
    Network:
        - Key: Name of the device (accepts spaces)
        - Value: IP address of your device (in the form of 192.168.0.1)
        
    *No 2 keys can be the same, so if you are monitoring a device both on bluetooth and network, the key (name) would need to be different for each type. For example, you could append the type to the name like: "iPhone-Bluetooth", "iPhone-Network"
6. Restart the NodeServer
7. Close/Open your Admin Console and you should now see a "Presence Controller" node, with all the node children you created

## Requirements

This should be covered by the install.sh script (chmod +x install.sh before you run it), but if you run into any trouble, please execute the below manually

1. sudo apt-get install -y pi-bluetooth bluez python-bluez
2. python3 -m pip install polyinterface --user
3. python3 -m pip install pybluez --user
