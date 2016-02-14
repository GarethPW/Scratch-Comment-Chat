'''
    Basic Config Manager v1.0.0
    Created for use with SCV Server v2.1.0

    Created by Scratch user, Gaza101.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

from io import open

class Config:
    def __init__(self,name):
        self.config = {}
        self.name = name
        self.reload()
    def reload(self):
        self.config = {}
        try:
            with open(self.name,'r') as cf:
                di = []
                for l in cf:
                    if l[0] != u'#':
                        di = [i.strip() for i in l.split(':',1)]
                        if len(di) == 1:
                            continue
                        elif (     len(di[1]) >= 2
                               and di[1][0]+di[1][-1] in (u'""',u"''") ):
                            pass
                        elif di[1].lower() in (u"true",u'1',u"yes",u'y',u"on"):
                            di[1] = True
                        elif di[1].lower() in (u"false",u'0',u"no",u'n',u"off"):
                            di[1] = False
                        else:
                            try:
                                di[1] = float(di[1])
                            except ValueError:
                                pass
                            else:
                                if di[1].is_integer():
                                    di[1] = int(di[1])
                        if di[0] in self.config:
                            if type(self.config[di[0]]) is tuple:
                                self.config[di[0]] += (di[1],)
                            else:
                                self.config[di[0]] = (self.config[di[0]],di[1])
                        else:
                            self.config[di[0]] = di[1]
        except IOError:
            self.reset()
    def reset(self):
        with open(self.name,'w') as cf:
            cf.close()
        self.reload()
    def write(self,r):
        if type(r) in (tuple,list):
            for i in r:
                if not type(i) is dict:
                    raise TypeError("expected tuple or list of dict, or dict. Got "+str(type(r))[6:-1]+" of "+str(type(i))[6:-1])
        elif type(r) is dict:
            r = (r,)
        else:
            raise TypeError("expected tuple or list of dict, or dict. Got "+str(type(r))[6:-1])
        with open(self.name,'a+') as cf:
            for i in r:
                if len(i) != 1:
                    cf.close()
                    raise ValueError("dict must have length of 1")
                cf.seek(0)
                try:
                    if cf.read()[-1] != u'\n':
                        cf.write(u'\n')
                except IndexError:
                    pass
                i = (unicode(i.keys()[0]),unicode(i[i.keys()[0]]))
                cf.write(i[0]+u": "+i[1]+u'\n')
                if i[0] in self.config:
                    if type(self.config[i[0]]) is tuple:
                        self.config[i[0]] += (i[1],)
                    else:
                        self.config[i[0]] = (self.config[i[0]],i[1])
                else:
                    self.config[i[0]] = i[1]
            cf.close()
    def remove_all(self,k):
        if type(k) in (tuple,list):
            for i in k:
                if not type(i) is str:
                    raise TypeError("expected tuple or list of str or unicode, str, or unicode. Got "+str(type(k))[6:-1]+" of "+str(type(i))[6:-1])
        elif type(k) is str or unicode:
            k = (k,)
        else:
            raise TypeError("expected tuple or list of str or unicode, str, or unicode. Got "+str(type(k))[6:-1])
        for i in k:
            del self.config[i]
        cc = self.config
        self.reset()
        wq = []
        for i in cc:
            if type(cc[i]) is tuple:
                for v in cc[i]:
                    wq.append({i: v})
            else:
                wq.append({i: cc[i]})
        self.write(wq)
        self.reload()
