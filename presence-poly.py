#!/usr/bin/env python3
import polyinterface
import sys
import time
import bluetooth
import bluetooth._bluetooth as bt
import struct
import array
import fcntl
import os

LOGGER = polyinterface.LOGGER

class PresenceController(polyinterface.Controller):

    def __init__(self, polyglot):
        super(PresenceController, self).__init__(polyglot)
        self.name = 'Presence Controller'

    def start(self):
        LOGGER.info('Presence Controller started.')
        self.check_params()
        self.discover()

    def shortPoll(self):
        #This is where the updates to each node happen
        for node in self.nodes:
            self.nodes[node].update()

    def longPoll(self):
        #Not used
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        #Discover nodes and add them by type
        for key,val in self.polyConfig['customParams'].items():
            #LOGGER.debug(key + " => " + val)
            if (val.find(':') != -1):
                blueid = val.replace(':','').lower()
                self.addNode(BluetoothNode(self, self.address, blueid, key))
            elif (val.find('.') != -1):
                netip = val.replace('.','')
                self.addNode(NetworkNode(self, self.address, netip, val, key))

    def update(self):
        pass    

    def delete(self):
        LOGGER.info('Deleted')

    def stop(self):
        LOGGER.debug('Presence Controller stopped.')

    def check_params(self):
        # Remove all existing notices
        self.removeNoticesAll()
        
    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all:')
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    id = 'presence_controller'
    commands = {
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
        'REMOVE_NOTICES_ALL': remove_notices_all
    }
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2}
    ]

class BlueHelper(object):

    def __init__(self, addr):
        #Initializes bluetooth object
        self.addr = addr
        self.hci_sock = bt.hci_open_dev()
        self.hci_fd = self.hci_sock.fileno()
        self.bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.bt_sock.settimeout(10)
        self.connected = False
        self.cmd_pkt = None

    def prepare_command(self):
        #Creates the command
        reqstr = struct.pack(
            "6sB17s", bt.str2ba(self.addr), bt.ACL_LINK, bytes("\0",'utf-8') * 17)
        request = array.array("b", reqstr)
        handle = fcntl.ioctl(self.hci_fd, bt.HCIGETCONNINFO, request, 1)
        handle = struct.unpack("8xH14x", request.tobytes())[0]
        self.cmd_pkt = struct.pack('H', handle)

    def connect(self):
        #Connects to the bluetooth device
        self.bt_sock.connect_ex((self.addr, 1))
        self.connected = True

    def get_rssi(self):
        #Gets the RSSI value
        try:
            # Only do connection if not already connected
            if not self.connected:
                self.connect()
            if self.cmd_pkt is None:
                self.prepare_command()
            # Send command to request RSSI
            rssi = bt.hci_send_req(
                self.hci_sock, bt.OGF_STATUS_PARAM,
                bt.OCF_READ_RSSI, bt.EVT_CMD_COMPLETE, 4, self.cmd_pkt)
            rssi = struct.unpack('b', rssi[3:4])[0]
            return rssi
        except IOError as ioerr:
            # Happens if connection fails
            #LOGGER.debug("I/O error: {0}".format(ioerr))
            self.connected = False
            return None

class BluetoothNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(BluetoothNode, self).__init__(controller, primary, address, name)
        self.blueid = ':'.join(self.address[i:i+2] for i in range(0, len(self.address), 2)).upper()
        self.scan = 1
        self.proximity = 0

    def start(self):
        self.setOn('DON')
        
    def update(self):
        if (self.scan):
            btnode = BlueHelper(addr=self.blueid)
            result = btnode.get_rssi()
            if (result != None):
                LOGGER.debug('Bluetooth ' + self.blueid + ': In range. RSSI: ' + str(result))
                if (result >=0):
                    self.setInRange(5)
                elif (result < 0 and result >= -5):
                    self.setInRange(4)
                elif (result < -5 and result >= -15):
                    self.setInRange(3)
                elif (result < -15 and result >= -35):
                    self.setInRange(2)
                elif (result < -35):
                    self.setInRange(1)
            elif (self.proximity > 1):
                self.setInRange(self.proximity - 1)
                LOGGER.debug('Bluetooth ' + self.blueid + ': In Fault')
            elif (self.proximity == 1):
                LOGGER.debug('Bluetooth ' + self.blueid + ': Out of range')
                self.setOutRange()
            
    def setInRange(self,prox):
        self.setDriver('ST', 1)
        self.proximity = prox
        self.setDriver('GV0', self.proximity)
        
    def setOutRange(self):
        self.setDriver('ST', 0)
        self.proximity = 0
        self.setDriver('GV0', self.proximity)
    
    def setOn(self, command):
        self.setOutRange()
        self.setDriver('GV1', 1)
        self.scan = 1

    def setOff(self, command):
        self.setOutRange()
        self.setDriver('GV1', 0)
        self.scan = 0

    def query(self):
        self.reportDrivers()


    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 56},
        {'driver': 'GV1', 'value': 1, 'uom': 2}
    ]

    id = 'bluetooth_node'

    commands = {
                    'DON': setOn, 'DOF': setOff
                }

class PingHelper(object):

    def __init__(self, ip, timeout):
        self.ip = ip
        self.timeout = timeout

    def ping(self):
        try:
            response = os.system("ping -c 1 -W " + str(self.timeout-1) + " " + self.ip)
            if response == 0:
                return response
            else:
                return None
        except:
            # Capture any exception
            return None
                
class NetworkNode(polyinterface.Node):

    def __init__(self, controller, primary, address, ipaddress, name):
        super(NetworkNode, self).__init__(controller, primary, address, name)
        self.ip = ipaddress
        self.scan = 1
        self.strength = 0
        
    def start(self):
        self.setOn('DON')
        
    def update(self):
        if (self.scan):
            onnet = PingHelper(ip=self.ip,timeout=self.parent.polyConfig['shortPoll'])
            result = onnet.ping()
            if (result != None):
                LOGGER.debug('Network ' + self.ip + ': On Network')
                self.setOnNetwork(5)
            elif (self.strength > 1):
                self.setOnNetwork(self.strength - 1)
                LOGGER.debug('Network ' + self.ip + ': In Fault')
            elif (self.strength == 1):
                LOGGER.debug('Network ' + self.ip + ': Out of Network')
                self.setOffNetwork()
            
    def setOnNetwork(self,strength):
        self.setDriver('ST', 1)
        self.strength = strength
        self.setDriver('GV0', self.strength)
        
    def setOffNetwork(self):
        self.setDriver('ST', 0)
        self.strength = 0
        self.setDriver('GV0', self.strength)
    
    def setOn(self, command):
        self.setOffNetwork()
        self.setDriver('GV1', 1)
        self.scan = 1

    def setOff(self, command):
        self.setOffNetwork()
        self.setDriver('GV1', 0)
        self.scan = 0

    def query(self):
        self.reportDrivers()


    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 56},
        {'driver': 'GV1', 'value': 1, 'uom': 2}
    ]

    id = 'network_node'

    commands = {
                    'DON': setOn, 'DOF': setOff
                }

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('PresenceController')
        polyglot.start()
        control = PresenceController(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
