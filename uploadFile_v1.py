from  MyDocs_config import * #configuration for all
import logging
import zmq
import sys
# import click # just now not needed
import datetime
import time
import requests
from pathlib import PurePosixPath


def listen():
    '''
    Receive message via ZeroMQ
    '''
    with zmq.Context() as context:
        with context.socket(zmq.PULL) as socket:
    
            socket.bind('tcp://%s:%s' % (ZMQ_SEAFILE_SERVER, ZMQ_SEAFILE_PORT))
            log.info('Listening... on tcp://*:%s \n'  % ZMQ_SEAFILE_PORT)
    
            while True:
                message = socket.recv_string()
                if message: 
                    log.info('\n Received message: ' + message + '\n')
                    if message.find("::") >= 0:
                        # expect Date::From::Subject::Filename::LinkFilename - 0:4
                        messageData=message.split("::")
                        
                        log.debug('Data for uploading:')
                        log.debug(messageData)
                        try:
                            log.info('Uploading file from %s as %s' % (messageData[3],messageData[4]))
                            upload_data_Seafile(messageData[3],messageData[4]) 
                            log.debug('File uploaded')
                        except Exception as e:
                            log.error('Failed to upload to SeaFile: '+ str(e))
                        finally:
                            log.info('-----------------------------------------------------------')
                            pass
                    else:
                        log.debug('no data for store (without parsertag as '+ZMQ_PARSERTAG)
                    
                
                time.sleep (1) 
                
def get_upload_link(url, token):
    resp = requests.get(
        url, headers={'Authorization': 'Token {token}'. format(token=token)}
    )
    return resp.json()


def upload_data_Seafile(filename, link_filename):
    # replace with your token
    token = SEAFILE_TOKEN
    # replace with your library id
    try:
        upload_link = get_upload_link(SEAFILE_LINK, token)
        log.debug (upload_link)
        log.debug ('filename: %s + link to file: %s' % (filename, link_filename))
        response = requests.post(
            upload_link, data ={'name':'tst.st', 'parent_dir':'/'},
            files={'file': open(link_filename, 'rb')},
            headers={'Authorization': 'Token {token}'. format(token=token)},
        )
        log.debug('Upload response: ')
        log.debug(response)
        #log.info('-----------------------------------------------------------')
        only_filename=PurePosixPath(link_filename).name
        log.debug(only_filename)
        renameFile_Seafile(filename, only_filename)
        pass
    except Exception as e:
        log.error('Failed to store into SeaFile: '+ str(e))    
    

def renameFile_Seafile(new_filename, orig_filename):
    # replace with your token
    token = SEAFILE_TOKEN
    # replace with your library id
    try:
        upload_link='http://%s/api2/repos/caf3810f-45be-4bc1-af6f-329828c7f5e7/file/?p=/%s' % (SEAFILE_SERVER+':'+SEAFILE_PORT, orig_filename)
        response = requests.post(
            upload_link, data ={'operation':'rename', 'newname':new_filename},
            headers={'Authorization': 'Token {token}'. format(token=token)},
        )        

    except:
        pass



# ----------------------------------------------------------------
if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)
    f_handler = logging.FileHandler(LOG_PATH_FILE+__file__+'.log')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)    
    log.addHandler(f_handler)
    
    log.setLevel('DEBUG')
    
    log.debug('Version of python: ' + sys.version)
    log.info('Starting '+__file__)
    log.info('LOG_FILE: '+LOG_PATH_FILE+__file__+'.log')
    log.info('SEAFILE_SERVER: '+SEAFILE_SERVER)
    log.info('SEAFILE_PORT: '+SEAFILE_PORT)
    log.debug('SEAFILE_token: '+SEAFILE_TOKEN)
    log.debug('SEAFILE:LINK: '+SEAFILE_LINK)
    log.info('ZMQ_SEAFILE_SERVER: '+ZMQ_SEAFILE_SERVER)
    log.info('ZMQ_SEAFILE_PORT: '+ZMQ_SEAFILE_PORT)
    
    log.info('-----------------------------------------------------------')
    
        
    listen()
