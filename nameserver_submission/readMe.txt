#Written by Benjamin Collins - BCOL602 - 9168328

To use the nameserver, run script.sh using "./script.sh"

The nameserver registers a service(currently buffers) by sending it the message
 -	give(nameserver,'assign_buffer',('servicename',pid) 
where pid is the Process ID of the buffer which is stored in the NameServer
and this pid is mapped to they key 'servicename' so other types of services can also be set and retrieved


The nameserver retrieves aservice when a client sends the message
 - 	give(nameserver,'get_buffer', ('servicename',pid) 
where pid is the Process ID of the client which is requesting the Buffer's ID
and 'servicename' is the key representing which service the client is looking for by name

The nameserver sends a message back to that pid (give pid, 'take_buffer', bufferID)
where bufferID is the value that was mapped to the service name provided in this case the buffer.

