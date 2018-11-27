from  MyDocs_config import *
import imaplib
import email
import logging
import zmq
import os
import time
import sys
from pathlib import PurePosixPath
import uuid
import io

# Connect to an IMAP server
def connect(server, user, password):
    m = imaplib.IMAP4_SSL(server)
    m.login(user, password)
    m.select()
    return m

# Download all attachment files for a given email
def downloaAttachmentsInEmail(m, emailid, outputdir):
    resp, data = m.fetch(emailid, "(RFC822)") # "(BODY.PEEK[])")
    email_body = data[0][1]
    mail = email.message_from_string(email_body)
    
    # read header - for SUBJECT FROM TO
    for header in [ 'subject', 'to', 'from','date' ]:
        log.info('%-8s: %s' % (header.upper(), mail[header]))
    
    
    # check attachment
    if mail.get_content_maintype() != 'multipart': # no attach
        return 
    
    for part in mail.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
    
        # save attachment
        if (part.get_filename()):
            # create link
            filename=part.get_filename()
            file_extension= PurePosixPath(filename).suffix
            
            link_filename = outputdir + '/' + str(uuid.uuid1()) +file_extension
            fp = open(link_filename, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()
            log.debug('Saved file: '+filename+' as: '+link_filename)
            

    # temp = m.store(emailid,'+FLAGS', '\\Seen')
    # move to Processed and delete
    # m.copy(emailid, 'Processed')
    # temp = m.store(emailid, '+FLAGS', r'(\Deleted)')
    # typ, response = m.expunge() # delete flaged mails
    try:
        ZMQmsg=mail['date']+ZMQ_PARSERTAG+mail['from']+ZMQ_PARSERTAG+mail['subject']+ZMQ_PARSERTAG+filename+ZMQ_PARSERTAG+link_filename
        log.info('%-8s: %s' % ('ZMQ',ZMQmsg))
        ZMQsend(ZMQmsg,ZMQ_LOGGER_SERVER, ZMQ_LOGGER_PORT, ZMQ_TIMEOUT)  
        ZMQsend(ZMQmsg,ZMQ_SEAFILE_SERVER, ZMQ_SEAFILE_PORT, ZMQ_TIMEOUT)  
        log.info('-----------------------------------------------------------') # end of one mail
    except Exception as e:
        log.error('Failed to send info about emails attachments via ZMQ: '+ str(e))

# Download all the attachment files for all emails in the inbox.
def downloadAllAttachmentsInInbox(server, user, password, outputdir):
    m = connect(server, user, password)
    resp, items = m.search(None, "(ALL)")
    items = items[0].split()
    for emailid in items:
        downloaAttachmentsInEmail(m, emailid, outputdir)
        time.sleep (1)
    
    #delete mails woth flag DELETE
    # typ, response = m.expunge()
    try:
        m.close()
    except:
        pass
    m.logout()    
        
        
def ZMQsend(message,server,port,timeout):
    '''
    Send message to server via ZeroMQ
    '''
    try:
        serveradd = 'tcp://' + server + ":" + port
        if (True): # ready to some condition in future :-)
            with zmq.Context() as context:
                # context.setsockopt(zmq.LINGER, timeout)
                with context.socket(zmq.PUSH) as socket:
                    socket.connect(serveradd)
                    socket.send_string(message,zmq.NOBLOCK) # pro timeout, ale nefunguje
    except Exception as e:
        log.error('Failed in sending via ZMQ: '+ str(e))


# ---------------------------------------------------------------------




if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)
    f_handler = logging.FileHandler(LOG_PATH_FILE+__file__+'.log')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)    
    log.addHandler(f_handler)
    
    log.setLevel('INFO')
    
    log.debug('Version of python: ' + sys.version) 
    log.info('Starting '+__file__)
    log.info('IMAP_SERVER: '+IMAP_SERVER)
    log.info('IMAP_USER: '+IMAP_USER)
    log.info('FILE_OUTDIR: '+FILE_OUTDIR)
    log.info('LOG_FILE: '+LOG_PATH_FILE+__file__+'.log')
    log.info('-----------------------------------------------------------')
     
    downloadAllAttachmentsInInbox(IMAP_SERVER, IMAP_USER, IMAP_PASS,FILE_OUTDIR)
    
