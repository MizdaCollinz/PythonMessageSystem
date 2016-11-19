from process_message_system import *

NAMESERVER = '/tmp/nameservermessagepipe'

#Written by Benjamin Collins - BCOL602 - 9168328

class name_server(MessageProc):

    def main(self):
        self.nameServer = True
        if not os.path.exists(NAMESERVER):
            os.mkfifo(NAMESERVER)

        # Create arrived condition
        self.arrived_condition = threading.Condition()
        # As per Robert's lectures start extracting messages in new thread
        self.transfer_thread = threading.Thread(target=self.extract_from_pipe, daemon=True)

        if (not self.transfer_thread.is_alive()):
            self.transfer_thread.start()

        self.service_dictionary = {}

        while True:
            self.receive(
                Message(
                    'assign_buffer',
                    guard = lambda: True,
                    action = lambda input : self.add_service(input)
                ),
                Message(
                    'get_service',
                    guard = lambda: not len(self.service_dictionary) == 0, #check if buffer exists
                    action=lambda input: self.give(input[1],'take_buffer',self.service_dictionary[input[0]])#provide first buffer by default
                ),
                Message(
                    'close_server',
                    guard = lambda: True,
                    action= lambda: self.end_server()
                ))
    def add_service(self,input):
        self.service_dictionary[input[0]] = (input[1])
        print(str(input[1]) + " assigned as " + input[0])

    def end_server(self):
        print('Server is exiting')
        if (os.path.exists('/tmp/nameservermessagepipe')):
            os.system('rm /tmp/nameservermessagepipe')
        sys.exit()






if __name__ =='__main__':

    #Start up the name server
    me = name_server()
    me.main()
