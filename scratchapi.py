# -*- coding: UTF-8 -*-

#!python3
# ScratchAPI 1.0
# Written by Dylan5797 [https://dylan5797.github.io]
#  _____        _             _____ ______ ___ ______  
# |  __ \      | |           | ____|____  / _ \____  | 
# | |  | |_   _| | __ _ _ __ | |__     / / (_) |  / /  
# | |  | | | | | |/ _  |  _ \|___ \   / / \__  | / /   
# | |__| | |_| | | (_| | | | |___) | / /    / / / /    
# |_____/ \__  |_|\__|_|_| |_|____/ /_/    /_/ /_/     
#          __/ |                                       
#         |___/      

from __future__ import absolute_import
import requests
import json
import socket
import hashlib
import os
import sys
import traceback
from io import open

class ScratchUserSession(object):
    SERVER = u'scratch.mit.edu'
    API_SERVER = u'api.scratch.mit.edu'
    PROJECTS_SERVER = u'projects.scratch.mit.edu'
    ASSETS_SERVER = u'assets.scratch.mit.edu'
    CDN_SERVER = u'cdn.scratch.mit.edu'
    CLOUD = u'cloud.scratch.mit.edu'
    CLOUD_PORT = 531
    def __init__(self, username, password):
        self.lib.utils.request = self._rcallarg
        self.lib.set.username = username
        self.lib.set.password = password
        self.lib.utils.session = requests.session()
        
        self.tools.verify_session = self._tools_verifySession
        self.tools.update = self._tools_update
        self.tools.reload_session = self._tools_reload_session
        
        self.projects.get = self._projects_getProject
        self.projects.set = self._projects_setProject
        self.projects.comment = self._projects_comment
        self.projects.get_meta = self._projects_get_meta
        self.projects.get_remix_data = self._projects_get_remixtree
        
        self.backpack.get = self._backpack_getBackpack
        self.backpack.set = self._backpack_setBackpack
        
        self.userpage.set_bio = self._userpage_setBio
        self.userpage.set_status = self._userpage_setStatus
        self.userpage.toggle_comments = self._userpage_toggleComments
        
        self.users.follow = self._users_follow
        self.users.unfollow = self._users_unfollow
        self.users.get_message_count = self._users_get_message_count
        self.users.comment = self._users_comment
        
        self.studios.comment = self._studios_comment
        self.studios.get_meta = self._studios_get_meta
        
        self.cloud.set_var = self._cloud_setvar
        self.cloud.create_var = self._cloud_makevar
        self.cloud.get_var = self._cloud_getvar
        self.cloud.get_vars = self._cloud_getvars
        
        self.HEADERS = {u'X-Requested-With': u'XMLHttpRequest', u'Referer':u'https://scratch.mit.edu/'}
        self.lib.utils.request(path=u'/csrf_token/', update=False)
        self.HEADERS[u'Cookie'] = u'scratchcsrftoken=' + self.lib.utils.session.cookies.get(u'scratchcsrftoken') + u'; scratchlanguage=en'
        self.HEADERS[u'X-CSRFToken'] = self.lib.utils.session.cookies.get(u'scratchcsrftoken')
        self.lib.utils.request(path=u'/login/', method=u'post', update=False, payload=json.dumps({u'username': username, u'password': password, u'csrftoken':self.lib.utils.session.cookies.get(u'scratchcsrftoken'), u'csrfmiddlewaretoken':self.lib.utils.session.cookies.get(u'scratchcsrftoken'),u'captcha_challenge':u'',u'captcha_response':u'',u'embed_captcha':False,u'timezone':u'America/New_York'}))
        self.tools.update()
    def _projects_getProject(self, projectId):
        return self.lib.utils.request(path=u'/internalapi/project/' + projectId + u'/get/', server=ScratchUserSession.PROJECTS_SERVER).json()
    def _projects_setProject(self, projectId, payload):
        return self.lib.utils.request(server=ScratchUserSession.PROJECTS_SERVER, path=u'/internalapi/project/' + projectId + u'/set/', payload=json.dumps(payload), method=u'post')
    def _projects_get_meta(self, projid):
        return self.lib.utils.request(path=u'/api/v1/project/' + unicode(projid) + u'/?format=json').json()
    def _projects_get_remixtree(self, projid):
        return self.lib.utils.request(path=u'/projects/' + unicode(projid) + u'/remixtree/bare/').json()
    def _tools_verifySession(self):
        return self.lib.utils.request(path=u'/messages/ajax/get-message-count/', port=None).status_code == 200
    def _tools_reload_session(self):
        self.__init__(self.lib.set.username, self.lib.set.password)
    def _backpack_getBackpack(self):
        return self.lib.utils.request(path=u'/internalapi/backpack/' + self.lib.set.username + u'/get/').json()
    def _backpack_setBackpack(self, payload):
        return self.lib.utils.request(server=ScratchUserSession.CDN_SERVER, path=u'/internalapi/backpack/' + self.lib.set.username + u'/set/', method=u"post", payload=payload)
    def _userpage_setStatus(self, payload):
        p2 = self.lib.utils.request(path=u'/site-api/users/all/' + self.lib.set.username).json()
        p = {}
        for i in p2:
            if i in [u'comments_allowed', u'id', u'status', u'thumbnail_url', u'userId', u'username']:
                p[i] = p2[i]
        p[u'status'] = payload
        return self.lib.utils.request(path=u'/site-api/users/all/' + self.lib.set.username, method=u"put", payload=json.dumps(p))
    def _userpage_toggleComments(self):
        return self.lib.utils.request(path=u'/site-api/comments/user/' + self.lib.set.username + u'/toggle-comments/', method=u"put", payload=json.dumps(p))
    def _userpage_setBio(self, payload):
        p2 = self.lib.utils.request(path=u'/site-api/users/all/' + self.lib.set.username).json()
        p = {}
        for i in p2:
            if i in [u'comments_allowed', u'id', u'bio', u'thumbnail_url', u'userId', u'username']:
                p[i] = p2[i]
        p[u'bio'] = payload
        return self.lib.utils.request(path=u'/site-api/users/all/' + self.lib.set.username, method=u"put", payload=json.dumps(p))
    def _users_get_meta(self, usr):
        return self.lib.utils.request(path=u'/users/' + usr, server=self.API_SERVER).json()
    def _users_follow(self, usr):
        return self.lib.utils.request(path=u'/site-api/users/followers/' + usr + u'/add/?usernames=' + self.lib.set.username, method=u'PUT')
    def _users_unfollow(self, usr):
        return self.lib.utils.request(path=u'/site-api/users/followers/' + usr + u'/remove/?usernames=' + self.lib.set.username, method=u'PUT')
    def _users_comment(self, user, comment):
        return self.lib.utils.request(path=u'/site-api/comments/user/' + user + u'/add/', method=u'POST', payload=json.dumps({u"content":comment,u"parent_id":u'',u"commentee_id":u''}))
    def _studios_comment(self, studioid, comment):
        return self.lib.utils.request(path=u'/site-api/comments/gallery/' + unicode(studioid) + u'/add/', method=u'POST', payload=json.dumps({u"content":comment,u"parent_id":u'',u"commentee_id":u''}))
    def _studios_get_meta(self, studioid):
        return self.lib.utils.request(path=u'/site-api/galleries/all/' + unicode(studioid)).json()
    def _studios_invite(self, studioid, user):
        return self.lib.utils.request(path=u'/site-api/users/curators-in/' + unicode(studioid) + u'/invite_curator/?usernames=' + user, method=u'PUT')
    def _projects_comment(self, projid, comment):
        return self.lib.utils.request(path=u'/site-api/comments/project/' + unicode(projid) + u'/add/', method=u'POST', payload=json.dumps({u"content":comment,u"parent_id":u'',u"commentee_id":u''}))
    def _cloud_setvar(self, var, value, projId):
        cloudToken = self.lib.utils.request(method=u'GET', path=u'/projects/' + unicode(projId) + u'/cloud-data.js').text.rsplit(u'\n')[-28].replace(u' ', u'')[13:49]
        bc = hashlib.md5()
        bc.update(cloudToken.encode())
        r = self.lib.utils.request(method=u'POST', path=u'/varserver', payload=json.dumps({u"token2": bc.hexdigest(), u"project_id": unicode(projId), u"value": unicode(value), u"method": u"set", u"token": cloudToken, u"user": self.lib.set.username, u"name": u'☁ ' + var}))
        return r
    def _cloud_makevar(self, var, value, projId):
        cloudToken = s.lib.utils.request(method=u'GET', path=u'/projects/' + unicode(projId) + u'/cloud-data.js').text.rsplit(u'\n')[-28].replace(u' ', u'')[13:49]
        bc = hashlib.md5()
        bc.update(cloudToken.encode())
        r = self.lib.utils.request(method=u'POST', path=u'/varserver', payload=json.dumps({u"token2": bc.hexdigest(), u"project_id": unicode(projId), u"value": unicode(value), u"method": u"create", u"token": cloudToken, u"user": self.lib.set.username, u"name": u'☁ ' + var}))
    def _cloud_getvar(self, var, projId):
        dt = self.lib.utils.request(path=u'/varserver/' + unicode(projId)).json()[u'variables']
        return dt[[x[u'name']==u'☁'+unichr(32)+var for x in dt].index(True)][u'value']
    def _cloud_getvars(self, projId):
        dt = self.lib.utils.request(path=u'/varserver/' + unicode(projId)).json()[u'variables']
        vardict = {}
        for x in dt:
          xn = x[u'name']
          if xn.startswith(u'☁'+unichr(32)):
            vardict[xn[2:]] = x[u'value']
          else:
            vardict[xn] = x[u'value']
        return vardict
    def _cloud_get_cmd(self, var, projId, value):
        cloudToken = s.lib.utils.request(method=u'GET', path=u'/projects/' + unicode(projId) + u'/cloud-data.js').text.rsplit(u'\n')[-28].replace(u' ', u'')[13:49]
        bc = hashlib.md5()
        bc.update(cloudToken.encode())
        return {u"token2": bc.hexdigest(), u"project_id": unicode(projId), u"value": unicode(value), u"method": u"create", u"token": cloudToken, u"user": self.lib.set.username, u"name": u'☁ ' + var} 
    def _tools_update(self):
        self.lib.set.csrf_token = self.lib.utils.session.cookies.get(u'scratchcsrftoken')
        self.lib.set.sessions_id = self.lib.utils.session.cookies.get(u'scratchsessionsid')
        self.HEADERS[u'Cookie'] = u'scratchcsrftoken=' + self.lib.utils.session.cookies.get_dict()[u'scratchcsrftoken'] + u'; scratchsessionsid=' + self.lib.utils.session.cookies.get(u'scratchsessionsid') + u'; scratchlanguage=en'
        self.HEADERS[u'X-CSRFToken'] = self.lib.utils.session.cookies.get(u'scratchcsrftoken')
    def _assets_get(self, md5):
        return self.lib.utils.request(path=u'/internalapi/asset/' + md5 + u'/get/', server=self.ASSETS_SERVER).content
    def _assets_set(self, md5, content, content_type=None):
        if not content_type:
            if os.path.splitext(md5)[-1] == u'.png':
                content_type = u'image/png'
            elif os.path.splitext(md5)[-1] == u'.svg':
                content_type = u'image/svg+xml'
            elif os.path.splitext(md5)[-1] == u'.wav':
                content_type = u'audio/wav'
            else:
                content_type = u'text/plain'
        headers = {u'Content-Length':unicode(len(content)),
u'Origin':u'https://cdn.scratch.mit.edu',
u'Content-Type':content_type,
u'Referer':u'https://cdn.scratch.mit.edu/scratchr2/static/__cc77646ad8a4b266f015616addd66756__/Scratch.swf'}
        return self.lib.utils.request(path=u'/internalapi/asset/' + md5 + u'/set/', method=u'POST', server=self.ASSETS_SERVER, payload=content)
    def _users_get_message_count(self, user=None):
        if user == None:
            user = self.lib.set.username
        return self.lib.utils.request(u'/proxy/users/' + user + u'/activity/count', server=self.API_SERVER).json()[u'msg_count']
    def _rcallarg(self, **options):
        headers = {}
        for x in self.HEADERS:
            headers[x] = self.HEADERS[x]
        method = u"get"
        server = ScratchUserSession.SERVER
        port = u''
        retry = 3
        if u'method' in options:
            method = options[u'method']
        if u'server' in options:
            server = options[u'server']
        if u'payload' in options:
            headers[u'Content-Length'] = len(unicode(options[u'payload']))
        if u'port' in options:
            if options[u'port'] == None:
                port = u''
            else:
                port = u':' + unicode(options[u'port'])
        if u'update' in options:
            if options[u'update'] == True:
                self.tools.update()             
        else:
            self.tools.update()
        if u'headers' in options:
            headers.update(options[u'headers'])
        if u'retry' in options:
            retry = options[u'retry']
        server = u'https://' + server
        def request():
            if u'payload' in options:
                r = getattr(self.lib.utils.session, method.lower())(server + port + options[u'path'], data=options[u'payload'], headers=headers)
            else:
                r = getattr(self.lib.utils.session, method.lower())(server + port + options[u'path'], headers=headers)
            return r
        for x in xrange(0, 3):
            try:
                r = request()    
            except:
                r = None
                continue
            else:
                break
        if r == None:
            raise ConnectionError(u'Connection failed on all ' + unicode(retry) + u' attempts')
        if u'update' in options:
            if options[u'update'] == True:
                self.tools.update()             
        else:
            self.tools.update()
        return r
    class lib(object):
        class set(object): pass
        class utils(object): pass
    class tools(object): pass
    class projects(object): pass
    class backpack(object): pass
    class userpage(object): pass
    class users(object): pass
    class studios(object): pass
    class cloud(object): pass


class CloudSession(object):
    def __init__(self, projectId, session):
        if type(session) == ScratchUserSession:
            self._scratch = session
        else:
            self._scratch = ScratchUserSession(session[0], session[1])
        self._user = self._scratch.lib.set.username
        self._projectId = projectId
        self._cloudId = self._scratch.lib.set.sessions_id
        self._token = self._scratch.lib.utils.request(method=u'GET', path=u'/projects/' + unicode(self._projectId) + u'/cloud-data.js').text.rsplit(u'\n')[-28].replace(u' ', u'')[13:49]
        md5 = hashlib.md5()
        md5.update(self._cloudId.encode())
        self._md5token = md5.hexdigest()
        self._connection = socket.create_connection((ScratchUserSession.CLOUD, ScratchUserSession.CLOUD_PORT))
        self._send(u'handshake', {})
    def _send(self, method, options):
        obj = {
            u'token': self._token,
            u'token2': self._md5token,
            u'user': self._user,
            u'project_id': unicode(self._projectId),
            u'method': method
            }
        obj.update(options)
        ob = (json.dumps(obj) + u'\r\n').encode(u'utf-8')
        self._connection.send(ob)
        md5 = hashlib.md5()
        md5.update(self._md5token.encode())
        self._md5token = md5.hexdigest()
        
    def set_var(self, name, value):
        self._send(u'set', {u'name': u'☁ ' + name, u'value': value})

    def create_var(self, name, value=None):
        if value == None:
            value = 0
        self._send(u'create', {u'name': u'☁ ' + name, u'value':value})

    def rename_var(self, oldname, newname):
        self._send(u'rename', {u'name': u'☁ ' + oldname, u'new_name': u'☁ ' + newname})
    
    def delete_var(self, name):
        self._send(u'delete', {u'name':u'☁ ' + name})
    
    def get_var(self, name):
        return self._scratch.cloud.get_var(name,self._projectId)

    def get_vars(self):
        return self._scratch.cloud.get_vars(self._projectId)

if u'install' in sys.argv:
    try:
        f = open(os.path.dirname(os.__file__) + u'/scratchapi.py', u'wb')
        me = open(__file__, u'rb')
        f.write(me.read())
        f.close()
        me.close()
    except:
        print u'Error in install: '
        traceback.print_exc()
        raw_input(u'\n\n\nPress return to close\n')

