"""
This a config template used for the BlueforsTC.py QCodes driver written by Eames Donovan. The values included here are the default values
used for the LD250-1.

All paths are referenced relative to the 
Bluefors Control Software Frontend v2.5.1  (Aug 2026)
OR
ControlSoftwareServer
"""

#The API key and port number can be found in Frotend/ (Hammer Icon) / API
API_KEY = '325dd0cd-19c9-4dc1-9689-e367aa807a02'
PORT_NUMBER = 49098

IP_ADDRESS = '192.168.1.5'

#Channel IDs for the BFTC 1 (50K, 4K , Magnet, Still, and Mxc) are found in Frontend / (Bluefors Icon) / Configuration
#Thermometer IDs
FIFTYK_ID = 1
FOURK_ID = 2
MAGNET_ID = 3
STILL_ID = 5
MXC_ID = 6

#Heater IDs
HS_STILL_ID = 1
HS_MXC_ID = 2
STILL_HTR_ID = 3
MXC_HTR_ID = 4

#Channel IDs for the BFTC 2 (FSE) are found in Frontend / (Bluefors Icon 2) / Configuration
#Thermometer IDs
FSE_ID = 9

#Heater IDs
FSE_HTR_ID = 4


