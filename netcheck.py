#!/usr/bin/python3

"""
Network Checker by Alek3y :)
? Ignore the useless codes dictionary but it might come useful in the future

Usage:
netcheck.py [ -u URL | -c COUNT | -t TIMEOUT | -d DELAY ]
 -u    url (including 'http://') used to check the connectivity [Default: https://google.com]
 -c    how many requets should be sent [Default: 1000]
 -t    maximum amount of time used for each request, in seconds [Default: 4]
 -d    time between each request, in milliseconds [Default: 900]
"""

import os, sys
import time
import requests as req
from colorama import Fore, Style, init

# Default values
URL = "https://google.com"
COUNT = 1000	# How many requets to make
TIMEOUT = 4		# Seconds (will be replaced by an automatic detection)
DELAY = 900		# Milliseconds

FAILSAFE_TIMEOUT = 5		# Timeout in case the detection goes wrong
AUTO_DETECTION_COUNT = 8		# Number of requests used to choose the best timeout 

def usage():
	print(Fore.CYAN + "Usage:" + Style.RESET_ALL)
	print(sys.argv[0] + " [ -u URL | -c COUNT | -t TIMEOUT | -d DELAY ]")
	print(" -u\turl used to check the connectivity [Default: https://google.com]")
	print(" -c\thow many requets should be sent [Default: 1000]")
	print(" -t\tmaximum amount of time used for each request, in seconds [Default: 4]")
	print(" -d\ttime between each request, in milliseconds [Default: 900]")
	sys.exit()

def sleep(ms):
	time.sleep(ms/1000)

# Close both I/O instead of calling sys.exit()
def leave(code):
	try:
		sys.stdin.close()
		sys.stdout.close()
	except:
		pass
	raise SystemExit(code)

# List of HTTP status codes
codes = {
	# 1XX Informational
	100: "Continue",
	101: "Switching Protocols",
	102: "Processing",

	# 2XX Success
	200: "OK",
	201: "Created",
	202: "Accepted",
	203: "Non-authoritative Information",
	204: "No Content",
	205: "Reset Content",
	206: "Partial Content",
	207: "Multi-Status",
	208: "Already Reported",
	226: "IM Used",

	# 3XX Redirection
	300: "Multiple Choices",
	301: "Moved Permanently",
	302: "Found",
	303: "See Other",
	304: "Not Modified",
	305: "Use Proxy",
	307: "Temporary Redirect",
	308: "Permanent Redirect",

	# 4XX Client Error
	400: "Bad Request",
	401: "Unauthorized",
	402: "Payment Required",
	403: "Forbidden",
	404: "Not Found",
	405: "Method Not Allowed",
	406: "Not Acceptable",
	407: "Proxy Authentication Required",
	408: "Request Timeout",
	409: "Conflict",
	410: "Gone",
	411: "Length Required",
	412: "Precondition Failed",
	413: "Payload Too Large",
	414: "Request-URI Too Long",
	415: "Unsupported Media Type",
	416: "Requested Range Not Satisfiable",
	417: "Expectation Failed",
	418: "I'm a teapot",
	421: "Misdirected Request",
	422: "Unprocessable Entity",
	423: "Locked",
	424: "Failed Dependency",
	426: "Upgrade Required",
	428: "Precondition Required",
	429: "Too Many Requests",
	431: "Request Header Fields Too Large",
	444: "Connection Closed Without Response",
	451: "Unavailable For Legal Reasons",
	499: "Client Closed Request",

	# 5XX Server Error
	500: "Internal Server Error",
	501: "Not Implemented",
	502: "Bad Gateway",
	503: "Service Unavailable",
	504: "Gateway Timeout",
	505: "HTTP Version Not Supported",
	506: "Variant Also Negotiates",
	507: "Insufficient Storage",
	508: "Loop Detected",
	510: "Not Extended",
	511: "Network Authentication Required",
	599: "Network Connect Timeout Error",
}

# Setup colorama for Windows
if "nt" in os.name.lower():
	init()

# Set up command line options
manualTimeout = False
for i in range(len(sys.argv)):
	if sys.argv[i] == "-u":
		try:
			URL = sys.argv[i+1]
		except IndexError:
			usage()
		if "http://" not in URL and "https://" not in URL:
			URL = "http://" + URL

	elif sys.argv[i] == "-c":
		try:
			COUNT = int(sys.argv[i+1])
			if COUNT <= 0:
				print(Fore.YELLOW + "Can't use a count less than or equal to zero." + Style.RESET_ALL)
				leave(0)
		except (IndexError, ValueError):
			usage()
	
	elif sys.argv[i] == "-t":
		try:
			manualTimeout = True
			TIMEOUT = float(sys.argv[i+1])
			if TIMEOUT <= 0:
				print(Fore.YELLOW + "Can't use a timeout less than or equal to zero." + Style.RESET_ALL)
				leave(0)
		except (IndexError, ValueError):
			usage()
	
	elif sys.argv[i] == "-d":
		try:
			DELAY = int(sys.argv[i+1])
			if DELAY <= 0:
				print(Fore.YELLOW + "Can't use a delay less than or equal to zero." + Style.RESET_ALL)
				leave(0)
		except (IndexError, ValueError):
			usage()

	elif "-" in sys.argv[i] and i > 0:
		if sys.argv[i-1] != "-u":
			usage()

# Main program with KeyboardInterrupt catching
try:
	# Automatic timeout detection
	isFailsafeActive = False
	if not manualTimeout:
		print(Fore.CYAN + "Choosing the best timeout automatically.." + Style.RESET_ALL)
		try:
			TIMEOUT = 0
			for i in range(AUTO_DETECTION_COUNT):
				_startTime = time.time()
				_testRequest = req.get(URL, stream=False, timeout=FAILSAFE_TIMEOUT)
				_stopTime = time.time()
				if _stopTime - _startTime > TIMEOUT and _testRequest.status_code == 200:
					TIMEOUT = _stopTime - _startTime + 2		# Add 2 seconds in case the network connection drops for a little

			if TIMEOUT == 0:
				raise Exception("Wrong timeout from automatic detection")
		except (req.exceptions.ConnectionError, req.exceptions.ReadTimeout):
			print(Fore.YELLOW + "Something went wrong, using " + str(FAILSAFE_TIMEOUT) + " seconds timeout." + Style.RESET_ALL)
			TIMEOUT = FAILSAFE_TIMEOUT
			isFailsafeActive = True

	# Print set timeout if failsafe wasn't activated
	if not isFailsafeActive:
		print(Fore.CYAN + "Using " + str(round(TIMEOUT, 2)) + " seconds timeout." + Style.RESET_ALL)

	# Sending requests
	for i in range(1, COUNT+1):
		response_color = Fore.RED
		try:
			response = req.get(URL, stream=False, timeout=TIMEOUT)
			response_status = response.status_code
			
			if str(response_status)[0] == "2":		# If success
				response_color = Fore.GREEN

			response_status = str(response_status) + " " + codes[response_status]
		except (req.exceptions.ConnectionError, req.exceptions.ReadTimeout) as e:
			response_status = "Error"

		print(str(i).zfill(len(str(COUNT))) + " | Response: " + response_color + str(response_status) + Style.RESET_ALL)
		sleep(DELAY)
except KeyboardInterrupt:
	print()		# Goes one line after ^C
	print(Fore.YELLOW + "Quitting.." + Style.RESET_ALL)
	leave(0)
