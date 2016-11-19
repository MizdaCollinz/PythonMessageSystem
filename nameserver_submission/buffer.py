from process_message_system import *

#Written by Benjamin Collins - BCOL602 - 9168328
#Buffer based on that used in multiple_consumer.py
class Buffer(MessageProc):

    def main(self):
        super().main()
        me.give('nameserver', 'assign_buffer', ('buffer',os.getpid())) #assign self as buffer to nameserver

        buffer_space = []
        while True:
            self.receive(
                Message(
                    'put',
                    action=lambda data: buffer_space.append(data)),
                Message(
                    'get',
                    guard=lambda: len(buffer_space) > 0,
                    action=lambda consumer: self.give(consumer, 'data', buffer_space.pop(0))),
                Message(
                    'stop',
                    guard=lambda: len(buffer_space) == 0,
                    action=self.finish))

    def finish(self):
        print('Buffer is exiting')
        sys.exit()

if __name__ =='__main__':
    me = Buffer()
    me.main()
