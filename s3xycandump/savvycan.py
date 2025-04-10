import os
from s3xycandump.canmsg import CanMsg

class Savvycan:
    def __init__(self, filename):
        self.filename = filename + "_savvycan.csv"
        
        fileExists = os.path.isfile(self.filename)
        if fileExists:
            print(f"Warning! Appending to an existing file: {self.filename}")
        self.file = open(self.filename, 'a')

        # CSV header
        if not fileExists:
            self.file.write("Time Stamp,ID,Extended,Bus,LEN,D1,D2,D3,D4,D5,D6,D7,D8\n")

        print(f"Opened file {self.filename} for writing.")
    
    def __del__(self):
        if self.file:
            self.file.close()
    
    def writeMessage(self, msg: CanMsg):
        """
        Write a single CAN message in the Candump format
        """

        # Convert data to list of bytes
        data_hex = msg.frame_data.hex()
        data_bytes = [int(data_hex[i:i+2], 16) for i in range(0, len(data_hex), 2)]

        # Format output line
        output_line = f"{msg.ts_us},{msg.frame_id:03x},false,{msg.bus_id:x},{len(data_bytes)}"
        for byte in data_bytes:
            output_line += f",{byte:02X}"
        output_line += "\n"
        self.file.write(output_line)