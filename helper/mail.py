#coding:utf-8

import os
import smtplib
import glob
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import zipfile


class mail():
    def __init__(self, FOLDER, TO, BODY = ''):
        self._msg = MIMEMultipart()
        self._folder = FOLDER
        self._zipName = self._folder + '..\\new-create.zip'
        
        self._gmail_user = "telefar@126.com"
        self._gmail_pwd = "7u7u7u&U"
        self._msg['From'] = self._gmail_user
        self._msg['To'] = TO
        self._msg['Subject'] = 'your required files'
        self._msg["Accept-Language"]="zh-CN"
        self._msg["Accept-Charset"]="ISO-8859-1,utf-8"
        self._text = BODY
        self._files = glob.glob("%s*.*" %FOLDER)
        assert isinstance(self._files, list)     


    def zip(self):
        zf = zipfile.ZipFile(self._zipName, "w")
        for dirname, subdirs, files in os.walk(self._folder):
            #print dirname
            #print subdirs
            zf.write(dirname)
            for filename in files:
                
                zf.write(os.path.join(dirname, filename))
        zf.close()


    def send_mail(self):
        self._msg.attach(MIMEText(self._text))
        print "  attaching files.."  
        
        self.zip()
        part = MIMEBase('application', "zip")
        part.set_payload( open(self._zipName,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % self._zipName)
        self._msg.attach(part)
        
        #=======================================================================
        #         
        # for f in self._files:
        #     part = MIMEBase('application', "octet-stream")
        #     part.set_payload( open(f,"rb").read() )
        #     Encoders.encode_base64(part)
        #     part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        #     self._msg.attach(part)
        #=======================================================================
        
        mailServer = smtplib.SMTP("smtp.126.com")
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(self._gmail_user, self._gmail_pwd)
        mailServer.sendmail(self._gmail_user, self._msg['To'], self._msg.as_string())
        mailServer.close()


if __name__ == "__main__":
    import DataSpider.config.Globaldata as G
    print glob.glob("%s*.*" %G.pngTargetFolder)
    print "start sending Email"
    mail(FOLDER=G.pngTargetFolder, TO='telefar@126.com').send_mail()
    print "finish sending Email"