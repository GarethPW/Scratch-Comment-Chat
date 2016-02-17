'''
    Scratch Project Comments Parser v1.1.0
    Created for use with SCV Server v2.1.6

    Created by Scratch user, Gaza101.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from urllib2 import urlopen

class CommentsParser(HTMLParser):
    def __init__(self,emap={}):
        self.emap = emap
        self.out = []
        self.nest = []
        self.comments = str()
    def aDict(self,a): #Converts attrs into dict format for easier parsing.
        d = {} #        e.g.    [('class', 'example'),('height', '50px')]
        for i in a: #   becomes  {'class':('example',),'height':('50px',)}
            if i[0] in d:
                d[i[0]] += (i[1],)
            else:
                d[i[0]] = (i[1],)
        return d
    def isLegal(self,n,r): #Checks the nest based on a set of rules provided.
        try: # Rule format: [(#tuple of tag nest - can be any length - starts from root tag),(#level of nest, #attr, #value)]
            if (     tuple([i[0] for i in n][:len(r[0])]) == r[0]
                 and not (False in [(True in [sr[2] in i for i in n[sr[0]][1][sr[1]]]) for sr in r[1:]]) ):
                return True
        except KeyError:
            pass
        return False
    def isCName(self,n): #Checks if the current nest is valid to be the comment username.
        return self.isLegal(n,[ ("li","div","div","div",'a'),
                                (0,"class","top-level-reply"),
                                (1,"class","comment"),
                                (2,"class","info"),
                                (3,"class","name")             ])
    def isCBody(self,n): #Checks if the current nest is valid to be the comment body.
        return self.isLegal(n,[ ("li","div","div","div"),
                                (0,"class","top-level-reply"),
                                (1,"class","comment"),
                                (2,"class","info"),
                                (3,"class","content")          ])
    def handle_starttag(self, tag, attrs):
        il = (self.isCName(self.nest),self.isCBody(self.nest))
        self.nest.append((tag,self.aDict(attrs)))
        if il != (self.isCName(self.nest),self.isCBody(self.nest)): #Check if a new comment username or body has begun.
            if self.isCName(self.nest) and not il[0]:
                self.out.append([self.nest[-4][1]['data-comment-id'][0]]) #If a new comment username has begun, append comment id to output array.
            self.out.append([]) #If a new comment username or body has begun, append new list to output array.
        if tag == "img": #If the tag is valid to be an emoticon,
            if (     self.isCBody(self.nest)
                 and self.isLegal(self.nest,[ tuple(),
                                              (-1,"class","easter-egg") ]) ):
                try:
                    self.out[-1].append(self.emap[self.nest[-1][1]['src'][0]]) #Attempt to match with its alias in the emoticon map.
                except KeyError:
                    self.out[-1].append("_undefined_") #If alias not found, refer to it as "_undefined_"
            self.nest.pop() #Remove image from nest array since it's most likely without an end tag.
    def handle_endtag(self,tag):
        if tag != "img": #Ignore img end tags since they will have already been dealt with.
            self.nest.pop()
    def handle_data(self,data):
        if self.isCName(self.nest) or self.isCBody(self.nest): #If we're in valid comment text,
            self.out[-1].append(data) #Append text to output.
    def handle_entityref(self,name):
        if self.isCName(self.nest) or self.isCBody(self.nest): #If we're in valid comment text,
            self.out[-1].append(unichr(name2codepoint[name])) #Append text to output.
    def handle_charref(self,name):
        if self.isCName(self.nest) or self.isCBody(self.nest): #If we're in valid comment text,
            self.out[-1].append(unichr(int(name[1:],16) if name[0] == 'x' else int(name))) #Append text to output.
    def parse(self,data,max_comments=30,page=1,to=1): #Parses any data given. Data must be complete.
        if self.comments != data: #If we haven't already parsed this,
            self.comments = data
            self.out = [] #Reinitialise the instance.
            self.nest = []
            self.reset() #Reset the parser.
            self.feed(self.comments) #Feed the parser the data from the comments of the project specified.
            self.out =  tuple( [{  "id": int(self.out[i][0]), #Convert parsed data into a more usable format. e.g. ({'id': 54852378, 'user': 'Gaza101', 'msg': '_waffle_'}, ...)
                                 "user": u''.join([u''.join([unichr(ord(c)) for c in m]) for m in self.out[i+1]]),
                                  "msg": u''.join([u''.join([unichr(ord(c)) for c in m]) for m in self.out[i+2]])[23:-12]} for i in range(0,min(len(self.out),max_comments),3)] )
        return self.out #Output parsed data.
    def parse_project(self,project_id,max_comments=30,page=1,to=1): #Parses any data given. Data must be complete.
        comments = urlopen("https://scratch.mit.edu/site-api/comments/project/"+str(project_id)+"/?page="+str(page),timeout=to).read()
        return self.parse(comments,max_comments,page,to)
    def parse_user(self,user,max_comments=30,page=1,to=1): #Parses any data given. Data must be complete.
        comments = urlopen("https://scratch.mit.edu/site-api/comments/user/"+user+"/?page="+str(page),timeout=to).read()
        return self.parse(comments,max_comments,page,to)
