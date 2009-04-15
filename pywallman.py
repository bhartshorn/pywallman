#!/usr/bin/env python

import os, string, sys, urllib, urlparse, hashlib, sqlite3
from time import strftime
from optparse import OptionParser

## Defaults
# default_savedir is where you want to save your wallpapers when downloaded.
# The script looks for genre specified with -g under this dir and saves it there.
# Leave a trailing slash (eg. "~/pictures/wallpapers/")
default_savedir = "~/pictures/wallpapers/test/"
default_database = "~/.pywallman/walls.db"

parser = OptionParser()
parser.add_option("-g", "--genre", dest="genre", default="", help="Define which 'genre' or subdirectory to save a wallpaper in")
parser.add_option("-f", "--file", dest="filename", default="", help="Changes output name of file downloaded - make SURE you set correct extension", metavar="FILE")
parser.add_option("-u", "--url", dest="fetch_url", default="", help="Set the url from which the script will fetch an image")
parser.add_option("-d", "--desc", dest="description", default="", help="Set the description for the wallpaper - stick to 1 or 2 descriptive words")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="Don't print status messages to stdout")
parser.add_option("-l", "--local", dest="local", default="", help="Performs actions on local wallpapers")
parser.add_option("-c", "--create", action="store_true", dest="create_dir", default=False, help="Create directory for genre")
parser.add_option("-p", "--print", action="store_true", dest="print_walls", default=False, help="Print all current wallpapers")


(options, args) = parser.parse_args()

def scriptStatus(status):
	# Checks if quiet is set, and if not, prints the status message
	if options.verbose:
		print status
		return True
	else:
		return False

def downloadWall(url, path):
	# Actually download the wallpaper file, given the url and the path to save to
	urllib.urlretrieve(url, path)
	return True

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
			# Make sure we won't overwrite an existing file
			scriptStatus("PathChecker: File already exists")
			return False
		else:
			scriptStatus("PathChecker: Full path is  " + full_path)
			return True
	else:
		scriptStatus("PathChecker: Path/Genre doesn't exist or isn't a directory")
		return False

def checkDataBase(db_path):
	if not os.path.exists(db_path):
		scriptStatus("DatabaseChecker: database doesn't exist, creating")
		sql_conn = sqlite3.connect(db_path)
		sql_curs = sql_conn.cursor()
		sql_curs.execute('''CREATE TABLE wallpapers(date text, md5 text, description text, path text)''')
		sql_conn.commit()
		sql_curs.close()
		sql_conn.close()
		return 1
	elif os.path.exists(db_path) and os.path.isfile(db_path):
		scriptStatus("DatabaseChecker: database exists, loading and pickling data")
		return 1
	elif os.path.exists(db_path) and os.path.isdir(db_path):
		scriptStatus("DatabaseChecker: Database path is a directory - exiting")
		return 0
	else:
		scriptStatus("DatabaseChecker: Unknow error - exiting")
		return 0

def printDataBase(db_path):
	scriptStatus("DatabasePrinter: Connecting to database")
	sql_conn = sqlite3.connect(db_path)
	sql_curs = sql_conn.cursor()
	sql_result = sql_curs.execute('''SELECT * FROM wallpapers''').fetchall()
	print sql_result
	sql_conn.commit()
	sql_curs.close()
	sql_conn.close()

def saveData(db_path, path, description, date):
	image_file = open(path, "rb")
	image_md5 = hashlib.md5(image_file.read()).hexdigest()
	image_file.close()
	scriptStatus("Save: md5 of image is " + image_md5)
	if options.description == "":
		options.description = options.filename

	sql_conn = sqlite3.connect(db_path)
	sql_curs = sql_conn.cursor()
	sql_result = sql_curs.execute('''SELECT * FROM wallpapers WHERE md5 = ?''', (image_md5,)).fetchone()

	if sql_result:
		image_info = (options.description, path)
		scriptStatus("Save: record already exists, updating info, please delete old image if it moved")
		print sql_result
		sql_curs.execute('''UPDATE wallpapers SET description = ?, path = ?''', image_info)
	else:
		image_info = (strftime("%Y-%m-%d %H:%M:%S"), image_md5, options.description, path)
		sql_curs.execute('''INSERT INTO wallpapers VALUES(?,?,?,?)''', image_info)
	sql_conn.commit()
	sql_curs.close()
	sql_conn.close()

def main():
	# Main program logic
	db_path = os.path.expanduser(default_database)
	if options.print_walls:
		scriptStatus("Main: Printing all wallpapers on system")
		if checkDataBase(db_path):
			printDataBase(db_path)
	elif not options.local == "" and checkDataBase(db_path):
		scriptStatus("Main: Adding local image to database")
		saveData(db_path, options.local, options.description, "")
	elif not options.fetch_url == "" and checkPath():
		scriptStatus("Main: Found url on cmd line - parsing and checking for genre")
		if downloadWall(options.fetch_url, full_path) and checkDataBase(db_path):
			saveData(db_path, full_path, options.description, "")
	else:
		scriptStatus("Nothing to do - exiting")

if __name__ == '__main__': main()
