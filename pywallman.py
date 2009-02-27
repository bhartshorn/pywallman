#!/usr/bin/env python

import os, string, sys, urllib, urlparse
from time import localtime
from optparse import OptionParser

## Defaults
# default_savedir is where you want to save your wallpapers when downloaded. 
# The script looks for genre specified with -g under this dir and saves it there.
# Leave a trailing slash (eg. "~/pictures/wallpapers/")
default_savedir = "~/pictures/wallpapers/test/"

parser = OptionParser()
parser.add_option("-g", "--genre", dest="genre", default="", help="Define which 'genre' or subdirectory to save a wallpaper in")
parser.add_option("-f", "--file", dest="filename", default="", help="Changes output name of file downloaded - make SURE you set correct extension", metavar="FILE")
parser.add_option("-u", "--url", dest="fetch_url", default="", help="Set the url from which the script will fetch an image")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="Don't print status messages to stdout")
parser.add_option("-l", "--local", action="store_true", dest="local", default=False, help="Performs actions on local wallpapers")
parser.add_option("-c", "--create", action="store_true", dest="create_dir", default=False, help="Create directory for genre")

(options, args) = parser.parse_args()

def scriptStatus(status):
	# Checks if quiet is set, and if not, prints the status message
	if options.verbose:
		print status
		return True
	else:
		return False

def downloadWall(url, path):
	# Actually downloads the wallpaper file, given 
	urllib.urlretrieve(url, path)

def checkPath():
	global full_path
	global options
	full_path = os.path.expanduser(os.path.join(default_savedir,  options.genre))

	if os.path.exists(full_path) and os.path.isdir(full_path):
		if not options.filename == "":
			# If a filename was passed, use it
			full_path = os.path.join(full_path, options.filename)
		else:
			# Else get the filename from the url
			options.filename = os.path.basename(urlparse.urlparse(options.fetch_url).path)
			full_path = os.path.join(full_path, options.filename)

		if os.path.exists(full_path):
			scriptStatus("File already exists")
			return False
		else:
			scriptStatus("Path: " + full_path)
			return True
	else:
		scriptStatus("Path/Genre doesn't exist or isn't a directory")
		return False

def pickleData(path, description, date):
	if description == "":
		description


# Main program logic
if not options.fetch_url == "" and checkPath():
	scriptStatus("Found url on cmd line - parsing and checking for genre")
	downloadWall(options.fetch_url, full_path)
else:
	scriptStatus("Nothing to do - exiting")
