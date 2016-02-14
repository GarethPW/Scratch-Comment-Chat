'''
    Scratch Comment Viewer Server v2.0.0

    Created by Scratch user, Gaza101.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

import scratchapi,scratchcomments,time,getpass,codecs,urllib2
from os import system

def info(s,c=0,l=True,v=False):
    m = '['+["INFO","WARNING"][c]+"] "+s
    if (not v) or (v and verbose):
        print m
    if logging and l:
        log.write(time.strftime("[%H:%M:%S] ",time.gmtime())+m+'\n')

def csreplace(s,o,n=''):
    for i in o: #For every find character,
        s = s.replace(i,n) #Replace with the new character.
    return s

emap = {}
new_lc = tuple()
lc = tuple()
enc = str()

verbose = True
logging = True

login = (raw_input("Username: "),getpass.getpass("Password: "))
system("cls")
scratch = scratchapi.ScratchUserSession(login[0],login[1])
while not scratch.tools.verify_session():
    info("Login failed! Please try again.",l=False)
    login = (raw_input("Username: "),getpass.getpass("Password: "))
    system("cls")
    scratch = scratchapi.ScratchUserSession(login[0],login[1])
info("Login successful!",l=False)

if logging:
    try:
        log = codecs.open("comment.log",'a',encoding="utf-8-sig")
        log.write(  '\n'
                   +time.strftime("%Y-%m-%d %H:%M:%S UTC",time.gmtime())
                   +'\n'                                                 )
    except:
        info("Unable to open comment.log! Continuing with logging disabled.",1)
        logging = False

try:
    with open("emap.txt",'r') as f:
        mi = []
        for l in f:
            mi = csreplace(l,"\r\n").split(" | ")
            emap[mi[1]] = mi[0]
        del mi
        f.close()
        info("emap.txt loaded")
except IOError:
    info("emap.txt not found! Continuing regardless.",1)

p = scratchcomments.CommentsParser(emap)

while True:
    while scratch.tools.verify_session():
        try:
            new_lc = p.parse(96895524,1)[0] #96895524
            if lc != new_lc:
                lc = new_lc
                enc = ''.join(  [str(ord(c) if ord(c) < 256 else 32).zfill(3) for c in lc['user']]
                               +["000"]
                               +[str(ord(c) if ord(c) < 256 else 32).zfill(3) for c in lc['msg']]  )
                try:
                    scratch.cloud.set_var("latest_comment",enc,96895524)
                    info("New comment! Author: "+lc['user'],v=True)
                    info(lc['msg'],v=True)
                    info("Encoded: "+(enc[:30]+"..." if len(enc) > 30 else enc),v=True)
                except:
                    info("Failed to send encoded data!",1)
        except urllib2.URLError as e:
            info("URL Error when obtaining comments.",1)
            info("Reason: "+e.reason,1,v=True)
        except urllib2.HTTPError as e:
            info("HTTP Error "+str(e.code)+" when obtaining comments.",1)
            info("Reason: "+e.reason,1,v=True)
        time.sleep(1)
    info("Session invalidated. Did Scratch go down?",1)
    while not scratch.tools.verify_session():
        for i in range(1,6):
            scratch = scratchapi.ScratchUserSession(login[0],login[1])
            info("Attempting to start new session... (Attempt "+str(i)+')')
            if scratch.tools.verify_session():
                info("Successful!")
                break
            elif i == 5:
                info("Unsuccessful! Sleeping for one minute.",1)
            time.sleep(1)
        if not scratch.tools.verify_session():
            time.sleep(59)
