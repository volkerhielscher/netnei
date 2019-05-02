import requests
import logging
import time, re

mode = "URL" # default mode
azureEndpoint = 'https://westeurope.api.cognitive.microsoft.com/vision/v2.0' #FIXME replace with your endpoint
# Azure access point consists your endpoint + the specific service to use
azureURL = azureEndpoint + '/recognizeText?mode=Printed'
# key to Azure Cloud
key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' #FIXME change Xs to your personal Azure resource key.

imageBaseURL = 'https://raw.githubusercontent.com/volkerhielscher/netnei/master/complete/images/'

# Headers for URL call
headersURL = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': key }

def getGermanPlatesFromResult(result):
    '''parse for text in json object and check lines for german number plates and
    returns a list that contains the correct ones.
    '''
    # list to store the regEx results in
    plates = []
    # lines is an array that holds all the recognized text
    for line in result['recognitionResult']['lines']:
        # remove small o's as they are misrecognized circles
        text = line['text']
        # search for german number plate via regular expression
        match = re.search("([A-Za-np-zÖÜÄ0]{1,3})[ |-|o|\.|\,|:]([A-Za-np-zÖÜÄ0]{1,2})[ |-|o|\.|\,|:]([0-9O]{1,4}[E|H]?)", text)
        if (match):
            loggerMain.debug ("Group1:" + str(match.group(1)) + " Group2:" + str(match.group(2)) + " Group3:" + str(match.group(3)))
            match1 = re.sub('0', 'O', str(match.group(1))).upper()
            match2 = re.sub('0', 'O', str(match.group(2))).upper()
            match3 = re.sub('O', '0', str(match.group(3)))
            loggerMain.debug ("Group1:" + match1 + " Group2:" + match2 + " Group3:" + match3)
            text = match1 + " " + match2 + " " + match3
            loggerMain.info("Plate: " + text)
            plates.append(text)
        else:
            loggerMain.info('Not a plate: '+text)
    loggerMain.debug('returned plates: ' + str(plates))
    return plates

def getResult(url):
    '''get result of recognizeTextFromImage() request
    '''
    time.sleep(3) # give Azure time to compute
    try:
        i = 0
        # get the response of the image recognition
        request2 = requests.get(url, headers=headersURL)
        loggerMain.debug ('STATUSTEXT: ' + request2.text)
        # test, if Azure needs more computing time. Break the loop after 10 tries
        while((request2.json()['status'] == 'Running' or request2.json()['status'] == 'Not started') and i <= 9):
            time.sleep(2)
            loggerMain.debug ('STATUSTEXT in loop: ' + request2.text)
            loggerMain.debug ("Loop iteration :"+str(i))
            i += 1
            try:
                request2 = requests.get(url, headers=headersURL)
            except requests.exceptions.RequestException as e:
                loggerMain.exception ('RequestException in while loop: ' + e)
            # log unusual behaviour
            if i == 5:
                loggerMain.warn('Azure computing needs longer than usual.')
            if i == 9:
                loggerMain.error('Break loop after trying to get result for 20 seconds' )
        result = request2.json()
        return result
    except requests.exceptions.RequestException as e:
                loggerMain.critical ('RequestException: ')
                loggerMain.exception (e)
                return
    except Exception as e:
        loggerMain.critical ('Miscellaneous exception: ')
        loggerMain.exception (e)
        return

def recognizeTextFromImage(mode, file):
    '''Post image to Azure cloud and calls getPlate() to get response text.

    Arguments:
    mode -- specifies in which mode the post request is done ('local', 'URL')
    file -- specifies which file to post (*.jpg, *.jpeg, *.bmp, *.png)

    Parameters:
    data -- file in binary, used for local access
    jsonData -- requestbody in json format ({"url": "imageURL"})
    request -- request object of post request. Used to access its headers (request.headers)
    '''
    try:
        if mode == 'local':
            # complete this in a later step
            print () # only for now
        elif mode == 'URL':
            # use images from the github remote repository
            jsonData = {"url": imageBaseURL + file}
            request = requests.post(azureURL, headers=headersURL, json=jsonData, timeout=10)
        else:
            loggerMain.error ('recognizeTextFromImage() was called with wrong mode')
            return
    except requests.exceptions.RequestException as e:
        loggerMain.critical ('Can\'t access Azure services')
        loggerMain.exception (e)
    except Exception as e:
        loggerMain.critical ('undefinded problem in recognizeTextFromImage')
        loggerMain.exception (e)
    try:
        response = request.headers['Operation-Location']
        loggerMain.debug (response)
        result = getResult (response)
        return result
        
    except Exception as e:
        loggerMain.error ('Exception:')
        loggerMain.error (request.text)
        loggerMain.exception (e)

# enable logging
loggerRequests = logging.getLogger('requests')
loggerMain = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(name)s:\t %(message)s')

result = recognizeTextFromImage(mode, 'bild1.jpg')
if result:
    plates = getGermanPlatesFromResult(result)
