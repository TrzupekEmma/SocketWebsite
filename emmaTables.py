

#really unimportant just for formatting weekdays
def getDayStr(dayInt):
    match dayInt:
        case 0:
            return "Mon"
        case 1:
            return "Tue"
        case 2:
            return "Wed"
        case 3:
            return "Thu"
        case 4:
            return "Fri"
        case 5:
            return "Sat"
        case 6:
            return "Sun"
            
#also unimportant for formatting Months
def getMonthStr(monthInt):
    match monthInt:
        case 0:
            return "Jan"
        case 1:
            return "Feb"
        case 2:
            return "Mar"
        case 3:
            return "Apr"
        case 4:
            return "May"
        case 5:
            return "Jun"
        case 6:
            return "Jul"
        case 7:
            return "Aug"
        case 8:
            return "Sep"
        case 9:
            return "Oct"
        case 10:
            return "Nov"
        case 11:
            return "Dec"

#turn date time object into the standardized http date format
def formatDatetime(thisDateTime):
    thisDate=thisDateTime.date()
    thisTime=thisDateTime.time()
    output="Date: "+getDayStr(thisDate.weekday())+", "+str(thisDate.day).ljust(2,"0")+" "+getMonthStr(thisDate.month-1)+" "+str(thisDate.year)+" "+thisTime.isoformat(timespec='seconds')+" GMT\r\n"
    return(output.encode())
def canBeInt(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
    
#This just straight up doesn't work for almost any edge case
#TODO get your shit together girl
def ruleComparison(comparison,formatRules={}):
    comparison=comparison.strip().lower()
    print(b'comparison is '+comparison)


    if(b'(' in comparison ):
        print("()")
        count=0;
        first=-1;
        i =0
        while i < len(comparison):
            byteChar=bytes([comparison[i]])
            if(byteChar==b'('):
                count+=1;
                if(first==-1):
                    first=i;
            if(byteChar==b')'):
                count-=1;
                if(count==0):
                    print(str(first)+" "+str(i))
                    return(ruleComparison(comparison[0:first]+str(ruleComparison(comparison[first+1:i],formatRules)).encode()+comparison[i+1:],formatRules))
            i=i+1
            
    
    elif(b"and" in comparison):
        left, right = comparison.split(b"and")
        return(ruleComparison(left,formatRules) and ruleComparison(right,formatRules));
    elif(b"or" in comparison):
        left, right = comparison.split(b"or")
        return(ruleComparison(left,formatRules) or ruleComparison(right,formatRules));
    elif(comparison==b"true"):
        return(True);
    elif(b'!=' in comparison):
        left, right = comparison.split(b"!=")
        return(ruleComparison(left,formatRules) != ruleComparison(right,formatRules));
    
    elif(b'==' in comparison):
        left, right = comparison.split(b"==")
        return(ruleComparison(left,formatRules) == ruleComparison(right,formatRules));

    elif(b'<' in comparison):
        left, right = comparison.split(b"<")
        return(ruleComparison(left,formatRules) < ruleComparison(right,formatRules));
    elif(b'>' in comparison):
        left, right = comparison.split(b">")
        return(ruleComparison(left,formatRules) > ruleComparison(right,formatRules));

    elif(b'<=' in comparison):
        left, right = comparison.split(b"<=")
        return(ruleComparison(left,formatRules) <= ruleComparison(right,formatRules));
    
    elif(b'>=' in comparison):
        left, right = comparison.split(b">=")
        return(ruleComparison(left,formatRules) >= ruleComparison(right,formatRules));
    elif(b'|' in comparison):
        left, right = comparison.split(b"|")
        return(ruleComparison(left,formatRules) | ruleComparison(right,formatRules));
    elif(b'&' in comparison):
        left, right = comparison.split(b"&")
        return(ruleComparison(left,formatRules) & ruleComparison(right,formatRules));
    elif(b'>>' in comparison):
        left, right = comparison.split(b">>")
        return(ruleComparison(left,formatRules) >> ruleComparison(right,formatRules));
    elif(b'<<' in comparison):
        left, right = comparison.split(b"<<")
        return(ruleComparison(left,formatRules) << ruleComparison(right,formatRules));
    elif(b'+' in comparison):
        left, right = comparison.split(b"+")
        return(ruleComparison(left,formatRules) + ruleComparison(right,formatRules));
    elif(b'-' in comparison):
        return(ruleComparison(left,formatRules) + ruleComparison(right,formatRules));
    elif(b'*' in comparison and b'**' not in comparison):
        left, right = comparison.split(b"*")
        return(ruleComparison(left,formatRules) + ruleComparison(right,formatRules));
    elif(b'/' in comparison and b'/' not in comparison):
        return(ruleComparison(left,formatRules) / ruleComparison(right,formatRules));
    elif(b'%' in comparison):
        left, right = comparison.split(b"%")
        return(ruleComparison(left,formatRules) / ruleComparison(right,formatRules));
    elif(b'//' in comparison):
        return(ruleComparison(left,formatRules) // ruleComparison(right,formatRules));
    elif(b'**' in comparison):
        return(ruleComparison(left,formatRules) ** ruleComparison(right,formatRules));
    elif(comparison[0]==b"\"" and comparison[-1]==b"\""):
            return(True);
    elif(comparison==b"false"):
        return(False);
    elif(comparison in formatRules):
        return(b"\""+formatRules[comparison]+b"\"")
    elif(canBeInt(comparison)):
        return(int(comparison))
    elif(b"not" in comparison):
        left, right = comparison.split(b"not")
        return(ruleComparison(left + str(not ruleComparison(right,formatRules)).encode(),formatRules));
    return(False)