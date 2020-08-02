'''
Installer - The Installer for the Datalore Discord bot
(C) 2020 J.C. Boysha
    This file is part of Datalore.

    Datalore is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Datalore is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Datalore.  If not, see <https://www.gnu.org/licenses/>.
'''

import os, json, fileinput, pip

def import_or_install(package_list):
    for package in package_list:
        try:
            __import__(package)
        except ImportError:
            pip.main(['install', package])

import_or_install(['os', 'discord', 'csv', 'random', 'asyncio', 'json', 'dotenv'])

print("Welcome to the Datalore installer! I am here to help you get configured.")
print("At any point you can respond to a question with a capital 'Q' to quit.")

TOKEN = ""
URL = ""
COMMCHAR="%"

def getToken():
    resp = ""
    while resp != "Q":
        resp = input("Have you configured a Discord Token for your bot? ")
        if resp[0].lower() == "y":
            TOKEN = input("What is your token? ")
            return TOKEN
        elif resp[0].lower() == "n":
            print("You will need to set up a new token for your Discord bot.")
            print("Please follow these steps:")
            print("\t1) In a web browser, navigate to https://www.discord.com/developers/ and login with your discord login information\n\
                \t2) At the upper right corner of the developers portal please click \"New Application\"\n\
                \t3) Follow the prompts to name your applicaiton with a name of your choosing \n\
                \t4) From your application dashboard, select \"bot\" on the left hand menu\n\
                \t5) To the right of your bot dashboard click \"Add Bot\" \n\
                \t6) If you would like to change the bot's username, you can do that here \n\
                \t\ta) The name of the bot defaults to the name of the application. If you want that to stay the same, that is OK\n\
                \t\tb) You can also upload an image for the bot to use as its avatar\n\
                \t7) Select the \"copy\" button underneath the Token section of the Bot page\n\
                \t\ta) This will be just under the prompt to name the bot\n\
                \t8) You have now copied the token and can continue")
            TOKEN = input("What is your token? ")
            return TOKEN
        else:
            print("Please respond yes, or no.")
            continue
    exit() 
        

def getURL():
    resp = ""
    while resp != "Q":
        resp = input("Do you have a URL you would like to use for images\n(If you select No, this can be configured later on manually\n\
            but the bot will not display images in embeds until this is configured)? ")
        if resp[0].lower() == "y":
            resp = input("Have you configured hosting for your bot's images? ")
            if resp[0].lower() == "y":
                print("This will be the directory you will host bot images in. \n If this is not configured, images will not display in embeds.")
                URL = input("Please input the base path for bot assets eg. https://www.someurl.com/botimages/ : ")
                if URL[0:5] != "https":
                    print("The host needs to be SSL enabled for this to function properly. Please use Let's Encrypt to get a Free SSL cert!")
                    continue
                return URL
            elif resp[0].lower() == "n":
                print("You will need to host the images on a server. These images are provided in the imgs folder.\n\
                       The images also need to be hosted on an SSL connection.")
                return ""
            else:
                print("Please respond yes, or no.")
            continue
    exit() 

def getCommandChar():
    commChar = input("What character would you like to precede the bot's command? (% is the default) ")
    if commChar == "Q":
        exit()
    return commChar

def setenv(URL, TOKEN, COMMCHAR):
    with fileinput.FileInput('.env', inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace('<##TOKEN##>', TOKEN), end='')
    if URL is not "" or URL is not None:
        with fileinput.FileInput('.env', inplace=True, backup='.bak') as file:
            for line in file:            
                print(line.replace('<##URL##>', URL), end='')
    with fileinput.FileInput('.env', inplace=True, backup='.bak') as file:
        for line in file:            
            print(line.replace('<##COMMCHAR##>', COMMCHAR), end='')

TOKEN = getToken()
URL = getURL()
COMMCHAR = getCommandChar()
setenv(URL, TOKEN, COMMCHAR)

print("Now you will need to invite the bot to your server! \n\
        \t1) In a web browser, navigate to https://www.discord.com/developers/ and login with your discord login information\n\
        \t2) On your dashboard please select your bot's application\n\
        \t3) From your application dashboard, select \"Oauth2\" on the left hand menu\n\
        \t4) You will need to ensure your bot has the following permissions\n\
        \t\ta) bot\n\
        \t\tb) Send Messages\n\
        \t\tc) Send TTS Messages (for future features)\n\
        \t\td) Embed Links\n\
        \t\te) Attach Files\n\
        \t\tf) Mention Everyone (for future features)\n\
        \t\tb) You can also upload an image for the bot to use as its avatar\n\
        \t5) In the URL bar above the permissions selection, copy the URL and navigate to it in a browser\n\
        \t\ta) This will be in the \"scope\" box\n\
        \t6) Follow the prompts in the URL to add the bot to your server!")

print("Thank you for using the DataLore installer! You can now run the bot from this directory by running\n\
    'python3 bot.py`")