#!/usr/bin/python
#coding : utf-8
import os
import platform


def install_on_linux():
    #os.system('sudo apt-get install git') 
    #os.system('sudo apt-get install nodejs')
    #os.system('sudo apt-get install npm')
    #os.system('sudo apt-get install node')
    #os.system('sudo npm install -g hexo')
    pass

def install_on_osx():
    if os.system('which git') != 0:
        os.system('sudo brew install git') 

    if os.system('which nodejs') != 0:
        os.system('sudo brew install nodejs')

    if os.system('which node') != 0:
        os.system('sudo brew install node')

    if os.system('which npm') != 0:
        os.system('sudo brew install npm')

    if os.system('which hexo') != 0:
        os.system('sudo npm install -g hexo')
if __name__ == '__main__':
    sysstr = platform.system()
    print sysstr
    if sysstr == 'Linux':
        install_on_linux()
    elif sysstr == 'Darwin':
        install_on_osx()
    else:
        print 'not support operating system'

