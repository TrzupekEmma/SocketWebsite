import socket
from datetime import date, time, datetime
import base64
from emmaTables import * 
from base64 import b64encode, b64decode
sessions=[]
sessionCounter=0;


userSites={}
#allows the placement of arbitrary text within html at runtime
#can either be used for simple text input or to add new website parts programatically
#ex {name} -> emma or {name} -> <div class="example"><div>
def smartParse(data,formatRules={},headers={}):
    output=b""
    i=0;
    type="pausePoint"
    forPair=(None,None)
    repeatChunk=b""
    ruleStart=-1
    enabled=0
    innerCount=0
    #this will run through until you find a pauspoint {pausepoint} and then use formatRules passed in to replace it    
    while i<len(data) :
        if(ruleStart==-1):
            if(bytes([data[i]]) == b'{'): #find the start index of the pause point 
                if(bytes([data[i+1]])==b'%'):
                    i=i+1
                    type=b"logic"
                else:
                    type=b'pausePoint'
                    if(enabled==-1):
                        ruleStart=-1
                ruleStart=i+2
            else:
                if(enabled>=0):
                    output+=bytes([data[i]])
                if(enabled==-2):
                    repeatChunk+=bytes([data[i]])

        else:
            if( (bytes([data[i]])==b'}' and type==b"pausePoint") or (bytes([data[i]])==b'%' and type==b"logic")): #find the end index of the pause point
                smartText=data[ruleStart:i].strip().lower();
                ruleStart=-1
                i=i+1
                if(type==b"pausePoint"):
                    if(enabled==-2):
                            repeatChunk+=b"{{ "+smartText+b" }}"
                    else:
                        if(smartText in formatRules and enabled != -1): #replace the point with the code the rule governs 
                            output+=formatRules[smartText]
                elif(type == b"logic"):
                    tokens=smartText.split(b" ")
                    logic=tokens[0];
                    print(logic)
                    if(logic==b"if"):
                        if(enabled==-2):
                            repeatChunk+=b"{% "+smartText+b" %}"
                        else:
                            enabled=-1
                            if(ruleComparison(b" ".join(tokens[1:]),formatRules)):
                                print(ruleComparison(b" ".join(tokens[1:]),formatRules))
                                enabled=1
                    elif(logic==b"elif"):
                        if(enabled==-2):
                            repeatChunk+=b"{%"+smartText+b" %}"
                        else:
                            enabled=-1
                            if(ruleComparison(b" ".join(tokens[1:]),formatRules)):
                                print(ruleComparison(b" ".join(tokens[1:]),formatRules))
                                enabled=1
                    elif(logic==b"else"):
                        if(enabled==-2):
                            repeatChunk+=b"{% "+smartText+b" %}"
                        else:
                            print(str(enabled)+" enabled previously")
                            enabled=-enabled
                    elif(logic==b"endfor"):
                        print("ending"+str(enabled));
                        print(innerCount)
                        print("about to start for");
                        inner,outer=forPair
                        print(outer)
                        for iterator in formatRules[outer]:
                            innerRules=formatRules
                            innerRules[inner]=iterator
                            output+=smartParse(repeatChunk,innerRules,headers);
                        repeatChunk=""
                        enabled=0
                    elif(logic==b"endif"):
                        print("ending"+str(enabled));
                        if(enabled==-2):
                            print(innerCount)
                            repeatChunk+=b"{% "+smartText+b" %}"
                            innerCount-=1;
                        else:
                            enabled=0
                    elif (logic==b"for" or logic == b"for("):
                        if(tokens[2]==b'in'):
                            print("starting for loop");
                            forPair=(tokens[1],tokens[3].split(b':')[0])
                            enabled=-2;
                    else:
                        print(b'logic not found')
                            
        i=i+1
    print("about to output:")
    print(output)
    return output


def template(fileName,formatRules={},headers={}):
    print(formatRules);
    print(b"loading template "+fileName)
    fileName=fileName[1:]
    addCustomHeaders(headers)
    if('user' in formatRules):
        print(formatRules['user']);
    
    with open(fileName.decode(),'rb') as file:
        return(smartParse(file.read(),formatRules,headers));
    return(output);


def addCustomHeaders(headers={}):
    response=b""
    #after you finish the code specific headers add any arbitrary headers passed in
    for key,value in headers.items():
        response+=key+b": "+value+b'\r\n';
    #close the connection and end the headers leading into the body
    response+=b"Connection: close\r\n\r\n"
    return(response);

def loadStatic(fileName):
    print(b'Loading the file:'+fileName)
    print(fileName)
    fileName=fileName[1:]
    with open(fileName,"rb") as file:
        return(file.read())
def createHeaderDynamic(code,fileName,userFunction,oldHeaders,filetype=b"",customHeaders={}):
    print(b"creating header code:"+str(code).encode()+b" filetype:"+filetype+b"fileName"+fileName)
    response=b""
    serverLine=b"Server: Emma's Custom Server \r\n"
    if(code==200):
        response+= b"HTTP/1.1 200 OK\r\n"
        response+=serverLine
        response+=b"Content-Type: text/html; charset=utf-8\r\n"

    #redirect message for post form substitution
    #instead of the normal role of opening a file here fileName serves as the redirect location    
    elif(code==303):
        response+=b"HTTP/1.1 303 See Other\r\n"
        response+=b"Location: "+fileName+b'\r\n';
        response+=b'Content-Type: text/html; charset=UTF-8\r\n'
        
    else: #code==404
        response+=b'HTTP/1.1 404 Not Found\r\n'
        response+=b"Content-Type: text/html; charset=utf-8\r\n"
        response+=formatDatetime(datetime.now());
    
    response+=addCustomHeaders(customHeaders);
    body=userFunction(oldHeaders);
    print(type(body))
    if(type(body)==type((1,2))):
        if(body[1]==-1):
            return(body[0])
    return response+body;


#Generate http responses using codes and other values                
def createHeaderStatic(code,filetype,fileName):
    print(b"loading resource code:"+str(code).encode()+b" filetype:"+filetype+b"fileName"+fileName)
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
        if(filetype==b"css"):
            response+=b"Content-Type: text/css; charset=utf-8\r\n"
        else:
            response+=b"Content-Disposition: inline; filename=\""+fileName.split(b'/')[1]+b"\"\r\n"
            response+=b"Content-Type: image/"+filetype+b"; charset=utf-8\r\n"
        
        #add the timecode
        response+=formatDatetime(datetime.now())
    

    #TODO add caching (probably won't happen honestly but a girl can dream)
    elif(code==304):
        response+= b"HTTP/1.1 304 NOT MODIFIED\r\n";
        response+=serverLine;
    
    #classic 404 message
    else:
        return(createHeaderDynamic(404,b"html",b"/notFound.html",pageNotFound))
    response+=b"\r\n"
    fullSend=response+loadStatic(fileName)
    return(fullSend)

#Get all the values out of any form tables form after submitting
def parseForm(headers):
    formValues={}
    if(headers[b"method"]==b"POST"):
        for line in headers[b"body"].split(b'\n'):
            for kv in line.split(b'&'):
                if(b'=' in kv):
                    key,value=kv.split(b'=')     
                    formValues[key]=value;
    return(formValues)

def redirect(url,requestHeaders,customHeaders={}):
    if(url in userSites):
        return(createHeaderDynamic(303,url,userSites[url],requestHeaders,customHeaders=customHeaders),-1)
    return(createHeaderDynamic(404,"/static/notFound.html",pageNotFound,requestHeaders))

def pageNotFound(headers):
    return(template(b"/sites/notFound.html"))
userSites[b'/notFound']=pageNotFound

def route(requestHeaders):
    global userSites;
    fileName=requestHeaders[b'subDirectory']
    print(fileName);
    if(fileName in userSites):
        print(b"Directing to"+fileName)
        return(createHeaderDynamic(200,b"html",userSites[fileName],requestHeaders))
    else:
        if(b'.' in fileName and b'/' in fileName):
            sds=fileName.split(b'/')
            if(len(sds)>2):
                fileType=sds[2].split(b'.')[1];
                if(sds[1]==b'images'):
                    return(createHeaderStatic(200,fileType,fileName))
                elif(sds[1]==b'style'):
                    return(createHeaderStatic(200,fileType,fileName))
            
        
    return(createHeaderDynamic(404,b"/sites/notFound.html",pageNotFound,requestHeaders))
#Split the headers into dictionary entriess
#TODO correct the mistake that method and subDirectory are being reffered to as headers, probably by making a class for the http requests 
def createHeaderDict(data):
    lines=data.split(b'\r\n')
    headers={};
    meDer=lines[0].split(b' ')
    headers[b"method"] = meDer[0];
    headers[b"subDirectory"] = meDer[1];
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
    headers[b"body"]=body;
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
                        response=route(createHeaderDict(data));
                        #print(response);
                        conn.sendall(response);
        
        #termination
        except KeyboardInterrupt:
            print("Interupt detected exiting now");
        s.shutdown(socket.SHUT_RDWR)
        s.close() 

####Starting point for website specific code#####
def deleteCookie(name,outHeaders={}):
    outHeaders[b'Set-Cookie']=name+b'=\"\"; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    return(outHeaders)


def root(headers):
    return(redirect(b"/home",headers))
userSites[b'/']=root


def home(headers):
    rules={}
    if(b'Cookie' in headers):
        rules[b'user']=b64decode(headers[b'Cookie'][8:]).split(b'-')[0]
        print(rules[b'user'])
        print("were the user rules ")
    else:  
        print("cookie not found")
    rules[b'test']=True;
    rules[b'coolnumbers']=(3,1,4,1,5);
    return(template(b"/sites/home.html",formatRules=rules,headers=headers))
userSites[b'/home']=home

def login(headers):
    global sessionCounter
    formValues=parseForm(headers);
    print(formValues);
    if(b'cookie' not in headers):
        if(headers[b"method"]==b"POST"):
            print("bsubmited post")
            sessionCookie=b"Session= "+b64encode(formValues[b'username']+b"-"+str(sessionCounter).encode());
            sessionCounter+=1;
            sessions.append(sessionCookie);
            outHeaders={}
            outHeaders[b"Set-Cookie"]=sessionCookie;
            return(redirect(b"/home",headers,outHeaders))
    else:
        deleteCookie(b"Session")
    return(template(b"/sites/login.html"))
userSites[b'/login']=login



def logout():
    deleteCookie(b"Session")
    return(template(b""))
userSites[b'/logout']=logout

##### END point for website specific code####
if __name__ == "__main__":
    start_server()

