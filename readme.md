This is a simple message passing system which creates additional processes using the Unix Fork functionality (Only works in Linux)
Messages are passed through pipes associated with the ID of their process

To test usage of the process message system, use any of the demo files provided

The nameserver section has its own readme to explain how it is used, it is a simple implementation using the process message system functionality with a statically named nameserver that all other processes can get access to without having to fork.