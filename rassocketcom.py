import sys
import numpy as np
from numpy import inf
# import pyzed.sl as sl
# import cv2
import os 
from socket import * 
from decimal import Decimal
############################################################

class CJetScketUDPSever(object):    
    '''
        # as server
        # Message Receiver 
    '''
    def __init__(self, sock=None):
        self.host = ""#"192.168.1.12"  # should be the addres o """
        self.port = 13000 
        self.buf = 1024 
        self.addr = (self.host, self.port) 
        self.UDPSock = socket(AF_INET, SOCK_DGRAM) 
        self.UDPSock.bind(self.addr)         
        print ("Waiting to receive messages ...")
        
          

    def Sever2Close(self):
        self.UDPSock.close() 
        os._exit(0)


    

    def RasReceive(self, EOFChar='\036'):

        """
        msg = ''
        (self.data, self.addr) = self.UDPSock.recvfrom(self.buf) 

        # print ("Received message: " + str(self.addr ))
        #     if self.data == "exit": 
        msg = self.data.decode('utf-8')
        return msg
        """

        (self.data, self.addr) = self.UDPSock.recvfrom(self.buf) 
        # print ("Received message: " + self.data.decode('utf-8'))
        print ("Received message from {sender} ".format(sender = self.addr))
        data= self.data.decode('utf-8')
        # print ("Received message: " + data)
        text = eval('[' + data + ']')
        return text
    def RasReceive_data(self, EOFChar='\036'):

        """
        msg = ''
        (self.data, self.addr) = self.UDPSock.recvfrom(self.buf) 

        # print ("Received message: " + str(self.addr ))
        #     if self.data == "exit": 
        msg = self.data.decode('utf-8')
        return msg
        """

        (self.data, self.addr) = self.UDPSock.recvfrom(self.buf) 
        # print ("Received message: " + self.data.decode('utf-8'))
        print ("Received message from {sender} ".format(sender = self.addr))
        data= self.data.decode('utf-8')
        # print ("Received message: " + data)
        # text = eval('[' + data + ']')
        return data
 