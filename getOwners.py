from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from hexbytes import HexBytes as hb
from dotenv import load_dotenv
import datetime
import requests
import json
import time
import sys
import csv
import os

# Load up your keys
load_dotenv()
infura_key = str(os.getenv('INFURA_KEY'))
etherscan_key = str(os.getenv('ETHERSCAN_KEY'))

# Mainnet
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/' + infura_key))
collection = sys.argv[1]

# Lookup the Collection Info
if collection:
	try:
		f = open('collections.json')
		info = json.load(f)
		nft = info[collection]
	except:
		print("Collection not found, add it!")
else:
	print('Provide the collection argument!')
	exit()


# Lookup the NFT Contracts ABI
def abiLookupByAddress(addr):
	url = 'https://api.etherscan.io/api?module=contract&action=getabi&address=' + addr + '&apikey=' + etherscan_key
	r = requests.get(url=url)
	abi = json.loads(r.text)
	return abi['result']


# Check NFT Token Index
def checkIndex():
		# Get the NFT Contract ABI
	nftABI = abiLookupByAddress(w3.toChecksumAddress(nft))
		#Load the Contract Instance
	nftContract = w3.eth.contract(address=nft, abi=nftABI)

	try:
		owner = nftContract.functions.ownerOf(0).call()
		print('Token Index starts at 0')
		nftIndexStart = 0
	except ContractLogicError:
		print('Token Index starts at 1')
		nftIndexStart = 1

	return nftIndexStart


def getOwners(nftIndexStart):
	# Get the NFT Contract ABI
	nftABI = abiLookupByAddress(w3.toChecksumAddress(nft))
	# Load the Contract Instance
	nftContract = w3.eth.contract(address=nft, abi=nftABI)
	# Get the Total Supply of NFTs
	nftCount = nftContract.functions.totalSupply().call()

	# Set the NFT Token Index
	x = nftIndexStart
	# Initialize the owners Index
	y = 0
	# Initialize the owners List
	owners = []
	token = []
	while x <= nftCount:
		try:
			owner = nftContract.functions.ownerOf(x).call()
			token = {"id": x, "owner": owner}
			owners.append(token)
			print('Token ' + str(x) + ': ' + str(owners[y]['owner']))
			x = x + 1
			y = y + 1
		except ContractLogicError:
			print('No NFT for Token ID: ' + str(x))
			x = x + 1

	return owners


def write(owners):
	# Get Todays Date
	now = datetime.datetime.now()
	with open('reports/' + collection + '-' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + 'owners.json', 'w') as result:
		json.dump(owners, result, indent=4)



def main():
	getOwners(checkIndex())
	write(owners)


main()