import requests, json, sys, getopt, os, threading, ast, csv, re
from text2Pdf import *
from collections import OrderedDict

password = ''


def getJsonFromFile(fileName,fileExtension):
    fileName = fileName+fileExtension
    with open(fileName) as json_data:
        r = json.load(json_data)
        return r


def runConsumer(fileName,fileExtension):
    try:
        jsonResponse = getJsonFromFile(fileName,fileExtension)
        # jsonResponse = json.loads(r.content)
        resultList = getResultDataMatchingTemplateFile(jsonResponse)
        fileName = 'Data subject request for information'
        readTemplate(jsonResponse)
        # Integartion from text to pdf
        objText2Pdf = text2Pdf("%s.pdf" % fileName)
        objText2Pdf.fontSize = 8
        objText2Pdf.createStyle()
        objText2Pdf.setFont('Arial')
        objText2Pdf.fontSize = 10
        #add Style
        objText2Pdf.addStyle(stylename = 'Heading', fontstyle=FontStyle.Normal)
        objText2Pdf.addStyle(stylename = 'Heading-Bold', fontstyle=FontStyle.Bold)
        objText2Pdf.addStyle(stylename = 'Heading-Italic', fontstyle=FontStyle.Italic)
        objText2Pdf.addStyle(stylename = 'Heading-Bold-Italic', fontstyle=FontStyle.Bold_Italic)
        
        objText2Pdf.addStyle(stylename = 'Text', fontstyle=FontStyle.Normal)
        objText2Pdf.addStyle(stylename = 'Text-Bold', fontstyle=FontStyle.Bold)
        objText2Pdf.addStyle(stylename = 'Text-Italic', fontstyle=FontStyle.Italic)
        objText2Pdf.addStyle(stylename = 'Text-Bold-Italic', fontstyle=FontStyle.Bold_Italic)
        objText2Pdf.addStyle(stylename = 'Text-rightIndent', fontstyle=FontStyle.Normal, rightindent=160)


        lines = readTemplate(jsonResponse)
        objText2Pdf.addImage("logo.jpg", 54, 54)
        objText2Pdf.addContent(lines[0][1], lines[0][0])
        objText2Pdf.addContent('\n', 'Text')
        objText2Pdf.addContent(lines[1][1], lines[1][0])
        objText2Pdf.addContent('\n', 'Text')

        for key in resultList:
            if len(resultList[key]) > 0:
                objText2Pdf.addContent(key, "Heading-Bold")
                objText2Pdf.addTable(resultList[key].items(),2)
            
        objText2Pdf.addContent('\n', 'Text')
        objText2Pdf.addContent('\n', 'Text')
        objText2Pdf.addContent(lines[2][1], 'Text-rightIndent')

        objText2Pdf.make_pdf_file_with_password(password)

    except Exception, e:
        raise
    else:
        pass
    finally:
        pass


def readTemplate(jsonResponse):
    startPos = 0
    endPos = -1
    lines = tuple(open('Template- Know all request.txt', 'r'))
    lines_dic = []
    for item in lines:
        field_name_dic= {}
        startPos = 0
        while startPos>-1:
            field_name=''
            startPos = item.find('[', startPos)
            endPos = item.find(']', startPos+1)
            if startPos>0 and (endPos > 0 and endPos >= startPos):
                startPos +=1
                field_name = item[startPos: endPos]
                if field_name_dic.has_key(field_name):
                    value = field_name_dic[field_name]
                    field_name_dic[field_name] = value+1
                else:
                    field_name_dic[field_name] = 1
        
            line = 0
        for aField in field_name_dic.keys():
            line+=1
            occeurance = field_name_dic[aField]
            value = ''
            if aField == 'last_name' :
                value = jsonResponse ['PersonalDetails']['last_name']
            if aField == 'first_name' :
                value = jsonResponse ['PersonalDetails']['first_name']
                if value is not None:
                    value = ', ' + value
            if aField == 'home_country_2l' :
                value = jsonResponse ['PersonalDetails']['home_country_2l']
            if aField == 'email_address' :
                value = jsonResponse ['ContactInfo']['Emails']['MainEmail']['email_address']
            if value is None:
                value = ""
            item = item.replace('['+aField+']', value, occeurance)


        style_str = 'Text'
        style_arr = re.split('#B', item)
        if len(style_arr)>1:
            style_str += '-Bold'
            item = style_arr[1]

        style_arr = re.split('#I', item)
        if len(style_arr)>1:
            style_str += '-Italic'
            item = style_arr[1]

        lines_dic.append([style_str, item])

    return lines_dic




def find_values(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try:
            results.append(a_dict[id])
        except KeyError:
            pass
        return a_dict
    # To resolve Return value ignored
    json.loads(json_repr, object_hook=_decode_dict)
    return results


def getResultDataMatchingTemplateFile(jsonResponse):
    sectionDict = OrderedDict()
    finalList = OrderedDict()
    valueString = ''
    displayKey = ''
    displayValue = ''
    isOptional = False
    jsonString = json.dumps(jsonResponse)
    lines = tuple(open('ReadableTemplate.json', 'r'))
    for intindex,item in enumerate(lines,start =1):
        index = 0
        if '#' in item:
            displayValue = item.split(":")[1].strip()
            displayKey = item.split(":")[0].strip()
            if str(displayKey) != '#AccountDetails' and displayKey != '' :
                searchKey = displayKey.split("#")[1].strip()
                try: 
                    partResponse = jsonResponse[searchKey]
                    jsonString = json.dumps(partResponse)
                except:
                    pass

            if (len(item.split(":")) == 3):
                isOptional = True
            else:
                isOptional = False
            sectionDict = OrderedDict()
            continue

        try:
            searchKey = item.split(':')[0].strip()
            searchValue = item.split(':')[1].strip()
        except IndexError:
            print 'Error inside #index'
            pass

        valueResult = find_values(searchKey, jsonString)
        if len(valueResult)== 0 and len(item.split(":")) != 3:
            valueResult = '0'
        for resultIndex,value in enumerate(valueResult,start = 0):
            if value is not None:
                index = index+1
                if isinstance(value, str):
                    valueString = str(value)
                elif isinstance(value, unicode):
                    valueString = value.encode('utf8')
                else:
                    valueString = str(value)

            ##Added regex to get rid of extraneous [] and unicode u if present
            valueString = re.sub(r'[\[\]\']', ' ', valueString)

            ##We need to add an extra piece of code to manipulate the #Communication Channel
            ## This is done in response to the requirement that for communication channel value of channel_refcode 
            ##is the key and value of opt_in_explicit_flag is the corresponding value
            ##Removed the opt_in_explicit_flag key from ReadableTemple.json
            if searchKey == 'channel_refcode':
                listOfChannelOptIn = jsonResponse['MarketingPreferences']['ChannelsOptIn']
                sectionDict[str(valueString)] = str(listOfChannelOptIn[resultIndex]['opt_in_explicit_flag'])

            elif (valueString != ''):
                sectionDict [str(searchValue)+str(index)if len(valueResult)>1 else str(searchValue)] = str(valueString)
            

        if isOptional:
            if len(sectionDict)>0 :
                if len(item.split(":")) == 3:
                    if str(valueString) != '[]':
                        finalList [displayValue] = sectionDict
                else:
                    finalList [displayValue] = sectionDict

        else:
            if len(item.split(":")) == 3:
                if str(valueString) != '[]':
                    finalList[displayValue] = sectionDict
            else:
                finalList[displayValue] = sectionDict
        
        valueString = ''
    return finalList 


def main(argv):
    inputfile = ''
    threadCount = 1
    global password
    try:
        opts, args = getopt.getopt(argv, "i:p:", ["ifile=","pfile="])
    except getopt.GetoptError:
        print '<filename>.py -i <inputfile> -p <password>'
        sys.exit(0)
    if len(opts) < 2:
        print '<filename>.py -i <inputfile> -p <password>'
        exit(1)
    for opt, arg in opts:
        if opt == '-help':
            print '<filename>.py -i <inputfile> -p <password>'
            sys.exit(2)
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            # print 'Input file is ', inputfile
        elif opt in ("-p", "--pfile"):
            password = arg

    if password == '':
        print('There is no password to encrypt the output file. Use the pattern <filename>.py -i <inputfile> -p <password>')
        exit(3)
    if len(inputfile) <= 0:
        print('There is no input file to process. Use the pattern <filename>.py -i <inputfile> -p <password>')
        exit(3)

    print 'Processing started for the file....', inputfile

    fileName, fileExtension = os.path.splitext(inputfile.strip())

    print 'Processing started for the file....'
    runConsumer(fileName,fileExtension)
    

if __name__ == "__main__":
    main(sys.argv[1:])
