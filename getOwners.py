from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv
import argparse
import datetime
import requests
import json
import sys
import os


# Load up your keys
load_dotenv()
infura_key = str(os.getenv('INFURA_KEY'))
etherscan_key = str(os.getenv('ETHERSCAN_KEY'))

# Mainnet
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/' + infura_key))

# Accept script arguments
parser = argparse.ArgumentParser(description='Provide the NFT Collection Name')
parser.add_argument('--collection', help='--collection BAYC')

s = vars(parser.parse_args())

# Lookup the Collection Info
if 'collection' in s.keys():
	try:
		f = open('collections.json')
		info = json.load(f)
		nft = info[s['collection']]
	except:
		print("Collection not found, add it!")
else:
	print('Provide the collection argument! ( --collection BAYC)')
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

	# Check if Token 0 returns, else start at 1
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

	# Collect the Token Owners
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
	_owners = getOwners(checkIndex())
	write(_owners)


main()