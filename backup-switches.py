# Backup HP/Aruba switches and email the results. Make sure to fill out the csv like this: https://i.imgur.com/CpxtXuB.png. 

import paramiko
import csv
import smtplib

i = 0

html = '<table border="1" class="fr-alternate-rows" style="height: 107px; width: 46%; border-style: solid;"> <tbody>'


# read the csv and put it into a dict object
with open("C:\\temp\\switches.csv") as f:
    reader = csv.DictReader (f)
    data =[r for r in reader]

maxlines = len(data)

# loop through each line to perform the actions
while i < maxlines:
    try:

        #combine 'path' and 'sourcefile' fields in csv to create a path that will be used to fetch the file on the switch.
        sourcefile = data[i]['path'] + data[i]['sourcefile']

        # save the source file with the 'hostname' from the csv in the file name.
        destfile = "c:\\temp\\backups\\{}.txt".format(data[i]['hostname']) 

        # s.connect below doesnt like it when you use something like 'data[i]['hostname'] in the command, so instead variables are created before hand to get around it.
        host = data[i]['hostname']
        adminuser = data[i]['username']
        
        # connect to switch using ssh, get the source file and save it locally.
        s = paramiko.SSHClient()

        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        s.connect(host,22,username=adminuser,password='PasswordForYourSwitch',timeout=4)
        sftp = s.open_sftp()

        sftp.get(sourcefile, destfile)

        i += 1

        print ("{} back up successful.".format(host))

        html += '<tr> <td style="width: 50.0000%;">{}</td> <td style="width: 50.0000%;">Success</td> </tr>'.format(host)

    except Exception as e: # print any exceptions
        print(e)
        html += '<tr> <td style="width: 50.0000%;">{}</td> <td style="width: 50.0000%;">Failed</td> </tr>'.format(host)
        i += 1
    # VERY IMPORTANT! Close the SSH connection with host otherwise you'll run into issues if connecting again in the same python session.

    s.close()
html += "</tbody> </table>"

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender = 'me@example.com'
recipient = ['you@example.com', 'you_another@example.com']

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Switches Backup"
msg['From'] = sender
msg['To'] = ", ".join(recipient)

msgContent = MIMEText(html, 'html')
msg.attach(msgContent)

# Send the message via local SMTP server.
m = smtplib.SMTP('smtpserver.example.com')
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
m.sendmail(sender, recipient, msg.as_string())
m.quit()
