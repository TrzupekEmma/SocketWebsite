##even jankier version of the http request tool that I just hardcode instead of using command line arguments
import socket, sys
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("localhost",8080,))

offset=0;
output=b"POST /login HTTP/1.1\r\nHOST: localhost/ \r\n Host: 127.0.0.1:8080\r\n Content-Type: application/x-www-form-urlencoded\r\n\r\n username=testuser&password=testpass&submit=submit"
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
