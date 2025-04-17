#!/usr/bin/env python 

# 
# s3xy-candump.py - A script to dump CAN messages from Panda interface to a file.
#

PANDA_IP = "192.168.4.1"
PANDA_PORT = 1338
SAVE_DIR = "candumps"
DBC_FILES = [   # Required to list the CAN IDs to subscribe to.
    "model3dbc/Model3CAN.dbc",
    "DBCTools/Samples/tesla_model3.dbc"
]
ADDITIONAL_IDs = [ 0x14A, 0x152, 0x172, 0x33D, 0x364, 0x3B2, 0x41D, 0x432, 0x50E, 0x545, 0x559, 0x682, 0x70A, 0x712, 0x724, 0x732, 0x73D, 0x1F9, 0x2A4, 0x2C4, 0x2D1, 0x2F2, 0x310, 0x31E, 0x320, 0x339, 0x33D, 0x364, 0x372, 0x374, 0x3A4, 0x3AA, 0x3B2, 0x3C4, 0x3DD, 0x41D, 0x438, 0x452, 0x458, 0x464, 0x472, 0x492, 0x53E, 0x545 ]

FORMAT_ENABLE_CANDUMP = True
FORMAT_ENABLE_SAVVYCAN = True

import cantools
import s3xycandump.panda as Panda
import s3xycandump.dumpfile as DumpFile

if __name__ == "__main__":
    # Gather a list of Frame IDs in each DBC file + the additional IDs
    id_list = ADDITIONAL_IDs.copy()
    for dfile in DBC_FILES:
        file_id_count = 0
        try:
            # Commented out. Some DBC files have issues making them incompatible with cantools.
            #dbc = cantools.database.load_file(dfile)
            #for message in dbc.messages:
            #    if message.frame_id not in id_list:
            #        id_list.append(message.frame_id)
            # Lets just parse ourselves
            with open(dfile, 'r') as f:
                for line in f:
                    if line.startswith('BO_'):
                        parts = line.split()
                        frame_id = int(parts[1])
                        file_id_count += 1
                        if frame_id not in id_list:
                            id_list.append(frame_id)
                            #print(f"Added frame ID {frame_id:03x} from {dfile}")
        except Exception as e:
            print(f"Error handling DBC file {dfile}: {e}")
            exit(1)
        print(f"Loaded {file_id_count} frame IDs from {dfile}")
    print(f"Loaded {len(ADDITIONAL_IDs)} additional frame IDs from the list")
    print(f"Total unique frame IDs to subscribe to: {len(id_list)}")

    # Create a Panda object.
    panda = Panda.Panda(PANDA_IP, PANDA_PORT, subscribeList=id_list)

    # Create dumpfile objects for each enabled format
    dumpfiles = []
    if FORMAT_ENABLE_CANDUMP:
        dumpfiles.append(DumpFile.DumpFile("candump", SAVE_DIR))
    if FORMAT_ENABLE_SAVVYCAN:
        dumpfiles.append(DumpFile.DumpFile("savvycan", SAVE_DIR))

    # Main loop
    while True:
        try:
            # Read a message from the Panda device
            msgList = panda.waitForMessage()
            if msgList is not None:
                for msg in msgList:
                    # Write the message to each enabled dumpfile
                    for dumpfile in dumpfiles:
                        dumpfile.writeMessage(msg)
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            raise