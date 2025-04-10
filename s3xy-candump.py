#!/usr/bin/env python 

# 
# s3xy-candump.py - A script to dump CAN messages from Panda interface to a file.
#

PANDA_IP = "192.168.4.1"
PANDA_PORT = 1338
SAVE_DIR = "candumps"
DBC_FILE = "model3dbc/Model3CAN.dbc"    # Required to list the CAN IDs to subscribe to.

FORMAT_ENABLE_CANDUMP = True
FORMAT_ENABLE_SAVVYCAN = True

import cantools
import s3xycandump.panda as Panda
import s3xycandump.dumpfile as DumpFile

if __name__ == "__main__":
    # Load the DBC file
    try:
        dbc = cantools.database.load_file(DBC_FILE)
    except Exception as e:
        print(f"Error loading DBC file: {e}")
        exit(1)

    # Create a Panda object. Subscribe to all messages in the DBC file.
    panda = Panda.Panda(PANDA_IP, PANDA_PORT, dbc, subscribeList=[])

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