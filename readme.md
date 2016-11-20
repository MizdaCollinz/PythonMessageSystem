This is a simple message passing system which creates additional processes using the Unix Fork functionality (Only works in Linux)
Messages are passed through pipes associated with the ID of their process

To test usage of the process message system, use any of the demo files provided

The nameserver section has its own readme to explain how it is used, it is a simple implementation using the process message system functionality with a statically named nameserver that all other processes can get access to without having to fork.

The message system uses a Give() call to send a message to a particular process ID
Each process has a thread dedicated to retrieving messages from its designated pipe file
The message system uses a Receive() call to process messages received on its pipe and placed into its message queue

A guard system is used to check if a certain condition is met before a message is processed from the queue
A receive call specifies acceptable types of messages and only proceeds to process relevant messages while storing others for later receive calls
A timeout system is used to drop a receive call if no acceptable messages are received within a certain amount of time