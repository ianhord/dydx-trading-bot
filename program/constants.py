from dydx3.constants import API_HOST_GOERLI, API_HOST_MAINNET
from decouple import config

#  !!!! SELECT MODE !!!
MODE = "DEVELOPMENT"


#close all open positions and orders
ABORT_ALL_POSITIONS = False


# Find Cointegrated Pairs
FIND_COINTEGRATED = False

# Manage exits
MANAGE_EXITS = True

# Place Trades
PLACE_TRADES = True

# Resolution
RESOLUTION = "1HOUR"

#Stats Window
WINDOW = 21

# Tresholds - Opening
MAX_HALF_LIFE = 24
ZSCORE_THRESH = 1.5
USD_PER_TRADE = 100
USD_MIN_COLLATERAL = 1800

# Thresholds - Closing
CLOSE_AT_ZSCORE_CROSS = True

#Ethereum Address
ETHEREUM_ADDRESS = "0x241f4Bff63c69435C6c6Fc69369c6123A1218777"

#KEYS - Production
# Must remember to be on Mainnet on DYDX
STARK_PRIVATE_KEY_MAINNET = config("STARK_PRIVATE_KEY_MAINNET")
DYDX_API_KEY_MAINNET = config("DYDX_API_KEY_MAINNET")
DYDX_API_SECRET_MAINNET = config("DYDX_API_SECRET_MAINNET")
DYDX_API_PASSPHRASE_MAINNET = config("DYDX_API_PASSPHRASE_MAINNET")

#KEYS - Development
# Must remember to be on Mainnet on DYDX
STARK_PRIVATE_KEY_TESTNET = config("STARK_PRIVATE_KEY_TESTNET")
DYDX_API_KEY_TESTNET = config("DYDX_API_KEY_TESTNET")
DYDX_API_SECRET_TESTNET = config("DYDX_API_SECRET_TESTNET")
DYDX_API_PASSPHRASE_TESTNET = config("DYDX_API_PASSPHRASE_TESTNET")

#KEYS - Export
STARK_PRIVATE_KEY = STARK_PRIVATE_KEY_MAINNET if MODE == "PRODUCTION" else STARK_PRIVATE_KEY_TESTNET
DYDX_API_KEY = DYDX_API_KEY_MAINNET if MODE == "PRODUCTION" else DYDX_API_KEY_TESTNET
DYDX_API_SECRET = DYDX_API_SECRET_MAINNET if MODE == "PRODUCTION" else DYDX_API_SECRET_TESTNET
DYDX_API_PASSPHRASE = DYDX_API_PASSPHRASE_MAINNET if MODE == "PRODUCTION" else DYDX_API_PASSPHRASE_TESTNET

#HOST - Export
HOST = API_HOST_MAINNET if MODE == "PRODUCTION" else API_HOST_GOERLI

# HTTP PROVIDER
HTTP_PROVIDER_MAINNET = "https://eth-mainnet.g.alchemy.com/v2/l5ERUhkyV_uGAxOvO5OUfZrBbVtNI2IE"
HTTP_PROVIDER_TESTNET = "https://eth-goerli.g.alchemy.com/v2/fsVnt2P-LCJIpykDVlaCW1qGNGx23pzO"
HTTP_PROVIDER = HTTP_PROVIDER_MAINNET if MODE == "PRODUCTION" else HTTP_PROVIDER_TESTNET

