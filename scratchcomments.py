'''
    Scratch Project Comments Parser v1.2.3
    Created for use with SCC Server v1.1.3

    Created by Scratch user, Gaza101.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from urllib2 import urlopen
from hashlib import md5

class CommentsParser(HTMLParser):
    def __init__(self):
        self.out = []
        self.nest = []
        self.comments = str()
        self.replies = bool()
        self.max_comn = int()
        self.comn = int()
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
                 and all(any(sr[2] in i for i in n[sr[0]][1][sr[1]]) for sr in r[1:]) ):
                return True
        except KeyError:
            pass
        return False
    def isCName(self,n): #Checks if the current nest is valid to be a comment username.
        return (     self.comn <= self.max_comn
                 and self.isLegal(n,[ ("li","div","div","div",'a'),
                                (0,"class","top-level-reply"),
                                (1,"class","comment"),
                                (2,"class","info"),
                                (3,"class","name")             ])   )
    def isCBody(self,n): #Checks if the current nest is valid to be a comment body.
        return (     self.comn <= self.max_comn
                 and self.isLegal(n,[ ("li","div","div","div"),
                                (0,"class","top-level-reply"),
                                (1,"class","comment"),
                                (2,"class","info"),
                                (3,"class","content")          ]) )
    def isRName(self,n): #Checks if the current nest is valid to be a reply username.
        return (     self.comn <= self.max_comn
                 and self.replies
                 and self.isLegal(n,[ ("li","ul","li","div","div","div",'a'),
                                      (0,"class","top-level-reply"),
                                      (1,"class","replies"),
                                      (2,"class","reply"),
                                      (3,"class","comment"),
                                      (4,"class","info"),
                                      (5,"class","name")                      ]) )
    def isRBody(self,n): #Checks if the current nest is valid to be a reply body.
        return (     self.comn <= self.max_comn
                 and self.replies
                 and self.isLegal(n,[ ("li","ul","li","div","div","div"),
                                      (0,"class","top-level-reply"),
                                      (1,"class","replies"),
                                      (2,"class","reply"),
                                      (3,"class","comment"),
                                      (4,"class","info"),
                                      (5,"class","content")               ]) )
    def handle_starttag(self, tag, attrs):
        il = (self.isCName(self.nest),self.isCBody(self.nest),self.isRName(self.nest),self.isRBody(self.nest))
        self.nest.append((tag,self.aDict(attrs)))
        if il != (self.isCName(self.nest),self.isCBody(self.nest),self.isRName(self.nest),self.isRBody(self.nest)): #Check if a new comment/reply username or body has begun.
            iscn = self.isCName(self.nest)
            if (iscn or self.isRName(self.nest)) and not (il[0] or il[2]): #If a new comment/reply name has begun and we're below the maximum,
                if iscn: #If new comment name,
                    self.comn += 1 #Increment by 1 to keep track of how many root comments we've come across.
                    if self.comn <= self.max_comn: #If we haven't reached the maximum,
                        self.out.append(["comment"]) #Append type to output.
                else: #If a new reply name,
                    self.out.append(["reply"]) #Append type.
                if self.comn <= self.max_comn:#If we haven't reached the maximum,
                    self.out.append([self.nest[-4][1]['data-comment-id'][0]]) #Append comment id to output array.
            if self.comn <= self.max_comn:#If we haven't reached the maximum,
                self.out.append([]) #Append new list to output array to store name or body.
        elif tag == "img": #If the tag is valid to be an emoticon,
            if (     (self.isCBody(self.nest) or self.isRBody(self.nest))
                 and self.isLegal(self.nest,[tuple(),(-1,"class","easter-egg")]) ):
                try:
                    ai = (self.nest[-1][1]['src'][0].rindex('/')+1,self.nest[-1][1]['src'][0].rindex(".png")) #Attempt to extract emoticon alias name fom src.
                    self.out[-1].append('_'+self.nest[-1][1]['src'][0][ai[0]:ai[1]]+'_')
                except ValueError:
                    self.out[-1].append("_undefined_") #If alias not found, refer to it as "_undefined_"
            self.nest.pop() #Remove image from nest array since it's most likely without an end tag.
        elif (     tag == 'a'
               and (self.isCBody(self.nest) or self.isRBody(self.nest))
               and self.nest[-1][1]['href'][0][:7] == "/users/"
               and self.out[-1][-1][-1] == ' '                          ):
            self.out[-1][-1] = self.out[-1][-1][:-1]
    def handle_endtag(self,tag):
        if tag != "img": #Ignore img end tags since they will have already been dealt with.
            self.nest.pop()
    def handle_data(self,data):
        if any((self.isCName(self.nest),self.isCBody(self.nest),self.isRName(self.nest),self.isRBody(self.nest))): #If we're in valid comment/reply text,
            self.out[-1].append(data) #Append text to output.
    def handle_entityref(self,name):
        if any((self.isCName(self.nest),self.isCBody(self.nest),self.isRName(self.nest),self.isRBody(self.nest))): #If we're in valid comment/reply text,
            self.out[-1].append(unichr(name2codepoint[name])) #Append text to output.
    def handle_charref(self,name):
        if any((self.isCName(self.nest),self.isCBody(self.nest),self.isRName(self.nest),self.isRBody(self.nest))): #If we're in valid comment/reply text,
            self.out[-1].append(unichr(int(name[1:],16) if name[0] == 'x' else int(name))) #Append text to output.
    def parse(self,data,max_comments=30,replies=True,to=1): #Parses any data given. Data must be complete.
        if self.comments != md5(data).digest(): #If we haven't already parsed this,
            self.comments = data
            self.out = [] #Reinitialise the instance.
            self.nest = []
            self.replies = replies
            self.comn = int()
            self.max_comn = max_comments
            self.reset() #Reset the parser.
            self.feed(self.comments) #Feed the parser the data from the comments of the project specified.
            self.comments = md5(self.comments).digest() #Set to MD5 hash to save memory and make comparison between this and future data faster
            self.out =  [{"type": self.out[i][0], #Convert parsed data into a more usable format. e.g. ({'type': 'comment', 'id': 54852378, 'user': u'Gaza101', 'msg': u'_waffle_'}, ...)
                            "id": int(self.out[i+1][0]),
                          "user": u''.join([m.decode("utf-8") for m in self.out[i+2]]),
                           "msg": u''.join([m.decode("utf-8") for m in self.out[i+3]])[:-12]} for i in range(0,len(self.out),4)]
            for i in range(len(self.out)): #Continued conversion...
                if self.out[i]['type'] == "comment":
                    self.out[i]['msg'] = self.out[i]['msg'][23:] #If regular comment, remove first 23 characters of body.
                else: #If reply,
                    try:
                        tei = self.out[i]['msg'].index(u'\n',15) #Index end of tag (@Gaza101) at beginning of reply.
                    except ValueError:
                        self.out[i]['msg'] = self.out[i]['msg'][23:] #If we fail, treat it as having no tag.
                    else:
                        self.out[i]['msg'] = self.out[i]['msg'][14:tei]+u' '+self.out[i]['msg'][tei+23:] #Otherwise, reformat to create, '@user rest_of_message'
            self.out = tuple(self.out)
        return self.out #Output parsed data.
    def parse_project(self,project_id,max_comments=30,page=1,replies=True,to=1): #Parses any data given. Data must be complete.
        comments = urlopen("https://scratch.mit.edu/site-api/comments/project/"+str(project_id)+"/?page="+str(page),timeout=to).read()
        return self.parse(comments,max_comments,replies,to)
    def parse_user(self,user,max_comments=30,page=1,replies=True,to=1): #Parses any data given. Data must be complete.
        comments = urlopen("https://scratch.mit.edu/site-api/comments/user/"+user+"/?page="+str(page),timeout=to).read()
        return self.parse(comments,max_comments,replies,to)
