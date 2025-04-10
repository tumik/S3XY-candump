import os
from s3xycandump.canmsg import CanMsg

class Candump:
    def __init__(self, filename):
        self.filename = filename + "_candump.txt"
        
        fileExists = os.path.isfile(self.filename)
        if fileExists:
            print(f"Warning! Appending to an existing file: {self.filename}")
        self.file = open(self.filename, 'a')

        # No header write required for candump format

        print(f"Opened file {self.filename} for writing.")
    
    def __del__(self):
        if self.file:
            self.file.close()
    
    def writeMessage(self, msg: CanMsg):
        """
        Write a single CAN message in the Candump format
        """
        self.file.write(f"({msg.ts_unix:.6f}) can{msg.bus_id:x} {msg.frame_id:03x}#{msg.frame_data.hex()}\n")