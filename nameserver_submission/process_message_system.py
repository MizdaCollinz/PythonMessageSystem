import os
import pickle
import sys
import time
import threading
import queue
import time
import atexit

ANY = 'any'

#Written by Benjamin Collins - BCOL602 - 9168328
class MessageProc:
    def __init__(self):
        self.pipeDict = {}
        self.communication_queue = queue.Queue()
        currentpid = os.getpid()
        self.pipe_name = "/tmp/" + str(currentpid) + "messagepipe.fifo"
        self.unmatchedMessages = []
        self.nameServer = False




    def main(self,*parameters):
        # create pipe if it doesn't exist
        currentpid = os.getpid()
        pipe_name = "/tmp/"+str(currentpid)+"messagepipe"
        if not os.path.exists(pipe_name):
            os.mkfifo(pipe_name)

        # Create arrived condition
        self.arrived_condition = threading.Condition()
        # As per Robert's lectures start extracting messages in new thread
        self.transfer_thread = threading.Thread(target=self.extract_from_pipe, daemon=True)

        if (not self.transfer_thread.is_alive()):
            self.transfer_thread.start()
            pid = os.getpid()

        atexit.register(self.exit_handler)

    def receive(self, *acceptedMessages):

        #check for timeout
        timeoutActive = False
        timeout = 10000
        timeoutAction = lambda: None
        timeProgress = 0
        # only apply the first timeout found
        for potentialTimeout in acceptedMessages:
            if (isinstance(potentialTimeout, TimeOut)):

                timeoutActive = True
                timeout = potentialTimeout.time
                timeoutAction = potentialTimeout.action
                break

        for message in self.unmatchedMessages:
            for messagetype in acceptedMessages:  # find the corresponding messagetype in input message objects
                if (isinstance(messagetype, Message)):
                    if message[0] == messagetype.label or messagetype.label == 'any':
                        value = message[1]

                        if (messagetype.guard() is True):
                            self.unmatchedMessages.remove(message)
                            if (len(value) == 0):
                                return messagetype.action()
                            else:
                                return messagetype.action(*value)

        while True:
            with self.arrived_condition:
                if (self.communication_queue.empty()):  # if no messages in queue wait
                    if timeoutActive:
                        timeoutTime = time.time() + timeout - timeProgress
                        self.arrived_condition.wait(timeout)  # wait for a new message
                        if (time.time() > timeoutTime):
                            return timeoutAction()
                        else:
                            timeProgress = timeout - (timeoutTime - time.time())

                    else:
                        self.arrived_condition.wait()


            message = self.communication_queue.get()

            for messagetype in acceptedMessages: #find the corresponding messagetype in input message objects
                if(isinstance(messagetype,Message)): #only match against instances of Message
                    if message[0] == messagetype.label or messagetype.label == 'any':
                        value = message[1] #values dumped in the give

                        if(messagetype.guard() == True): #check if guard is satisfied
                            if (len(value) == 0): #call method with no parameters if no value given
                                return messagetype.action()
                            else:
                                for thevalue in value:
                                    #otherwise call method with value as input
                                    return messagetype.action(thevalue)
                        else:
                            pass





            self.unmatchedMessages.append(message)






    def start(self,*parameters):
        # split into two processes
        pid = os.fork()
        if(pid == 0):
            childid = os.getpid()
            if(len(parameters) > 0):
                self.main(*parameters) #call main of child process
            else:
                self.main()
            sys.exit()
        else:
            parentid = os.getpid()
            return pid  #return id of child to main



    def give(self,pid,label,*values):
        send_to_pipe = "/tmp/" + str(pid) + "messagepipe"

        if (not os.path.exists(send_to_pipe)):
            time.sleep(0.001) # wait if pipe doesnt exist
        #open pipe if not already opened and stored in dictionary
        if (not pid in self.pipeDict):
            fifo = open(send_to_pipe, "wb")
            self.pipeDict[pid] = fifo
        else:
            fifo = self.pipeDict[pid]

        try:

            #pickle message and dump in pipe
            pickle.dump((label,values),fifo)

            fifo.flush()
        except BrokenPipeError:
            pass
            #Ignore gives to closed pipes

    #Primarily from Robert's lectures
    def extract_from_pipe(self):
        my_pipe = "/tmp/" +str(os.getpid()) + "messagepipe"

        #Use nameserver pipe if this is a nameserver - Nameserver exclusive
        if(self.nameServer):
            my_pipe = "/tmp/nameservermessagepipe"
        self.pipe_read = open(my_pipe,'rb')

        with self.pipe_read as fifo:
            while True:
                try:
                    message = pickle.load(fifo)
                    with self.arrived_condition:
                        self.communication_queue.put(message)
                        self.arrived_condition.notify() #wake up anything waiting


                except EOFError: #no writer open yet
                    time.sleep(0.01) #Idle while writer doesnt exist

    def exit_handler(self):
        myid = os.getpid()
        if (os.path.exists('/tmp/' + str(myid) + 'messagepipe')):
            os.system('rm /tmp/' + str(myid) + 'messagepipe')





class Message:
    def __init__(self,label,action=lambda *x: None,guard=lambda: True):
        self.label = label
        self.action = action
        self.guard = guard

class TimeOut:
    def __init__(self,time,action):
        self.time = time
        self.action = action
