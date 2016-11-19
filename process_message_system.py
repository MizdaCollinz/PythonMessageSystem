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
        atexit.register(self.exit_handler)




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

        #Start up transfer thread if not already started
        if (not self.transfer_thread.is_alive()):
            self.transfer_thread.start()
            



    def receive(self, *acceptedMessages):

        #check for timeout - default timeout values assigned
        timeoutActive = False
        timeout = 10000
        timeoutAction = lambda: None
        timeProgress = 0 #default to no progress when method starts, nothing to resume from
        # only apply the first timeout found
        for potentialTimeout in acceptedMessages:
            if (isinstance(potentialTimeout, TimeOut)):
                #assign timeout values
                timeoutActive = True
                timeout = potentialTimeout.time
                timeoutAction = potentialTimeout.action
                break

        #prioritise the messages in the unmatched list of previously unmatched messages
        for message in self.unmatchedMessages:
            for messagetype in acceptedMessages:  # find the corresponding messagetype in input message objects
                if (isinstance(messagetype, Message)):
                    #check if message matches label or if label is ANY
                    if message[0] == messagetype.label or messagetype.label == 'any':
                        value = message[1]
                        #check if message guard check is satisfied
                        if (messagetype.guard() is True):
                            self.unmatchedMessages.remove(message)
                            #call message action with corresponding values if necessary
                            if (len(value) == 0): #call method with no parameters if no value given
                                return messagetype.action()
                            else:
                                for thevalue in value:
                                    return messagetype.action(thevalue)
        
        #loop through newly received messages until a message is returned or a timeout occurs
        while True:
            with self.arrived_condition:
                if (self.communication_queue.empty()):  # if no messages in queue wait
                    if timeoutActive: #if a timeout has been input use this path
                        timeoutTime = time.time() + timeout - timeProgress #calculate what the time will be when timeout expires
                        self.arrived_condition.wait(timeout)  # wait for a new message
                        if (time.time() > timeoutTime): #check if timeout has expired
                            return timeoutAction()
                        else:
                            #calculate the progress of the timeout if the timeout was interrupted
                            timeProgress = timeout - (timeoutTime - time.time())

                    else:#just wait if queue empty and no timeout is applied
                        self.arrived_condition.wait()


            message = self.communication_queue.get() #retrieve message from the queue

            for messagetype in acceptedMessages: #find the corresponding messagetype in input message objects
                if(isinstance(messagetype,Message)): #only match against instances of Message
                    if message[0] == messagetype.label or messagetype.label == 'any':
                        value = message[1] #values dumped in the give

                        if(messagetype.guard() == True): #check if guard is satisfied
                            if (len(value) == 0): #call method with no parameters if no value given
                                return messagetype.action()
                            else:
                                for thevalue in value:
                                    return messagetype.action(thevalue)




            #if message is not matched, append it to the unmatched list and check for newly received messages
            self.unmatchedMessages.append(message)






    def start(self,*parameters):
        # split into two processes
        pid = os.fork()
        if(pid == 0): 
            if(len(parameters) > 0):
                self.main(*parameters) #call main of child process
            else:
                self.main()#call main of child process
            sys.exit()
        else:
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
            pass #Ignore gives to closed pipes
            

    #From Robert's lectures
    def extract_from_pipe(self):
        my_pipe = "/tmp/" +str(os.getpid()) + "messagepipe"
        #This pipe is created in the main directly before this thread starts, check is unnecessary

        try:
            self.pipe_read = open(my_pipe,'rb')
        except FileNotFoundError:
            return #Ignore attempt to read a pipe that has already been deleted(program exiting)

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
        time.sleep(0.15) #Give program a chance to finish properly before deleting
	#Leads to a slight delay on process exit and cleanup, maximum of several seconds for most 		#complex multi_producer and multi_consumer
        if( os.path.exists('/tmp/' + str(myid) + 'messagepipe')):
            os.system('rm /tmp/' + str(myid) + 'messagepipe')




#Storage object for acceptable message types and their responses
#named parameters for action and guard
class Message:
    def __init__(self,label,action=lambda *x: None,guard=lambda: True):
        self.label = label
        self.action = action
        self.guard = guard

#Storage object for TimeOut values and response
class TimeOut:
    def __init__(self,time,action):
        self.time = time
        self.action = action
