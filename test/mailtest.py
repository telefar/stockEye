__author__ = 'phabio'

# -*- coding: cp936 -*-

import config.Globaldata as G

from helper.mail import *

import os
import time
import datetime
import shutil


def make_dir(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print " make dir %s successful" %(folder_name)
    else:
        print " dir %s already exists" %(folder_name)

def copy_txt(source_file, target_folder):
    if source_file[-4:]== ('.TXT') :
        shutil.copy2(source_file, target_folder)



if __name__ == "__main__":

    email_body_final = ''
    changxian_title = u"Only for send mail test."
    email_body_final += (changxian_title)

    mail(FOLDER=G.pngTargetFolder, TO='telefar@126.com', BODY = email_body_final).send_mail()
    print 'finished'


