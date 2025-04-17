import socket
import struct
import time
import datetime

from s3xycandump.canmsg import CanMsg

class Panda:
    def __init__(self, ip, port, candb=None, subscribeList=[]):
        self.ip = ip
        self.port = port
        self.candb = candb
        self.subscribeList = subscribeList
        self.sock = None
        self.lastSend = None
        self.lastRecv = None
        self.lastStatsPrint = None
        self.statsPacketCount = 0

        # If subscribelist is defined, no need for candb
        if len(self.subscribeList) > 0:
            if candb is not None:
                print("WARNING: Candb is not used when subscribelist is defined. Ignoring candb.")
                self.candb = None

    def reconnect(self):
        """
        Reconnect to the Panda device.
        """
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                print(f"Error closing socket: {e}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.sendto(b"ehllo", (self.ip, self.port))
        self.lastSend = time.time()
        self.lastRecv = None
    
    def refresh(self):
        """
        Refresh the connection to the Panda device. Needs to be done every few seconds to keep the connection alive.
        """
        if self.sock is None:
            self.reconnect()
        else:
            if self.lastSend is not None and time.time() - self.lastSend < 1:
                # Already sent a message within a second. Skipping.
                return
            try:
                self.sock.sendto(b"ehllo", (self.ip, self.port))
                self.lastSend = time.time()
            except Exception as e:
                print(f"Error sending refresh command: {e}")
                self.reconnect()
    
    def subscribe(self):
        """
        Subscribe to a list of CAN IDs.
        Empty list will subscribe to all CAN IDs in DBC.
        """
        if self.sock is None:
            self.reconnect()
        
        subPacket = bytearray([0x0f])
        
        if len(self.subscribeList) == 0:
            self.subscribeList = [x.frame_id for x in self.candb.messages]
        
        for item in self.subscribeList:
            frameId = item
            if not isinstance(frameId, int):
                print(f"Invalid frame ID: {frameId}. Must be an integer.")
                continue
            if frameId < 0 or frameId > 0x7FF:
                print(f"Invalid frame ID: {frameId}. Must be between 0 and 2047 (0x7FF, 11 bits).")
                continue
            # A maximum of 43 bus id/frame id pairs can be sent per packet
            if len(subPacket) > 1 + (3*42):
                self.sock.sendto(subPacket, (self.ip, self.port))
                subPacket = bytearray([0x0f])
            subPacket.extend(bytearray([
                0xff,
                frameId >> 8,
                frameId & 0xff]))
        if len(subPacket) > 1:
            self.sock.sendto(subPacket, (self.ip, self.port))
        self.lastSend = time.time()
        print(f"Subscribed to {len(self.subscribeList)} CAN IDs.")

    def parseMessage(self, data):
        """
        Parse a message from the Panda device.
        """
        
        unpackedHeader = struct.unpack('<II', data[0:8])
        frameID = unpackedHeader[0] >> 21
        frameLength = unpackedHeader[1] & 0x0F
        frameBusId = unpackedHeader[1] >> 4
        parsedLength = 8 + frameLength
        frameData = data[8:parsedLength]

        if frameID == 0:
            return None
        
        if frameBusId == 15 and frameID == 6:
            # TODO is this required? Is this proper?
            print(f"Received Panda ACK, responding by sending subscription.")
            self.subscribe()
            return None

        if frameLength < 1 or frameLength > 8:
            print(f"Invalid frame length: {frameLength}")
            print(f"Bus ID: {frameBusId}, Frame ID: {frameID}, Frame length: {frameLength} Data: {frameData.hex()}")
            return None
    
        msg = CanMsg(
            ts_unix = time.time(),
            bus_id = frameBusId,
            frame_id = frameID,
            frame_data = frameData
        )

        if self.lastRecv is None:
            print(f"Received first CAN frame at unix TS {msg.ts_unix}!")
            print(f"    Bus ID: 0x{msg.bus_id:x}, Frame ID: 0x{msg.frame_id:03x}, Frame length: {len(msg.frame_data)}, Data: 0x{msg.frame_data.hex()}")
        self.lastRecv = msg.ts_unix
        return msg

    def parseLoop(self, data):
        # Should be a maximum of 512 frames, 16 bytes each
        if len(data) > 512*16:
            print(f"ERROR: Received too large packet: {len(data)} bytes. Expecting a max of 512 frames, 16 bytes each (8192 bytes).")
            return None
        if len(data) % 16 != 0:
            print(f"ERROR: Received invalid packet length: {len(data)}. Expecting a multiple of 16 bytes.")
            return None
        offset = 0
        msgList = []
        while offset < len(data):
            msg = self.parseMessage(data[offset:offset+16])
            if msg is not None:
                msgList.append(msg)
            offset += 16
        return msgList
    
    def debugPrint(self, data):
        print(f"Successfully parsed a packet with {len(data)} CAN messages:")
        for msg in data:
            print(f"    Bus ID: 0x{msg.bus_id:x}, Frame ID: 0x{msg.frame_id:03x}, Frame length: {len(msg.frame_data)}, Data: 0x{msg.frame_data.hex()}")

    def printStats(self, count):
        # Print stats every 1 minute, exactly when wall clock minute has changed
        self.statsPacketCount += count
        if self.lastStatsPrint is None:
            self.lastStatsPrint = datetime.datetime.now()
            return
        if datetime.datetime.now().replace(second=0, microsecond=0) > self.lastStatsPrint.replace(second=0, microsecond=0):
            self.lastStatsPrint = datetime.datetime.now().replace(second=0, microsecond=0)
            ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{ts_str} - Received {self.statsPacketCount} messages since last print ({int(self.statsPacketCount/60)} per second).")
            self.statsPacketCount = 0

    def waitForMessage(self):
        """
        Wait for messages from the Panda device.
        """
        if self.sock is None:
            self.reconnect()
        startTs = time.time()
        failCount = 0
        
        while True:
            try:
                data, addr = self.sock.recvfrom(65535)
                msgList = self.parseLoop(data)
                #self.debugPrint(msgList)
                self.printStats(len(msgList))
                return msgList
            except BlockingIOError:
                # No data available yet
                time.sleep(0.11)
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.reconnect()
            
            self.refresh()
            waitTime = time.time() - startTs

            if self.lastRecv is None and waitTime > 5:
                print("ERROR: Connection timed out. No data received within 5s of sending ehlo. Trying again...")
                failCount += 1
                startTs = time.time()
                self.reconnect()
            
            if self.lastRecv is not None and waitTime > 5:
                print("ERROR: Connection broke. No data received within last 5 seconds. Reconnecting...")
                self.reconnect()
            
            if failCount > 5:
                print("ERROR: Tried connecting 5 times but did not get any response.")
                print("       May need to wait until session times out from Commander's end.")
                print("       Sleeping for 120s...")
                self.sock.close()
                self.sock = None
                failCount = 0
                time.sleep(120)