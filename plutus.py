# Plutus Bitcoin Brute Forcer
# Made by Isaac Delly
# https://github.com/Isaacdelly/Plutus

import os
import datetime
import pickle
import hashlib
import binascii
import multiprocessing
from fastecdsa import keys, curve
from message import send_telegram_message

DATABASE = r'database/MAR_15_2021/'

def generate_private_key(): 
	"""
	Generate a random 32-byte hex integer which serves as a randomly 
	generated Bitcoin private key.
	Average Time: 0.0000061659 seconds
	"""
	return binascii.hexlify(os.urandom(32)).decode('utf-8').upper()

def private_key_to_public_key(private_key):
	"""
	Accept a hex private key and convert it to its respective public key. 
	Because converting a private key to a public key requires SECP256k1 ECDSA 
	signing, this function is the most time consuming and is a bottleneck in 
	the overall speed of the program.
	Average Time: 0.0016401287 seconds
	"""
	c = int('0x%s'%private_key,0)
	d = keys.get_public_key(c, curve.secp256k1)
	# return '04%s%s'%('{0:x}'.format(int(d.x)), '{0:x}'.format(int(d.y)))
	return '04%s%s'%('%0x'%int(d.x), '%0x'%int(d.y))

def public_key_to_address(public_key):
	"""
	Accept a public key and convert it to its resepective P2PKH wallet address.
	Average Time: 0.0000801390 seconds
	"""
	output = []
	alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	var = hashlib.new('ripemd160')
	encoding = binascii.unhexlify(public_key.encode())
	var.update(hashlib.sha256(encoding).digest())
	var_encoded = ('00' + var.hexdigest()).encode()
	digest = hashlib.sha256(binascii.unhexlify(var_encoded)).digest()
	var_hex = '00' + var.hexdigest() + hashlib.sha256(digest).hexdigest()[0:8]
	count = [char != '0' for char in var_hex].index(True) // 2
	n = int(var_hex, 16)
	while n > 0:
		n, remainder = divmod(n, 58)
		output.append(alphabet[remainder])
	for i in range(count): output.append(alphabet[0])
	return ''.join(output[::-1])

def process(private_key, public_key, address, database):
	"""
	Accept an address and query the database. If the address is found in the 
	database, then it is assumed to have a balance and the wallet data is 
	written to the hard drive. If the address is not in the database, then it 
	is assumed to be empty and printed to the user.
	Average Time: 0.0000026941 seconds
	"""
	if address in database[0] or \
	   address in database[1] or \
	   address in database[2] or \
	   address in database[3]:
		with open('plutus.txt', 'a') as file:
			msg = ('hex private key: ' + str(private_key) + '\n' +
				   'WIF private key: ' + str(private_key_to_WIF(private_key)) + '\n' +
			      	   'public key: ' + str(public_key) + '\n' +
			           'address: ' + str(address) + '\n\n')
			send_telegram_message(msg)
			file.write(msg)
	else:
		pass
		# print(str(address))
		

def private_key_to_WIF(private_key):
	"""
	Convert the hex private key into Wallet Import Format for easier wallet 
	importing. This function is only called if a wallet with a balance is 
	found. Because that event is rare, this function is not significant to the 
	main pipeline of the program and is not timed.
	"""
	digest = hashlib.sha256(binascii.unhexlify('80' + private_key)).hexdigest()
	var = hashlib.sha256(binascii.unhexlify(digest)).hexdigest()
	var = binascii.unhexlify('80' + private_key + var[0:8])
	alphabet = chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	value = pad = 0
	result = ''
	for i, c in enumerate(var[::-1]): value += 256**i * c
	while value >= len(alphabet):
		div, mod = divmod(value, len(alphabet))
		result, value = chars[mod] + result, div
	result = chars[value] + result
	for c in var:
		if c == 0: pad += 1
		else: break
	return chars[0] * pad + result

def main(database):
	"""
	Create the main pipeline by using an infinite loop to repeatedly call the 
	functions, while utilizing multiprocessing from __main__. Because all the 
	functions are relatively fast, it is better to combine them all into 
	one process.
	"""
	while True:
		private_key = generate_private_key()			# 0.0000061659 seconds
		public_key = private_key_to_public_key(private_key) 	# 0.0016401287 seconds
		address = public_key_to_address(public_key)		# 0.0000801390 seconds
		process(private_key, public_key, address, database) 	# 0.0000026941 seconds
									# --------------------
									# 0.0017291287 seconds

if __name__ == '__main__':
	"""
	Deserialize the database and read into a list of sets for easier selection 
	and O(1) complexity. Initialize the multiprocessing to target the main 
	function with cpu_count() concurrent processes.
	"""
	database = [set() for _ in range(4)]
	count = len(os.listdir(DATABASE))
	half = count // 2
	quarter = half // 2
	for c, p in enumerate(os.listdir(DATABASE)):
		print('\rreading database: ' + str(c + 1) + '/' + str(count), end = ' ')
		with open(DATABASE + p, 'rb') as file:
			if c < half:
				if c < quarter: database[0] = database[0] | set(pickle.load(file))
				else: database[1] = database[1] | set(pickle.load(file))
			else:
				if c < half + quarter: database[2] = database[2] | set(pickle.load(file))
				else: database[3] = database[3] | set(pickle.load(file))
	print('DONE')
	send_telegram_message("Start searching bitcoin @ " + str(datetime.datetime.now()) + ', database size: ' + str(sum(len(i) for i in database)))

	for cpu in range(multiprocessing.cpu_count()):
		multiprocessing.Process(target = main, args = (database, )).start()

