import scratchapi
from time import sleep
from sys import exit as sysexit
from urllib2 import urlopen
from os import system
from HTMLParser import HTMLParser

scratch = scratchapi.ScratchUserSession(raw_input("Username: "),raw_input("Password: "))
system("cls")
if not scratch.tools.verify_session():
    sysexit()

p = HTMLParser()

new_lc = tuple()
lc = tuple()
enc = str()
emap = {}

def csreplace(s,o,n=''):
    for i in o: #For every find character,
        s = s.replace(i,n) #Replace with the new character.
    return s

def emreplace(s,m=emap):
    for i in m:
        s = s.replace(i,m[i])
    return s

with open("emap.txt",'r') as f:
    mi = []
    for l in f:
        mi = csreplace(l,"\r\n").split(" | ")
        emap[mi[1]] = mi[0]

while True:
    try:
        comments = urlopen("https://scratch.mit.edu/site-api/comments/project/96895524/").read() #96895524
        new_lc = (p.unescape(comments[comments.index('data-comment-user="')+19:comments.index('"',comments.index('data-comment-user="')+19)]),
                  emreplace(p.unescape(comments[comments.index('<div class="content">')+44:comments.index('</div>',comments.index('<div class="content">')+21)-12])))
        if lc != new_lc:
            lc = new_lc
            enc = ''.join([str(ord(c)).zfill(3) for c in lc[0]]
                         +["128"]
                         +[str(ord(c)).zfill(3) for c in lc[1]])
            print scratch.cloud.set_var("latest_comment",enc,96895524)
            print '\n'+lc[0]+'\n'+lc[1]+'\n\n'+(enc[:30]+"..." if len(enc) > 30 else enc)+'\n'
    except:
        pass
    sleep(1)
