#!/usr/bin/python3

# Hals Pi-Hole GUI mod

# Raspberrypi Zero W + Waveshare 1.3inch LED Hat (https://www.waveshare.com/wiki/1.3inch_OLED_HAT)
# made using Python 3.7

# v1.0  basic menu and sys info working
# v1.1  added Pi reboot (main menu (7) )
# v1.1.1 added Pi shutdown (System Related page)
# v1.2  EXPERIMENTATION.
# v1.3  revamped SysInfo code.
#       started Pi-Hole GUI commands
# v1.4  Rewrote lots as I'm learning and experimenting \\ finally achieved multiline Pi-hole output GUI
#       GUI added random password reset of admin panel
#       GUI added Pi-Hole update 
# v1.4.1 GUI added Pi-Hole version \ status (needs work)      


# -*- coding:utf-8 -*-
#imports 
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator
from luma.core import lib
from luma.oled.device import sh1106
import RPi.GPIO as GPIO
import datetime
import time
import subprocess
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import socket, sys
import os
import base64
import struct
import smbus
import sys
import io
from contextlib import redirect_stdout
import random

SCNTYPE = 1 # 1= OLED #2 = TERMINAL MODE BETA TESTS VERSION
bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
GPIO.setwarnings(False)


# Load default font.
font = ImageFont.load_default()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 64
image = Image.new('1', (width, height))
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
line1 = top
line2 = top+8
line3 = top+16
line4 = top+25
line5 = top+34
line6 = top+43
line7 = top+52
brightness = 255 #Max
fichier=""
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
RST = 25
CS = 8
DC = 24

#GPIO define and OLED configuration
RST_PIN        = 25 #waveshare settings
CS_PIN         = 8  #waveshare settings
DC_PIN         = 24 #waveshare settings
KEY_UP_PIN     = 6  #stick up
KEY_DOWN_PIN   = 19 #stick down
KEY_LEFT_PIN   = 5 #5  #sitck left // go back
KEY_RIGHT_PIN  = 26 #stick right // go in // validate
KEY_PRESS_PIN  = 13 #stick center button
KEY1_PIN       = 21 #key 1 // up
KEY2_PIN       = 20  #20 #key 2 // cancel/goback
KEY3_PIN       = 16 #key 3 // down
USER_I2C = 0        #set to 1 if your oled is I2C or  0 if use SPI interface
#init GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
screensaver = 0
#SPI
#serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = 24, gpio_RST = 25)
if SCNTYPE == 1:
    if  USER_I2C == 1:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RST,GPIO.OUT)
        GPIO.output(RST,GPIO.HIGH)
        serial = i2c(port=1, address=0x3c)
    else:
        serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = 24, gpio_RST = 25)
if SCNTYPE == 1:
    device = sh1106(serial, rotate=2) #sh1106
def DisplayText(l1,l2,l3,l4,l5,l6,l7):
    # simple routine to display 7 lines of text
    if SCNTYPE == 1:
        with canvas(device) as draw:
            draw.text((0, line1), l1,  font=font, fill=255)
            draw.text((0, line2), l2, font=font, fill=255)
            draw.text((0, line3), l3,  font=font, fill=255)
            draw.text((0, line4), l4,  font=font, fill=255)
            draw.text((0, line5), l5, font=font, fill=255)
            draw.text((0, line6), l6, font=font, fill=255)
            draw.text((0, line7), l7, font=font, fill=255)
    if SCNTYPE == 2:
            os.system('clear')
            print(l1)
            print(l2)
            print(l3)
            print(l4)
            print(l5)
            print(l6)
            print(l7)


# lets get some menu code done \\ Theres lots more right at the end
def switch_menu(argument):
    switcher = {
        0: "_Screen Off",
        1: "_Pi-Hole settings",
        2: "_System settings",
        3: "_**testing**",
        4: "_",
        5: "_About",
        6: "_Reboot Device",
        7: "_System info", #menu 1
        8: "_OLED brightness",
        9: "_Display Off ",
        10: "_Key Test",
        11: "_Restart GUI",
        12: "_Shutdown Pi",
        13: "_",
        14: "_show Logo", # menu 2
        15: "_sys infos",
        16: "_",
        17: "_",
        18: "_",
        19: "_",
        20: "_",
        21: "_go blank", # menu 3
        22: "_",
        23: "_",
        24: "_",
        25: "_",
        26: "_",
        27: "_",
        28: "_go blank", # menu 4
        29: "_",
        30: "_",
        31: "_",
        32: "_",
        33: "_",
        34: "_",
        35: "_About", # menu 5
        36: "_",
        37: "_",
        38: "_",
        39: "_",
        40: "_",
        41: "_",
        42: "_Pi-Hole Status", # Pi-Hole page menu (6)
        43: "_Reset Web Admin Pwd", 
        44: "_Pi-Hole Version",
        45: "_Pi-Hole Update",
        46: "_",
        47: "_Enable AD Blocking",
        48: "_Disable AD Blocking" 
}
    return switcher.get(argument, "Invalid")

#system information sub routine
def sysinfos():
    while GPIO.input(KEY_LEFT_PIN):
          
        cmd = "hostname -I"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        IP = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        CPU = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        MemUsage = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        Disk = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = """/sbin/ifconfig wlan0 | grep "RX packets" | awk '{print $6" " $7}' | sed 's/[()]//g'"""  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        network_rx = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = """/sbin/ifconfig wlan0 | grep "TX packets" | awk '{print $6" " $7}' | sed 's/[()]//g'"""  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        network_tx = ps.communicate()[0].decode('utf-8').strip()    
   
        cmd = "date '+%Y-%m-%d %H:%M:%S'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        date_time = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = "vcgencmd measure_temp | sed 's/temp=//g'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        temp = ps.communicate()[0].decode('utf-8').strip()  

# system information page
        DisplayText(
           "" + str(CPU),
           "" + str(MemUsage),
           "" + str(Disk),
           "Temp: " + str(temp),
           " ",
           "IP: " + str(IP),
           " " + str(network_rx) + "/" + str(network_tx),
            )
        time.sleep(0.1)

# OLED contrast page
def OLEDContrast(contrast):
    #set contrast 0 to 255
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            #loop until press left to quit
            with canvas(device) as draw:
                if GPIO.input(KEY_UP_PIN): # button is released
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  #Up filled
                        contrast = contrast +5
                        if contrast>255:
                            contrast = 255

                if GPIO.input(KEY_DOWN_PIN): # button is released
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1) #down filled
                        contrast = contrast-5
                        if contrast<0:
                            contrast = 0
                device.contrast(contrast)
                draw.text((54, line4), "Value : " + str(contrast),  font=font, fill=255)
    return(contrast)        

def about():
    # Main IP Address (WiFi)
    cmd = "hostname -I | cut -d\' \' -f1"
    ips = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)
    ipout = (ips.stdout)
    # secondary IP address (ETH0)
    cmd = "hostname -I"
    ipeth = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)
    eth = (ipeth.stdout).split(" ")[1]
    # simple sub routine to show an About
    DisplayText(
        "  Hals PiHole GUI",
        "      V 1.0",
        "   EXPERIMENTAL",
        "",
        " IP: " + str(ipout),
        "Eth: " + str(eth),
        "",

        )
    while GPIO.input(KEY_LEFT_PIN):
        #wait
        menu = 1
        page = 0

def blank():
    # simple sub routine to show a page
    DisplayText(
        " ",
        " : blank for test :",
        " ",
        " ",
        " ",
        " ",
        " "
        )
    while GPIO.input(KEY_LEFT_PIN):
        #wait
        menu = 1
        page = 0


def logo():

    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images', 'bootPi-Hole.bmp'))
    logo = Image.open(img_path) \
        .transform((device.width, device.height), Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert(device.mode)
    device.display(logo)

    while GPIO.input(KEY_LEFT_PIN):
        #wait
        menu = 3
        page = 0
        #wait


def splash():
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images', 'bootPi-Hole.bmp'))
    splash = Image.open(img_path) \
        .transform((device.width, device.height), Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert(device.mode)
    device.display(splash)
    time.sleep(5) #5 sec splash boot screen


def SreenOFF():
    #put screen off until press left
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            device.hide()
            time.sleep(0.1)
        device.show()


def KeyTest():
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            with canvas(device) as draw:
                if GPIO.input(KEY_UP_PIN): # button is released
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  #Up filled

                if GPIO.input(KEY_LEFT_PIN): # button is released
                        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left
                else: # button is pressed:
                        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  #left filled

                if GPIO.input(KEY_RIGHT_PIN): # button is released
                        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right
                else: # button is pressed:
                        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1) #right filled

                if GPIO.input(KEY_DOWN_PIN): # button is released
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1) #down filled

                if GPIO.input(KEY_PRESS_PIN): # button is released
                        draw.rectangle((20, 22,40,40), outline=255, fill=0) #center 
                else: # button is pressed:
                        draw.rectangle((20, 22,40,40), outline=255, fill=1) #center filled

                if GPIO.input(KEY1_PIN): # button is released
                        draw.ellipse((70,0,90,20), outline=255, fill=0) #A button
                else: # button is pressed:
                        draw.ellipse((70,0,90,20), outline=255, fill=1) #A button filled

                if GPIO.input(KEY2_PIN): # button is released
                        draw.ellipse((100,20,120,40), outline=255, fill=0) #B button
                else: # button is pressed:
                        draw.ellipse((100,20,120,40), outline=255, fill=1) #B button filled
                        
                if GPIO.input(KEY3_PIN): # button is released
                        draw.ellipse((70,40,90,60), outline=255, fill=0) #A button
                else: # button is pressed:
                        draw.ellipse((70,40,90,60), outline=255, fill=1) #A button filled


#restart OLED UI
def restart():
    DisplayText(
    "",
    "",
    "",
    "PLEASE WAIT ...",
    "",
    "",
    ""
    )
    subprocess.run(['python','/home/pi/PiDisplay/runmenu.py','&'])
 #   print(stdout)
    return()                            

def rebootpi():
    DisplayText(
    "",
    "",
    "",
    "PLEASE WAIT ...",
    "",
    "",
    ""
    )
    cmd = "sudo shutdown -r now"
    reboot = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)

    DisplayText(
    "",
    "   Rebooting now",
    "",
    "",
    "  allow 5 minutes ",
    "  for device start",
    ""
    )     
    time.sleep(30)   
    return()

def shutdownpi():
    DisplayText(
    "",
    "",
    "",
    "PLEASE WAIT ...",
    "",
    "",
    ""
    )
    cmd = "sudo shutdown now"
    reboot = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)
     
    DisplayText(
    "",
    "  turning off now",
    "",
    "",
    "    wait for LED ",
    "    to turn off",
    ""
    )     
    time.sleep(30)   
    return(

    )
## Pi-Hole commands

# reset Pi-Hole web admin password
def PiHoleWebPwdReset():
    
    # generate a random password
    rndpw = str()
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    for i in range(8):
        rndpw = rndpw + random.choice(characters)
    #print(rndpw)

    # runs pi-hole command, strips tickbox out (latin-1 unicode error)
    cmd = "pihole -a -p " + rndpw + " | cut -d' ' -f4-8"

    resetpwd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
    resetpwdout = resetpwd.communicate()[0].decode('utf-8').strip()  
    if resetpwd.returncode != 0: 

        DisplayText(
        "",
        "   Error in code",
        " Failed: PWD Reset",
        "",
        "       " + str((phupdate.returncode)),
        "",
        ""
        )
        time.sleep(1) #pause     
        while GPIO.input(KEY_LEFT_PIN):
        #wait
            menu = 2
            page = 0


    else: 

        DisplayText(
        "",
        "  " + str(resetpwdout),
        "",
        " New Web Admin Pwd:",
        "     " + str(rndpw),
        "",
        ""
        )         
        time.sleep(2)      
    while GPIO.input(KEY_LEFT_PIN):
        #wait
        menu = 2
        page = 1


# Pi-Hole update
def PiHoleUpdate():

    while GPIO.input(KEY_LEFT_PIN):
        answer = 0
        while answer == 0:
            DisplayText(
                "YES              YES",
                "",
                "",
                "  Update software",
                "",
                "",
                "NO                NO"
                )
            if GPIO.input(KEY_UP_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 1
            if GPIO.input(KEY_DOWN_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 2
            if GPIO.input(KEY1_PIN): # button is released  <-----****** change back to button 1
                menu = 1
            else: # button is pressed:
                answer = 1
            if GPIO.input(KEY3_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 2
        if answer == 2:

            return()
     #   time.sleep(0.5) #pause

        DisplayText(
        "",
        "  Update beginning",
        "",
        "     be patient",
        "",
        "",
        ""
        )   
    # begin Pi-Hole update
        ## NOW with error checking??
        cmd = "pihole -up | cut -d' ' -f4-8" # cuts output to suit
        phupdate = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        updateout = phupdate.communicate()[0].decode('utf-8').strip()                     
        if phupdate.returncode != 0: 
       # print("::DEBUG:: Error: in code")
       # print((phupdate.returncode))
            DisplayText(
            "",
            "   Error in code",
            "   Failed: Update",
            "",
            "   " + str((phupdate.returncode)),
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
            #wait
                menu = 2
                page = 0



        else: 
            DisplayText(
            "" + str(updateout),
            "",
            "",
            "",
            "",
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
        #wait
                menu = 2
                page = 0

# Pi-Hole version
def PiHoleVersion():
        cmd = "pihole -v | cut -d' ' -f1,3,6" # cuts output to suit
        phv = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        phvout = phv.communicate()[0].decode('utf-8').strip()                     
        if phv.returncode != 0: 
       # print("::DEBUG:: Error: in code")
       # print((phupdate.returncode))
            DisplayText(
            "",
            "   Error in code",
            " Failed: Version",
            "",
            "        " + str((phv.returncode)),
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
            #wait
                menu = 2
                page = 3



        else: 

            print(phvout)

            DisplayText2(
            " " + str(phvout),
            #"",
            #"",
            #"",
            #"",
            #"",
            #""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
            #wait
                menu = 2
                page = 3


# Pi-Hole Disable Ad Blocking
def PiHoleDisable():

    while GPIO.input(KEY_LEFT_PIN):
        answer = 0
        while answer == 0:
            DisplayText(
                "YES              YES",
                "",
                "",
                "      Disable ",
                "    Ad Blocking?",
                "",
                "NO                NO"
                )
            if GPIO.input(KEY_UP_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 1
            if GPIO.input(KEY_DOWN_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 2
            if GPIO.input(KEY1_PIN): # button is released  <-----****** change back to button 1
                menu = 1
            else: # button is pressed:
                answer = 1
            if GPIO.input(KEY3_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 2
        if answer == 2:

            return()
     #   time.sleep(0.5) #pause

    # begin Pi-Hole disable

        cmd = "pihole disable | sed 's/[✓]/*/' | cut -d' ' -f4,5,6" # cuts output to suit
        phdisable = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        disout = phdisable.communicate()[0].decode('utf-8').strip()                     
        if phdisable.returncode != 0: 
       # print("::DEBUG:: Error: in code")
       # print((phupdate.returncode))
            DisplayText(
            "",
            "   Error in code",
            "  Failed: disable",
            "",
            "        " + str((phdisable.returncode)),
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
            #wait
                menu = 2
                page = 0



        else: 
            print(disout)
            DisplayText(
            "" + str(disout),
            "",
            "",
            "",
            "",
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
        #wait
                menu = 2
                page = 0

# Pi-Hole Enable Ad Blocking
def PiHoleEnable():

    while GPIO.input(KEY_LEFT_PIN):
        answer = 0
        while answer == 0:
            DisplayText(
                "YES              YES",
                "",
                "",
                "      Enable ",
                "    Ad Blocking?",
                "",
                "NO                NO"
                )
            if GPIO.input(KEY_UP_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 1
            if GPIO.input(KEY_DOWN_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 2
            if GPIO.input(KEY1_PIN): # button is released  <-----****** change back to button 1
                menu = 1
            else: # button is pressed:
                answer = 1
            if GPIO.input(KEY3_PIN): # button is released
                menu = 1
            else: # button is pressed:
                answer = 2
        if answer == 2:

            return()
     #   time.sleep(0.5) #pause

    # begin Pi-Hole Enable

        cmd = "pihole enable | sed 's/[✓]/*/' | cut -d' ' -f4,5,6" # cuts output to suit
        phenable = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        enout = phenable.communicate()[0].decode('utf-8').strip()                     
        if phenable.returncode != 0: 
       # print("::DEBUG:: Error: in code")
       # print((phupdate.returncode))
            DisplayText(
            "",
            "   Error in code",
            "   Fail: enable",
            "",
            "   " + str((phdenable.returncode)),
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
            #wait
                menu = 2
                page = 0



        else: 
            print(enout)
            DisplayText(
            "" + str(enout),
            "",
            "",
            "",
            "",
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
        #wait
                menu = 2
                page = 0



############################### Satus page custom ########## redfine new screen layout

# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
line11 = top

def DisplayText2(l1):
    # simple routine to display 7 lines of text
    if SCNTYPE == 1:
        with canvas(device) as draw:
            draw.text((0, line11), l1,  font=font, fill=255)


            ################################################ end define new screen layout

# Pi-Hole Status GUI  <--- needs work on output to oled nicely
def PiHoleStatus():
        cmd = "pihole status | cut -d' ' -f5-10 | sed 's/[✓]/*/'" # cuts output to suit
        phs = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        phsout = phs.communicate()[0].decode('utf-8').strip() 
        phsout2 = phsout.replace(" [\u2713]","+")
        #phsout3 = phsout2.replace("  ","")                   
        if phs.returncode != 0: 
       # print("::DEBUG:: Error: in code")
       # print((phupdate.returncode))
            DisplayText(
            "",
            "   Error in code",
            " Failed: status",
            "",
            "       " + str((phs.returncode)),
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
            #wait
                menu = 2
                page = 4



        else: 

            print(phsout2)

            DisplayText(
            "" + str(phsout2),
            "",
            "",
            "",
            "",
            "",
            ""
            )     
            time.sleep(1) #pause     
            while GPIO.input(KEY_LEFT_PIN):
            #wait
                menu = 2
                page = 4




######################################################## MENU SYSTEM BELOW ##################

#init vars 
curseur = 1
page=0  
menu = 1
ligne = ["","","","","","","",""]
selection = 0
if SCNTYPE == 1:
    splash()  # display boot splash image ---------------------------------------------------------------------
    device.contrast(2)
while 1:
    if GPIO.input(KEY_UP_PIN): # button is released
        menu = 1
    else: # button is pressed:
        curseur = curseur -1
        if curseur<1:
            curseur = 7     
    if GPIO.input(KEY_LEFT_PIN): # button is released
        menu = 1
    else: # button is pressed:
                # back to main menu on Page 0
        page = 0    
    if GPIO.input(KEY_RIGHT_PIN): # button is released
        menu = 1
    else: # button is pressed:
        selection = 1
    if GPIO.input(KEY_DOWN_PIN): # button is released
        menu = 1
    else: # button is pressed:
        curseur = curseur + 1
        if curseur>7:
            curseur = 1
#-----------
    if selection == 1:
        # display pages --------------------------------------------------------------
            if page == 7:
                #system menu
                if curseur == 1:
                    sysinfos()
                if curseur == 2:
                    brightness = OLEDContrast(brightness)
                if curseur == 3:
                    SreenOFF()
                if curseur == 4:
                    KeyTest()
                if curseur == 5:
                    restart()
                if curseur == 6:
                    shutdownpi()

            if page == 14:
                # related menu
                if curseur == 1:
                    #blank page
                    logo()
                if curseur == 2:
                    #blank page
                    sysinfos()            
            if page == 21:
                if curseur == 1:
                   #blank page
                    logo()
            if page == 28:
                    #trigger section
                if curseur == 1:
                    #blank page
                    blank()
            if page == 35:
                #template section menu
                if curseur == 1:
                    #blank page
                   about()
                if curseur == 2:
                    #blank page
                    blank()
                    
                # Pi-Hole menu pages        
            
            if page == 42:
                #Pi-Hole commands
                if curseur == 1:
                    #Pi-hole status
                    PiHoleStatus()  
                if curseur == 2:
                    #pihole password reset
                    PiHoleWebPwdReset()
                if curseur == 3:
                    #Pi-hole version
                    PiHoleVersion()
                if curseur == 4:
                    #pi-hole update
                    PiHoleUpdate()
                if curseur == 5:
                    #nothing
                    blank()
                if curseur == 6:
                    #pi-hole Enable AD Blocking
                    PiHoleEnable()    
                if curseur == 7:
                    #pi-hole Disable AD Blocking 
                    PiHoleDisable()
    

############# MAIN MENU ############## -----------------------------------

            if page == 0:
            #we are in main menu
                if curseur == 1:
                    SreenOFF()
                if curseur == 2:
                    # PiHole menu
                    page = 42
                    curseur = 1
                if curseur == 3:
                    #system menu 
                    page = 7
                    curseur = 1
                if curseur == 4:
                   #logo img menu
                    page = 14
                    curseur = 1
                if curseur == 5:
                    page = 0
                    curseur = 5
                if curseur == 6:
                    # about
                    about()
                if curseur == 7:
                    rebootpi()                                  
                print(page+curseur)
    ligne[1]=switch_menu(page)
    ligne[2]=switch_menu(page+1)
    ligne[3]=switch_menu(page+2)
    ligne[4]=switch_menu(page+3)
    ligne[5]=switch_menu(page+4)
    ligne[6]=switch_menu(page+5)
    ligne[7]=switch_menu(page+6)




    #add curser on front on current selected line
    for n in range(1,8):
        if page+curseur == page+n:
            if page == 1:
                if readCapacity(bus) < 16:
                    ligne[n] = ligne[n].replace("_","!")
                else:
                    ligne[n] = ligne[n].replace("_",">")
            else:
                ligne[n] = ligne[n].replace("_",">")
        else:
            ligne[n] = ligne[n].replace("_"," ")
    DisplayText(ligne[1],ligne[2],ligne[3],ligne[4],ligne[5],ligne[6],ligne[7])
    #print(page+curseur) #debug trace menu value
    time.sleep(0.1)
    selection = 0
GPIO.cleanup()


