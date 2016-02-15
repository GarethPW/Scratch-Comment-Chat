'''
    Scratch Comment Chat Server v1.0.0
    Based on Scratch Comment Viewer Server v2.1.2

    Created by Scratch user, Gaza101.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

from sys import exit as sysexit
if __name__ != "__main__": sysexit()

# === Initialisation ===

import config,scratchapi,scratchcomments
import getpass,time,urllib2
from os import system
from io import open

def info(s,c=0,l=True,v=False):
    m = '['+["INFO","WARNING","ERROR"][c]+"] "+s
    if (not v) or (v and verbose):
        print m
    if l and logging:
        log.write(unicode(time.strftime("[%H:%M:%S] ",time.gmtime()))+unicode(m)+u'\n')

def csreplace(s,o,n=''):
    for i in o: #For every find character,
        s = s.replace(i,n) #Replace with the new character.
    return s

emap = {}
new_lc = tuple()
lc = tuple()
enc = str()

# === Configuration ===

default_config = ( {"login_prompt"   : "true" },
                   {"username"       : ''     },
                   {"password"       : ''     },
                   {"project"        : 0      },
                   {"delay"          : 1      },
                   {"comment_timeout": 10     },
                   {"visual"         : "false"},
                   {"logging"        : "true" },
                   {"verbose"        : "true" },
                   {"config_version" : 1      }  )
default_config_u = (
u'''# Prompt for login? Set to false to automagically login with preset username and
# password.
login_prompt: true

# Details used to log into Scratch if login_prompt has been set to false.
# Surround your password with quotation marks if it has whitespace at the start
# or end.
username: 
password: 

# Project ID to monitor comments on.
project: 0

# The time between each check for comments in seconds. It is recommended that
# this is not set below 1.
delay: 1

# The maximum amount of time that the program can spend retrieving the comment
# data in seconds. Leave this at 10 if you're unsure.
comment_timeout: 10

# If visual mode is enabled, the program will not attempt to log into Scratch
# but will serve as a comment monitor instead.
visual: false

# If logging is enabled, data such as comment detection will be recorded to the
# comment.log file.
logging: true

# If verbose mode is enabled, information that would normally be recorded in the
# log alone will also be disabled in the console.
verbose: true

# Do not change this value! Seriously - it could reset your config.
config_version: 1''')

info("Loading config.yml...",l=False)

conf = config.Config("config.yml")

if (    "config_version" not in conf.config
     or conf.config['config_version'] not in (1,)
     or tuple in [type(conf.config[i]) for i in conf.config]    ):
    info("config.yml does not exist or is corrupted. Recreating with default values.",2,l=False)
    with open(conf.name,'r') as c, open(conf.name+".broken",'w') as b:
        c.seek(0)
        b.write(c.read())
        c.close()
        b.close()
    with open(conf.name,'w') as f:
        f.write(default_config_u)
        f.close()
    info("Please fill in config.yml appropriately and restart the program afterwards.",l=False)
    raw_input("Press enter to exit...")
    sysexit()
else:
    for i in default_config[:-1]:
        if i.keys()[0] not in conf.config:
            info(i.keys()[0]+" key missing from config.yml Recreating with default value.",1,l=False)
            conf.write(i)

try:
    login_prompt    = bool(  conf.config['login_prompt']    )
    username        = str(   conf.config['username']        )
    password        = str(   conf.config['password']        )
    project         = int(   conf.config['project']         )
    delay           = float( conf.config['delay']           )
    comment_timeout = float( conf.config['comment_timeout'] )
    visual          = bool(  conf.config['visual']          )
    logging         = bool(  conf.config['logging']         )
    verbose         = bool(  conf.config['verbose']         )
    config_version  = int(   conf.config['config_version']  )
except ValueError:
    info("A key in config.yml has an illegal value. Please fix the value and restart the program.",2,l=False)
    raw_input("Press enter to exit...")
    sysexit()

info("config.yml loaded.",l=False)

# === Log ===

if logging:
    info("Loading comment.log...",l=False)
    try:
        log = open("comment.log",'a',encoding="utf-8-sig")
    except IOError:
        info("Unable to open comment.log. Continuing with logging disabled.",1)
        logging = False
    else:
        log.write(  u'\n'
                   +unicode(time.strftime(u"%Y-%m-%d %H:%M:%S UTC",time.gmtime()))
                   +u'\n'                                                          )
        info("comment.log loaded.")
else:
    info("Logging is disabled")

# === Emoticon Map ===

info("Loading emap.txt...")

try:
    with open("emap.txt",'r') as f:
        mi = []
        for l in f:
            mi = csreplace(l,"\r\n").split(" | ")
            if len(mi) == 2:
                emap[mi[1]] = mi[0]
        del mi
        f.close()
except IOError:
    info("Unable to load emap.txt. Continuing regardless.",1)
else:
    info("emap.txt loaded.")

# === Authentication ===

if visual:
    info("Visual mode is enabled. Skipping authentication.")
elif login_prompt:
    while True:
        username = raw_input("[PROMPT] Username: ")
        password = getpass.getpass("[PROMPT] Password: ")
        try:
            scratch = scratchapi.ScratchUserSession(username,password)
            if scratch.tools.verify_session():
                break
        except StandardError:
            pass
        info("Login failed. Please try again.",2,l=False)
    info("Successfully logged in with account, "+username+'.')
else:
    info("Automatic login is enabled. Logging into user, "+username+'.')
    for i in range(1,6):
        info("Attempt "+str(i)+"...")
        try:
            scratch = scratchapi.ScratchUserSession(username,password)
            if scratch.tools.verify_session():
                break
        except StandardError:
            pass
        if i == 5:
            info("Unsuccessful after five attempts.",2)
            raw_input("Press enter to exit...")
            sysexit()
        time.sleep(1)
    info("Successfully logged in with account, "+username+'.')

# === Main Loop ===

p = scratchcomments.CommentsParser(emap)

info("Initialisation successful.")

while True:
    while True:
        try:
            new_lc = p.parse(project,1,to=comment_timeout)[0]
        except urllib2.HTTPError as e:
            info("HTTP Error "+str(e.code)+" when obtaining comments. Does the project exist?",1)
            info("Reason: "+str(e.reason),1,v=True)
        except urllib2.URLError as e:
            info("URL Error when obtaining comments.",1)
            info("Reason: "+str(e.reason),1,v=True)
        else:
            if lc != new_lc:
                lc = new_lc
                enc = ''.join(  [str(ord(c) if ord(c) < 256 else 32).zfill(3) for c in lc['user']]
                               +["000"]
                               +[str(ord(c) if ord(c) < 256 else 32).zfill(3) for c in lc['msg']]  )
                info("New comment! Author: "+lc['user'],v=True)
                try:
                    info(lc['msg'],v=True)
                except UnicodeEncodeError:
                    info("Unable to display comment.",1)
                info("Encoded: "+(enc[:30]+"..." if len(enc) > 30 else enc),v=True)
                if not visual:
                    try:
                        scratch.cloud.set_var("latest_comment",enc,project)
                    except StandardError:
                        info("Failed to send encoded data.",1)
        if not visual:
            try:
                if not scratch.tools.verify_session():
                    raise StandardError
            except StandardError:
                break
        time.sleep(delay)
    info("Session invalidated. Did Scratch go down?",1)
    while True:
        for i in range(1,6):
            info("Attempting to start new session... (Attempt "+str(i)+')')
            try:
                scratch = scratchapi.ScratchUserSession(username,password)
                if scratch.tools.verify_session():
                    info("Successful!")
                    break
            except StandardError:
                pass
            if i == 5:
                info("Unsuccessful. Sleeping for one minute.",1)
            time.sleep(delay)
        try:
            if scratch.tools.verify_session():
                break
        except StandardError:
            pass
        time.sleep(59)
