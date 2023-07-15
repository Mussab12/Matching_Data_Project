import re
from datetime import datetime
# Possible Data Type Pattern
patternInteger = re.compile(r'([-+]\s*)?\d+[lL]?$')
patternBoolean = re.compile(r'True$|^False$|^true$|^TRUE$|^false$|^FALSE$')
patternDouble1 = re.compile(r'([-+]\s*)?[1-9][0-9]*\.?[0-9]*([Ee][+-]?[0-9]+)?$')
patternDouble2 = re.compile(r'([-+]\s*)?[0-9]*\.?[0-9][0-9]*([Ee][+-]?[0-9]+)?$')

possibleFMTs = ('%Y', '%b %d, %Y', '%B %d %Y', '%m/%d/%Y', '%m/%d/%y', '%b %Y', '%B%Y', '%b %d,%Y',
                '%b %d, %Y %H:%M:%S','%B %d %Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%b %Y %H:%M:%S', '%B%Y %H:%M:%S', '%b %d,%Y %H:%M:%S',
                "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%y-%m-%d", "%y-%m-%d %H:%M:%S", "%y/%m/%d", "%y/%m/%d %H:%M:%S", "%Y/%m/%d", "%Y/%m/%d %H:%M:%S")

# check if the data is valid or not
def checkifDataType(type, data):
    result = False
    if type == "int":
        if patternInteger.match(data):
            result = True
    elif type == "double":
        if patternDouble1.match(data) or patternDouble2.match(data):
            result = True
    elif type == "string":
        result = True
    elif type == "date":
        if checkDateType(data) != "None":
            result = True
    return result

# check if the type is date
def checkDateType(data):
    date_format = "None"
    for fmt in possibleFMTs:
        try:
            t = datetime.strptime(data, fmt)
            date_format = fmt
            break
        except ValueError as err:
            pass
        except TypeError as terr:
            pass
    return date_format

zipCodePattern = re.compile(r'^((\d{5}((|-)-\d{4})?)|([A-Za-z]\d[A-Za-z][\s\.\-]?(|-)\d[A-Za-z]\d)|[A-Za-z]{1,2}\d{1,2}[A-Za-z]? \d[A-Za-z]{2})$')
def checkZipCode(data):
    if zipCodePattern.match(data):
        return True
    return False
