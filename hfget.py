#!/usr/bin/env python

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


import urllib
import os
import sys
import hashlib
import ConfigParser
import re

apiUrl = 'http://api.hotfile.com/?'

args = sys.argv;

username = ''
passwd = ''
download_dir = '.'

linkfile = ''
link = ''
links = []

def isPremiumAccount():
  action = 'action=getuserinfo&' + preparePassword()
  request = apiUrl + action
  f = urllib.urlopen(request)
  if not (re.match('.*premium=1.*', f.read())):
    return 0
  return 1

def getHotfileLinksFromUrl(url):
  regex = re.compile('<a href="(http://hotfile.com/dl/\d*?/[a-z,0-9]*?/.*?)"')
  f = urllib.urlopen(url)
  return regex.findall(f.read())

def checkAvailable(link):
  action = 'action=checklinks&fields=status&links=' + link
  request = apiUrl + action
  f = urllib.urlopen(request)
  if f.read().strip() == '1':
    return 1
  else:
    return 0

def getDigest():
  action = 'action=getdigest'
  request = apiUrl + action
  f = urllib.urlopen(request)
  return f.read().strip()
  
def preparePassword():
  digest = getDigest()
  md5pw = hashlib.md5(password).hexdigest()
  return 'username=' + username + '&passwordmd5dig=' + hashlib.md5(md5pw + digest).hexdigest() + '&digest=' + digest

def getDirectLink(link):
  request = apiUrl + 'action=getdirectdownloadlink&link=' + link + '&' + preparePassword()
  f = urllib.urlopen(request)
  return f.read().strip()

def isVaildHotfileLink(link):
  if re.match('http://hotfile.com/dl/\d*?/[a-z,0-9]*?/.*?', link):
    return 1
  return 0

if '-h' in args or len(args) == 1:
  print 'Usage: ' + args[0] + ' options link || linkslist'
  print '\tOptions: '
  print '\t-h help'
  print '\t-d download directory e.g. /home/user/downloads; default is "."'
  print '\t-c only check if file is online, do not download it'
  print '\t-l linklist'
  print '\t-p parse url for hotfile links'
  exit()

#check if username and password are given as command line options
if '-u' in args and '-p' in args:
  username = args[args.index('-u') + 1]
  password = args[args.index('-p') + 1]
else:
  #check for config file
  if os.path.exists(os.environ['HOME'] + '/.hfget.conf'):
    #load config file
    Config = ConfigParser.ConfigParser()
    Config.read(os.environ['HOME'] + '/.hfget.conf')
    username = Config.get('account', 'username')
    password = Config.get('account', 'password')
    if Config.has_option('account', 'download_dir'):
      download_dir = Config.get('account', 'download_dir')
  else:
    exit('no login information found')

if '-d' in args:
  download_dir = args[args.index('-d') + 1]

if '-p' in args:
  links = getHotfileLinksFromUrl(args[args.index('-p') + 1])


if '-l' not in args and '-p' not in args and len(args) > 1:
  tmplink = args[len(args) - 1]
  if not isValidHotfileLink(tmplink):
    exit(tmplink + ' is not a valid hotfile.com link')
  links.append(tmplink)
 
if '-l' in args:
 if args.index('-l') >= (len(args) - 1):
   exit('missing argument for -l')
 else:
   linkfile = args[args.index('-l') + 1]
   
if linkfile.strip() != '':
  input = open(linkfile, 'r')
  for line in input:
    if line == '' or not line.startswith('http://hotfile.com'):
      continue
    links.append(line.strip())

#check if it's a premium account
#if not, exit
if not isPremiumAccount():
  exit('wrong login information or account is not premium')    

if '-c' in args:
  for link in links:
    if not checkAvailable(link):
      print link + ' [offline]'
      continue
    print link
else:
  for link in links:
    if not checkAvailable(link):
      print link + ' [offline]'
      continue
    else:
      dlink = getDirectLink(link)
      filename_explode = link.split('/')
      filename = filename_explode[len(filename_explode) - 1]
      if filename.endswith('.html'):
        filename = filename[0:len(filename) - 5]
      print 'wget -c -O ' + download_dir + '/' + filename + ' ' + link
      os.system('wget -c -O ' + download_dir + '/' + filename + ' ' + dlink)
  
  


