# S3XY-candump

Python tools to dump CAN bus data from a Tesla vehicle using [Enhauto S3XY buttons / The Commander](https://enhauto.com/commander)

S3XY Commander can connect to two different CAN buses on a Tesla vehicle. With Wi-Fi enabled, it can forward the raw can data over Wi-Fi using the Panda protocol.

This project has only been tested on Model 3 2022. You should change the DBC file used if you are using a different vehicle. The DBC file is only used as a list of can message IDs to subscribe to.

[Candash](https://github.com/nmullaney/candash/blob/e34dae7db4df0f1a18535ccde6ca55822b79318b/android/app/src/main/java/app/candash/cluster/PandaService.kt) project was great help for understanding the Panda protocol.

## Instructions

1. Connect the S3XY Commander
2. Enable Wi-Fi in Commander settings in S3XY app

    Now you may test the Wi-Fi Panda data using [ScanMyTesla](https://www.scanmytesla.com/) app. But make sure to disconnect after testing - only one device can be connected to Wi-Fi at a time

3. Connect your device (for example Raspberry Pi or a laptop) to the Commander's Wi-Fi
4. Check the hardcoded settings in s3xy-candump.py
5. Run the project: `python3 s3xy-candump.py`

## Output formats

Currently two output formats are supported and enabled by default, and they should cover importing the data to variety of tools:
- **candump** - Should match with log exports of candump tool of [can-utils](https://github.com/linux-can/can-utils/)
- **savvycan** - Should match with [SavvyCAN](https://www.savvycan.com/) / GVRET format.

SavvyCAN format can be used with [make_cabana_route](https://github.com/projectgus/make_cabana_route) to import the dump into [Openpilot Cabana](https://github.com/commaai/openpilot/tree/master/tools/cabana#readme)

## Disclaimer

_TESLA is a registered trademarks of Tesla Motors, Inc. This project has no affiliation with Tesla Motors, Inc. or Enhance Ltd. The terms Tesla, Enhauto and S3XY Commander are used strictly for identification purposes only. It is not implied that any part of this project is a product of, or approved by, Tesla Motors, Inc. or Enhance Ltd. All trademarks and registered trademarks are the property of their respective owners._
