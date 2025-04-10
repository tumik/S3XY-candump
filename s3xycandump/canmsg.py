class CanMsg:
    """
    Class representing a CAN message.
    Attributes:
        ts_unix (float): Timestamp in Unix format.
        bus_id (int): Bus ID.
        frame_id (int): Frame ID.
        frame_data (bytes): Frame data.
    Methods:
        ts_us (int): Timestamp in microseconds.
    """
    def __init__(self, ts_unix, bus_id, frame_id, frame_data):
        self.ts_unix = ts_unix
        self.bus_id = bus_id
        self.frame_id = frame_id
        self.frame_data = frame_data
    
    @property
    def ts_us(self):
        return int(self.ts_unix * 1_000_000)