'''
    Scratch Comment Chat Server v1.1.3
    Based on Scratch Comment Viewer Server v2.1.7

    Created by Scratch user, Gaza101.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

from sys import exit as sysexit
if __name__ not in ("__main__","__builtin__"): sysexit()

# === Initialisation ===

import config,scratchapi,scratchcomments
import getpass,time,urllib2,os
from io import open

def info(s,c=0,l=True,v=False,f=True):
    m = '['+["INFO","WARNING","ERROR"][c]+"] "+s
    if (not v) or (v and verbose):
        print m
    if l and logging:
        log.write(unicode(time.strftime("[%H:%M:%S] ",time.gmtime()))+unicode(m)+u'\n')
        if f:
            log.flush()
            os.fsync(log.fileno())

def custom_fallback(prompt="Password: ",stream=None):
    info("Unable to hide password. Make sure no-one else can see your screen!",1,False)
    return getpass._raw_input(prompt)

getpass.fallback_getpass = custom_fallback

ver = "1.1.3"
header = ''.join([hex(ord(c) if ord(c) < 256 else 32)[2:].zfill(2) for c in "Gaza101/Scratch-Comment-Chat/v"+ver])

os.system("cls" if os.name == "nt" else "clear")

print (  "Gaza101's Scratch Comment Chat Server v"+ver
        +"\nWith thanks to Dylan5797 and DadOfMrLog\n" )

emap = {}
new_lc = tuple()
lc = ({"id": 0},)
chatlog = []
idlog = []

# === Configuration ===

default_config = ( {"login_prompt"   : "true" },
                   {"username"       : ''     },
                   {"password"       : ''     },
                   {"project"        : 0      },
                   {"comment_prefix" : '#'    },
                   {"comment_mode"   : 0      },
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

# Characters that a comment must begin with in order to be recognised as a chat
# message. Use '' (with quotation marks) to make all comments a chat message.
# Replies are checked from the beginning of their message (including initial
# tag) therefore this should probably be set to to '' if you wish for replies
# to be reported. This value is case sensitive.
comment_prefix: '#'

# The mode for reporting comments.
# 0 = comments only
# 2 = comments and replies
comment_mode: 0

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
    info("config.yml does not exist or is corrupted. Recreating with default values.",2,False)
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
            info(i.keys()[0]+" key missing from config.yml Recreating with default value.",1,False)
            conf.write(i)

try:
    login_prompt    = bool(    conf.config['login_prompt']    )
    username        = str(     conf.config['username']        )
    password        = str(     conf.config['password']        )
    project         = int(     conf.config['project']         )
    comment_prefix  = unicode( conf.config['comment_prefix']  )
    comment_mode    = int(     conf.config['comment_mode']    )
    delay           = float(   conf.config['delay']           )
    comment_timeout = float(   conf.config['comment_timeout'] )
    visual          = bool(    conf.config['visual']          )
    logging         = bool(    conf.config['logging']         )
    verbose         = bool(    conf.config['verbose']         )
    config_version  = int(     conf.config['config_version']  )
except ValueError:
    info("A key in config.yml has an illegal value. Please fix the value and restart the program.",2,False)
    raw_input("Press enter to exit...")
    sysexit()

info("config.yml loaded.",l=False)

# === Log ===

if logging:
    info("Loading chat.log...",l=False)
    try:
        log = open("chat.log",'a',encoding="utf-8-sig")
    except IOError:
        logging = False
        info("Unable to open chat.log. Continuing with logging disabled.",1)
    else:
        log.write(  u'\n'
                   +unicode(time.strftime(u"%Y-%m-%d %H:%M:%S UTC",time.gmtime()))
                   +u'\n'                                                          )
        info("chat.log loaded.")
else:
    info("Logging is disabled")

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
        except Exception:
            pass
        info("Login failed. Please try again.",2,False)
    info("Successfully logged in with account, "+username+'.')
else:
    info("Automatic login is enabled. Logging into user, "+username+'.')
    for i in range(1,6):
        info("Attempt "+str(i)+"...")
        try:
            scratch = scratchapi.ScratchUserSession(username,password)
            if scratch.tools.verify_session():
                break
        except Exception:
            pass
        if i == 5:
            info("Unsuccessful after five attempts.",2)
            raw_input("Press enter to exit...")
            sysexit()
        time.sleep(1)
    info("Successfully logged in with account, "+username+'.')

# === Main Loop ===

p = scratchcomments.CommentsParser()

info("Initialisation successful.")

while True:
    while True:
        try:
            new_lc = p.parse_project(project,replies=(comment_mode == 2),to=comment_timeout)
        except urllib2.HTTPError as e:
            info("HTTP error "+str(e.code)+" when obtaining comments. Does the project exist?",1,f=False)
            info("Reason: "+str(e.reason),1,v=True)
        except urllib2.URLError as e:
            info("URL error when obtaining comments.",1,f=False)
            info("Reason: "+str(e.reason),1,v=True)
        except Exception as e:
            info("Unknown error when obtaining comments.",1,f=False)
            info("Reason: "+str(e.__class__.__name__),1,v=True)
        else:
            if len(new_lc) != 0 and lc[0]['id'] != new_lc[0]['id']:
                lc = new_lc
                for i in reversed(lc):
                    if (     i['id'] not in idlog
                         and i['msg'][:len(comment_prefix)] == comment_prefix ):
                        idlog.insert(0,i['id'])
                        chatlog.insert(0,'')
                        for k in ("type","id","user","msg"):
                            for c in unicode(i[k]):
                                if ord(c) > 255:
                                    break
                                else:
                                    chatlog[0] += hex(ord(c))[2:].zfill(2)
                            else:
                                chatlog[0] += "00"
                                continue
                            break
                        if ord(c) > 255:
                            del idlog[0],chatlog[0]
                            continue
                        info("New "+i['type']+"! ID: "+str(i['id']),v=True,f=False)
                        info("Author: "+i['user'],v=True,f=False)
                        try:
                            info(u"Body: "+i['msg'][len(comment_prefix):],v=True,f=False)
                        except UnicodeEncodeError:
                            info("Unable to display comment.",1,v=True,f=False)
                        info("Encoded: "+(chatlog[-1][:30]+"..." if len(chatlog[-1]) > 30 else chatlog[-1]),v=True,f=False)
                if logging:
                    log.flush()
                    os.fsync(log.fileno())
                while sum([len(i) for i in chatlog]) > 10237-len(header):
                    del idlog[-1],chatlog[-1]
                if not visual:
                    info("Sending encoded data...",v=True,f=False)
                    try:
                        scratch.cloud.set_var("scratchchat","0x"+header+"00"+''.join(chatlog),project)
                    except Exception:
                        info("Failed to send encoded data.",1)
                    else:
                        info("Successful!",v=True)
        if not visual:
            try:
                if not scratch.tools.verify_session():
                    raise Exception
            except Exception:
                break
        time.sleep(delay)
    info("Session invalidated. Did Scratch go down?",1)
    while True:
        if not verbose:
            info("Attempting to start new session...",l=False)
        for i in range(1,6):
            info("Attempting to start new session... (Attempt "+str(i)+')',v=True)
            try:
                scratch = scratchapi.ScratchUserSession(username,password)
                if scratch.tools.verify_session():
                    info("Successful!")
                    break
            except Exception:
                pass
            if i == 5:
                info("Unsuccessful. Sleeping for one minute.",1)
            else:
                time.sleep(delay)
        try:
            if scratch.tools.verify_session():
                break
        except Exception:
            pass
        time.sleep(60)
