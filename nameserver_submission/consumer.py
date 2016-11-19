from process_message_system import *

#Written by Benjamin Collins - BCOL602 - 9168328

 #Consumer as based on multiple_consumer.py
class Consumer(MessageProc):

    def main(self):
        self.buffer = 0
        super().main()
        self.count = 0
        time.sleep(0.1)

        #Request and assign buffer from nameserver
        self.give('nameserver', 'get_service',('buffer',os.getpid()))
        self.receive(
            Message(
                'take_buffer',
                action=lambda bufferid: self.assignBuffer(bufferid)))

        while True:
            time.sleep(0.01)
            self.give(self.buffer, 'get', os.getpid())
            self.receive(
                Message(
                    'stop',
                    action=self.finish),
                Message(
                    ANY,
                    action=self.handle_input),
                TimeOut(
                    5,
                    action=self.finish
                ))


    def handle_input(self, data):
        print('{} was handled by the consumer'.format(data))
        self.count += 1

    def assignBuffer(self,bufferid):
        self.buffer = bufferid

    def finish(self):
        print("Consumer received a count of " + str(self.count) + ' and is now exiting.')
        sys.exit()

if __name__ =='__main__':
    me = Consumer()
    time.sleep(1) #wait for nameserver to get buffer
    me.main()
