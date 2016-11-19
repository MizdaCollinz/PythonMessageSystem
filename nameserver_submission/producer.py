from process_message_system import *

#Written by Benjamin Collins - BCOL602 - 9168328

class Producer(MessageProc):
    def main(self):
        super().main()
        self.buffer = 0
        # Request and assign buffer from nameserver
        self.give('nameserver', 'get_service', ('buffer', os.getpid()))
        self.receive(
            Message(
                'take_buffer',
                action=lambda bufferid: self.assignBuffer(bufferid)))

        for i in range(10):
            me.give(self.buffer, 'put', i * i)
        time.sleep(1) #Give consumer a chance to consume the buffer
        me.give(self.buffer, 'stop')
        me.give('nameserver','close_server')

    def assignBuffer(self, bufferid):
        self.buffer = bufferid


if __name__ =='__main__':
    me = Producer()
    time.sleep(1) # wait for nameserver to get buffer
    me.main()
    print('Producer is exiting')
    sys.exit()
