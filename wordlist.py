#!/usr/bin/python
import sys, re, hashlib, getopt
import os, subprocess

debug = False
	
def start_attack(address, addresses_filename, dictionary_filename):
	try:
		wordlist = open(dictionary_filename, "r")
	except(IOError):
		print "[-] Error: Check your dictionary file path.\n"
		sys.exit(1)

	words = wordlist.readlines()
	print "\n",len(words),"words loaded..."
	
	if not address:
		try:
			addresslist = open(addresses_filename, "r")
		except(IOError):
			print "[-] Error: Check your address list path.\n"
			sys.exit(1)
		
		addresses = addresslist.readlines()
		print "\n",len(addresses),"addresses loaded..."
		i = 1
		length = len(addresses)
		
		for address in addresses:
			i += 1
			percent = float(i) / float(length) * 100.
			address = address.rstrip(' \n\r' );
			sys.stdout.write("\r Trying Address: " + address + " Overall Percentage: " + str(percent))
			sys.stdout.flush()
			dict_attack(address, words)
	else: 
		dict_attack(address,words, 100.)
			

# Check hash length
def chklength(address):
	
	if len(address.rstrip(' \n\r' )) != 34:
		print "[-] Improper length for a bitcoin address hash."
		return -1

# Attempts to crack hash against any givin wordlist.
def dict_attack(address, words):
	if chklength(address) == -1:
		return
	#wordlist = raw_input("\nPlease specify wordlist path: ")
	length = len(words)
	i = 1
	for word in words:
		#if (i % 100) == 0:
		#	sys.stdout.write("\r Wordlist Progress for Address: " + str(float(i)/float(length)*100)[:5] + "%")
		i += 1
		hash = hashlib.sha256(word)
		value = hash.hexdigest()
		
		proc = subprocess.Popen(["./bx","ec-to-public", "-u",value], stdout=subprocess.PIPE)
		tmp = proc.stdout.read()
		
		proc = subprocess.Popen(["./bx","sha256", tmp.rstrip('\n\r')], stdout=subprocess.PIPE)
		tmp = proc.stdout.read()

		proc = subprocess.Popen(["./bx","ripemd160", tmp.rstrip('\n\r')], stdout=subprocess.PIPE)
		tmp = proc.stdout.read()

		proc = subprocess.Popen(["./bx","address-encode", tmp.rstrip('\n\r')], stdout=subprocess.PIPE)
		tmp = proc.stdout.read()

		if debug:
			print "Trying: "+ word + "ECDSA Private Key: " + value + "Address: " + tmp
					
		if address == value:
			print "[+] Password is:"+word,"\n"
			sys.exit(0)

def main():
	global debug
	address = ""
	input_filename = ""
	addresses_filename = ""

	print 'ARGV      :', sys.argv[1:]

	try:
		options, remainder = getopt.getopt(sys.argv[1:], 'a:c:df:', ['crack=', 
															 'debug',
															 'wfile=',
															 'afile='
															 ])
	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)
		
	print 'OPTIONS   :', options

	for opt, arg in options:
		if opt in ('-c', '--crack'):
			address = arg
		elif opt in ('-f', '--wfile'):
			input_filename = arg
		elif opt in ('-a', '--afile'):
			addresses_filename = arg
		elif opt in ('-d','--debug'):
			debug = True

	if addresses_filename and address:
		print "Either specify address (-c) or list of addresses (-a,--afile)"
		sys.exit(3)

	print "HASH TO CRACK :", address
	print 'DEBUG :', debug
	print 'WORDLIST FILE :', input_filename
	print 'REMAINING :', remainder
	print 'ADDRESS FILE ', addresses_filename


	if (address or addresses_filename) and input_filename:
		start_attack(address, addresses_filename, input_filename)
		
	print "Did not succeed :("
if __name__ == "__main__":
	main()
