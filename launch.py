import time,platform,sys
from io import open
from os.path import isfile

env = {}
report = []
rn = str()
rs = 1

try:
    execfile("comment.py",env)
except Exception as e:
    rn = "crash_"+time.strftime("%Y-%m-%d-utc",time.gmtime())
    print "[ERROR] It looks like something broke! Generating crash report."
    if isfile(rn+".txt"):
        while isfile(rn+'_'+str(rs)+".txt"):
            rs += 1
        rn += '_'+str(rs)
    rn += ".txt"
    try:
        with open(rn,'w') as f:
            f.write(u"It looks like something broke! Send this file to Gaza101 for assistance.\n\n")
            try:
                f.write(u"ver: '"+unicode(env['ver'])+u"'\n\n")
            except KeyError:
                f.write(u"ver: undefined\n\n")
            f.write(  u"platform.platform: '"+unicode(platform.platform())+u"'\n"
                     +u"platform.python_version: '"+unicode(platform.python_version())+u"'\n"
                     +u"is_64bits: "+unicode(sys.maxsize > 2**32)+u"\n\n"
                     +u"e.__class__.__name__: "+unicode(e.__class__.__name__)+u"\n"
                     +u"e.args: "+unicode(e.args)+"\n\n"                                      )
            for i in ("__builtins__","password","ver"):
                try:
                    del env[i]
                except KeyError:
                    pass
            for i in env:
                report = unicode(i)+u': '+(u"'"+unicode(env[i])+u"'" if type(env[i]) is str else u"u'"+env[i]+u"'" if type(env[i]) is unicode else unicode(env[i]))+u'\n'
                if u'\n' in report[:-1]:
                    report = u'\n'+report+u'\n'
                f.write(report)
            f.close()
    except IOError:
        print "[ERROR] Unable to save crash report."
    else:
        print "[INFO] Crash report saved as '"+rn+"'"

raw_input("Press enter to exit...")
