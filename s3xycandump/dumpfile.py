import datetime
import os
from s3xycandump.candump import Candump
from s3xycandump.savvycan import Savvycan
from s3xycandump.canmsg import CanMsg

class DumpFile: 
    """
    A class to handle writing CAN messages to a file.
    """

    def __init__(self, format, save_dir):
        self.format = format
        self.save_dir = save_dir
        self.file = None
        self.fileStartTime = None
        if format == "candump":
            self.extension = "txt"
        elif format == "savvycan":
            self.extension = "csv"
        else:
            raise ValueError("Invalid format. Supported formats are 'candump' and 'savvycan'.")
    
    def initFile(self):
        # Get the current time rounded down to the nearest 10 minutes
        ts = datetime.datetime.now()
        ts -= datetime.timedelta(minutes=ts.minute % 10, seconds=ts.second, microseconds=ts.microsecond)

        if self.file is not None:
            # Should we still append to currently open file?
            if ts == self.fileStartTime:
                return
            # If not, close it
            del(self.file)

        # Format the time as a string, eg 2025-01-30_20-50
        date_str = ts.strftime("%Y-%m-%d")
        time_str = ts.strftime("%H-%M")
        self.fileStartTime = ts

        # Create the directory if it doesn't exist
        dir = os.path.join(self.save_dir, date_str)
        os.makedirs(dir, exist_ok=True)

        # Create the filename based on the current time
        filename = os.path.join(dir, f"{date_str}_{time_str}")
        
        if self.format == "candump":
            self.file = Candump(filename)
        elif self.format == "savvycan":
            self.file = Savvycan(filename)
        else:
            raise ValueError("Invalid format. Supported formats are 'candump' and 'savvycan'.")

    def writeMessage(self, msg: CanMsg):
        """
        Write the CAN message to a file.
        """
        # Initialize the file if not already done
        self.initFile()

        self.file.writeMessage(msg)
