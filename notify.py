#!/usr/bin/env python3
# pylint: disable=W0401,W0613


import os,time,sys,traceback,math,itertools,json
from telegram import Update
from telegram.ext import Updater,CallbackContext,Filters
from telegram.ext import CommandHandler,MessageHandler
from telegram.error import BadRequest,Conflict,NetworkError
try:
    from config import *
except:
    print("Please copy config_example.py to config.py and fill in the blanks")
    sys.exit(0)

LOGLEVEL={0:"DEBUG",1:"INFO",2:"WARN",3:"ERR",4:"FATAL"}
LOGFILE="log"

def log(msg,l=1,end="\n",logfile=LOGFILE):
    st=traceback.extract_stack()[-2]
    lstr=LOGLEVEL[l]
    now_str=time.strftime("%y%m%d %H:%M:%S",time.localtime())
    perfix="%s [%s,%s:%03d]"%(now_str,lstr,st.name,st.lineno)
    if l<3:
        tempstr="%s %s%s"%(perfix,str(msg),end)
    else:
        tempstr="%s %s:\n%s%s"%(perfix,str(msg),traceback.format_exc(limit=5),end)
    print(tempstr,end="")
    if l>=1:
        with open(logfile,"a") as f:
            f.write(tempstr)

class NotifyBot():
    def __init__(self):
        self.dir = "/".join(os.path.abspath(__file__).split("/")[:-1])

    def check_msg(self):
        for i in os.listdir(self.dir):
            if i.endswith('.json'):
                try:
                    self.send_msg(self.dir+'/'+i)
                except:
                    log("send %s failed"%(i),l=3)

    def send_msg(self,msgfile):
        "msgfile should be a full path at this step"
        log("sending %s"%(msgfile))
        with open(msgfile) as f:
            msg = json.load(f)
        assert 'chat_id' in msg, '`chat_id` not in %s'%(msg)
        assert 'text' in msg, '`text` not in %s'%(msg)
        if 'parse_mode' not in msg:
            msg['parse_mode'] = 'HTML'

        updater = Updater(TOKEN)
        updater.bot.sendMessage(msg['chat_id'],msg['text'],parse_mode=msg['parse_mode'])

        sent_dir = self.dir+"/sent"
        if not os.path.exists(sent_dir):
            os.mkdir(sent_dir)
            log("made dir: %s"%(sent_dir))

        os.system("mv %s %s"%(msgfile,sent_dir))
        log("sent %s"%(msgfile))

    def make_msg(self,chat_id,text,parse_mode='HTML',dir=None):
        msg = {'chat_id':chat_id,'text':text,'parse_mode':parse_mode}
        now_str = time.strftime("%y%m%d%H%M%S",time.localtime())
        if dir is None:
            dir = self.dir
        with open(dir+'/%s-%s.json'%(chat_id,now_str),'w') as f:
            json.dump(msg,f)


if __name__ == '__main__':
    if len(sys.argv)==2 and 'check' in sys.argv[1]:
        b = NotifyBot()
        b.check_msg()
    elif len(sys.argv)==2 and 'test' in sys.argv[1]:
        b = NotifyBot()
        b.make_msg("@tokenindices",'This is a test message')
        b.check_msg()
    else:
        print('--check\n--test')
