##janky little tool to make HTTP requests
import socket, sys
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("localhost",8080,))

offset=0;
method=b"GET "
if(len(sys.argv)<2):
	print("specify where to query");
	exit(-1);
if(sys.argv[1][0]=='-'):
	offset=1
	for char in sys.argv[1][1:]:
		if(char=='p'):
			method=b"POST "
output=method+sys.argv[1+offset].encode()+b" HTTP/1.1\r\nHOST: localhost/ \r\n"
if(len(sys.argv)>2+offset):
        for arg in sys.argv[2+offset:]:
                output+=arg.encode()+b'\r\n'
output+=b'\r\n'
print(output);
s.send(output);

fullData=b''
while True:
        data=s.recv(1024);
        if (len(data) < 1) :
                break
        fullData+=data
s.close()
dataLines=fullData.split(b'\n');
for line in dataLines:
        print(line)
