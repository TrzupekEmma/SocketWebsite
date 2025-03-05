import socket
from datetime import date, time, datetime
import base64
from emmaTables import * 
from base64 import b64encode, b64decode
sessions=[]
sessionCounter=0;


    

#allows the placement of arbitrary text within html at runtime
#can either be used for simple text input or to add new website parts programatically
#ex {name} -> emma or {name} -> <div class="example"><div>
def template(fileName,assembledHeader,formatRules):
    if('user' in formatRules):
        print(formatRules['user']);
    output=assembledHeader
    
    with open(fileName.decode(),'rb') as file:
        ruleStart=-1; #-1 when you are not in a pausepoint or the index of the start of the pausepoint otherwise
        type=b"pausePoint";
        enabled=0;
        for line in file:    
            i=0; 
            #this will run through until you find a pauspoint {pausepoint} and then use formatRules passed in to replace it    
            while i<len(line) :
                if(ruleStart==-1):
                    if(bytes([line[i]]) == b'{'): #find the start index of the pause point 
                        if(bytes([line[i+1]])==b'%'):
                           i=i+1
                           type=b"logic"
                        else:
                            type=b'pausePoint'
                            if(enabled==-1):
                                ruleStart=-1
                        ruleStart=i+2;
                    else:
                        if(enabled!=-1):
                            output+=bytes([line[i]]);
                else:
                    if( (bytes([line[i]])==b'}' and type==b"pausePoint") or (bytes([line[i]])==b'%' and type==b"logic")): #find the end index of the pause point
                        smartText=line[ruleStart:i].strip().lower();
                        ruleStart=-1
                        i=i+1
                        if(type==b"pausePoint"):
                            if(smartText in formatRules and enabled != -1): #replace the point with the code the rule governs 
                                output+=formatRules[smartText]
                        elif(type == b"logic"):
                            tokens=smartText.split(b" ")
                            logic=tokens[0];
                            if(logic==b"if"):
                                enabled=-1
                                if(ruleComparison(b" ".join(tokens[1:]),formatRules)):
                                    print(ruleComparison(b" ".join(tokens[1:]),formatRules))
                                    enabled=1
                            elif(logic==b"elif"):
                                enabled=-1
                                if(ruleComparison(b" ".join(tokens[1:]),formatRules)):
                                    print(ruleComparison(b" ".join(tokens[1:]),formatRules))
                                    enabled=1
                            if(logic==b"else"):
                                print(str(enabled)+" enabled previously")
                                enabled=-enabled
                            elif(logic==b"end"):
                                enabled=0;
                i=i+1
            output+=b"\n"
    return(output);
                        
#Generate http responses using codes and other values                
def response(code,filetype,fileName,headers={},formatRules={}):
    today=date.today()  
    today.weekday
    response=b""
    serverLine=b"Server: Emma's Custom Server \r\n"
    
    #your basic sucess case
    if(code==200):

        #State the code and server
        response+= b"HTTP/1.1 200 OK\r\n"
        response+=serverLine

        #State whether you are serving an html file, css file, or image 
        if(filetype==b"html"):
            response+=b"Content-Type: text/html; charset=utf-8\r\n"
        elif(filetype==b"css"):
            response+=b"Content-Type: text/css; charset=utf-8\r\n"
        else:
            response+=b"Content-Disposition: inline; filename=\""+fileName.split(b'/')[1]+b"\"\r\n"
            response+=b"Content-Type: image/"+filetype+b"; charset=utf-8\r\n"
        
        #add the timecode
        response+=formatDatetime(datetime.now())
    
    #redirect message for post form substitution
    #instead of the normal role of opening a file here fileName serves as the redirect location    
    elif(code==303):
        response+=b"HTTP/1.1 303 See Other\r\n"
        response+=b"Location: "+fileName+b'\r\n';
        response+=b'Content-Type: text/html; charset=UTF-8\r\n'

    #TODO add caching (probably won't happen honestly but a girl can dream)
    elif(code==304):
        response+= b"HTTP/1.1 304 NOT MODIFIED";
        response+=serverLine;
    
    #classic 404 message
    else:
        response+=b'HTTP/1.1 404 Not Found\r\n'
        response+=formatDatetime(datetime.now());

    #after you finish the code specific headers add any arbitrary headers passed in
    for key,value in headers.items():
        response+=key+b": "+value+b'\r\n';
    
    #close the connection and end the headers leading into the body
    response+=b"Connection: close\r\n\r\n"

    
    if(b"." in fileName):
        if(filetype==b'html'): #switch to templating for html files 
            return(template(fileName,response,formatRules));
        else: #otherwise just load the file into the body of the http request 
            with open(fileName.decode(),'rb') as file:
                response+=file.read()
    return response

#Get all the values out of any form tables form after submitting
def parseForm(headers):
    formValues={}
    if(headers["method"]==b"POST"):
        for line in headers["body"].split(b'\n'):
            for kv in line.split(b'&'):
                if(b'=' in kv):
                    key,value=kv.split(b'=')     
                    formValues[key]=value;
    return(formValues)

####Starting point for website specific code#####

def root(headers):
    formValues=parseForm(headers);
    return(response(303,b"html",b"/login"))

def home(headers):
    rules={}
    if(b'Cookie' in headers):
        rules[b'user']=b64decode(headers[b'Cookie'][8:]).split(b'-')[0]
        print(rules[b'user'])
        print("were the user rules ")
    else:  
        print("cookie not found")
    rules[b'test']=True;
    return(response(200,b'html',b'sites/home.html',formatRules=rules))
def deleteCookie(name,outHeaders={}):
    outHeaders[b'Set-Cookie']=name+b'=\"\"; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    return(outHeaders);
def login(headers):
    global sessionCounter
    formValues=parseForm(headers);
    print(formValues);
    if('cookie' not in headers):
        if(headers["method"]==b"POST"):
            print("submited post")
            sessionCookie=b"Session= "+b64encode(formValues[b'username']+b"-"+str(sessionCounter).encode());
            sessionCounter+=1;
            sessions.append(sessionCookie);
            outHeaders={}
            outHeaders[b"Set-Cookie"]=sessionCookie;
            return(response(303,b"html",b"/home",outHeaders))
    else:
        deleteCookie("Session")
    return(response(200,b"html",b"sites/login.html"))

def pageNotFound(headers):
    return(response(404,b"html",b"sites/notFound.html"))
def logout():
    deleteCookie("Session")
    return(response(303,b"html",b"/logout",outHeaders))
def route(headers):
    print(headers);
    fileName=bytearray(headers['subDirectory'])
    if(fileName==b'/'):
        return(root(headers))
    if(fileName==b'/login'):
        return(login(headers))
    if(fileName==b'/home'):
        return(home(headers))
    else:
        if(b'.' in fileName and b'/' in fileName):
            del fileName[0]
            sds=fileName.split(b'/')
            if(len(sds)>1):
                fileType=sds[1].split(b'.')[1];
                if(sds[0]==b'images'):
                    return(response(200,fileType,fileName))
                elif(sds[0]==b'style'):
                    return(response(200,fileType,fileName))
            
        
    return(pageNotFound(headers))
##### END point for website specific code####

#Split the headers into dictionary entries
#TODO correct the mistake that method and subDirectory are being reffered to as headers, probably by making a class for the http requests 
def createHeaderDict(data):
    lines=data.split(b'\r\n')
    headers={};
    meDer=lines[0].split(b' ')
    headers["method"] = meDer[0];
    headers["subDirectory"] = meDer[1];
    body=b""
    inBody=False
    for line in lines[1:]:
        if(not inBody):
            kv=line.split(b':')
            if(len(kv)>1):
                headers[kv[0].strip()]=kv[1].strip()
            else:
                inBody=True
        else:
            body+=line+b'\n';
    headers["body"]=body;
    return(headers)

def start_server():
    """Starts a simple server to listen for HTTP requests."""
    host = '127.0.0.1'
    port = 8080
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            while(True):
                s.listen()
                print(f"Server listening on {host}:{port}")
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if(data):
                        conn.sendall(route(createHeaderDict(data)))
        
        #termination
        except KeyboardInterrupt:
            print("Interupt detected exiting now");
        s.shutdown(socket.SHUT_RDWR)
        s.close() 

if __name__ == "__main__":
    start_server()