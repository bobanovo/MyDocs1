from  MyDocs_config import * #configuration for all
import logging
import zmq
import sys
# import click # just now not needed
import datetime
import time
import sqlite3 as db #for sqlite version

def listen():
    '''
    Receive message via ZeroMQ
    '''
    with zmq.Context() as context:
        with context.socket(zmq.PULL) as socket:
    
            socket.bind('tcp://%s:%s' % (ZMQ_LOGGER_SERVER, ZMQ_LOGGER_PORT))
            log.info('Listening... on tcp://*:%s'  % ZMQ_LOGGER_PORT)
    
            while True:
                message = socket.recv_string()
                if message: 
                    log.info('\n Received message: ' + message + '\n')
                    if message.find("::") >= 0:
                        # expect Date::From::Subject::Filename::LinkFilename - 0:4
                        messageData=message.split("::")
                        
                        log.debug('Data for SQL:')
                        log.debug(messageData)
                        try:
                            storedata_sqlite(DB_DBNAME_SQLITE,DB_TBLNAME_SQLITE,messageData)
                            log.debug('Data stored')
                        except Exception as e:
                            log.error('Failed to store into DB: '+ str(e))
                        finally:
                            log.info('-----------------------------------------------------------')
                    else:
                        log.debug('no data for store (without parsertag as '+ZMQ_PARSERTAG)
                    
                
                time.sleep (1) 
                
    
# store received data
def storedata_sqlite(database, table, record):
    '''
    Store data into storage - as DB - sqlite (table recdata1)
    '''    
    try:
        dbcon = db.connect(database)
        with dbcon:
            dbcur = dbcon.cursor()    
            # dbcur.execute('INSET INTO %s VALUES ()' % table) #change to insert data
            dbcur.executemany("INSERT INTO " + table + " VALUES(?, ?, ?, ?, ?)", [record]) # expect 5 strings + 1 AutoID! ... data is list of list ((A,B,C),(AA,BB,CC),...)
            
        data = dbcur.fetchone()
        
        
    except dbcon.Error as e:
        log.error('Failed during save to DB: '+ str(e))
        print("Error %s:" % e.args[0])
        sys.exit(1)    
    finally:
        if dbcon:
            dbcon.close()    
    

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
    log.info('DB_CLIENT: '+DB_CLIENT)
    log.info('DB_SERVER_SQLITE: '+DB_SERVER_SQLITE)
    log.info('DB_PORT_SQLITE: '+DB_PORT_SQLITE)
    log.info('DB_USER_SQLITE: '+DB_USER_SQLITE)
    log.info('DB_PASS_SQLITE: '+DB_PASS_SQLITE)
    log.info('DB_DBNAME_SQLITE: '+DB_DBNAME_SQLITE)
    log.info('DB_TBLNAME_SQLITE: '+DB_TBLNAME_SQLITE)   
    log.info('-----------------------------------------------------------')
    
    #check DB
    try:
        dbcon = db.connect(DB_DBNAME_SQLITE)
        dbcur = dbcon.cursor()    
        dbcur.execute('SELECT SQLITE_VERSION()')
        data = dbcur.fetchone()         
        log.debug ("SQLite version: %s" % data)
    except dbcon.Error as e:
        print("Error %s:" % e.args[0])
        sys.exit(1)    
    finally:
        if dbcon:
            dbcon.close()    
    
    listen()
