# DevCamp 2019 diconium

## Step 1: Send Get Request to the Azure Cloud and get the response text

*If something in this step went wrong for you or if you're unsure where to put something, devCampStep1.py contains the code from the completed step 1 tutorial.*
 *'#-------' lines mark inserted parts*

After creating the script in Step 0 and sending the first Request to the cloud, you can now start getting the actual response.  
Azure's *recognizeText* works in 2 parts. At the beginning you need to post the image to the cloud as done in Step 0.  
From this request you get an URL in the response header. That was the printed part of the script in Step 0.  
This URL is the location, where Azure stores the result of the text recognition after computing is done.  
This result is easily accessible by sending a GET request with your key in the request header.  

To do this, we first import two new modules by adding the following code below the already existing *import requests* line:  

```python
import time, re
```

We need the time module to use a sleep timer and we need the re module to filter all the text in a picture for number plates.
re is the abbreviation for 'regular expressions'.  
Global variables aren't needed in this step, so we can go right to making a new function (add it above the postToCloud function from the previous step):  

```python
def getPlate (url):
    '''Get response of posted image and parses it to access number plate text.
    It uses a regular expression to filter received text for german number plates.

    Argument:
    url -- url to send the Get Request to. Obtained by posting image to Azure Cloud.
    '''
    time.sleep(3) # give Azure time to compute

```

First we want to give Azure a little time to compute. Three seconds usually do the trick.  
Add the next part right below the previous one (*make sure to keep all the indents, as they are needed*):  

```python
    try:
        i = 0
        # get the response of the image recognition
        request2 = requests.get(url, headers=headersURL)
        print ('STATUSTEXT: ')
        print (request2.text)
```

Again we do a request, but this time we only need information and dont need to post anything, so we're going with a GET request.  
We use the same headers as before, because we still need the authorization with our key and the key is part of the header. We also print the response body into the console to see, what's happening.  

In the next part we want to check, if Azure is done computing. Simply add it below the previous code:  

```python
        while(request2.json()['status'] == 'Running' or request2.json()['status'] == 'Not started'):
            print ('STATUSTEXT: ' + request2.text)
            print ("Loop "+str(i))
            i += 1
            try:
                request2 = requests.get(url, headers=headersURL)
            except requests.exceptions.RequestException as e:
                print (e)
            time.sleep(2)
```

This part tests, if the status of the request is 'Running' or 'Not started', because then Azure is not done with computing and we can't move on.
It prints the current status to the console and breaks the loop, if Azure is ready for us to continue.  

After the loop is done, we want to continue with the response.  
Add the following code below your previously added code:  

```python
        # lines is an array that holds all the recognized text
        for line in request2.json()['recognitionResult']['lines']:
            # remove small o's as they are misrecognized circles
            text = re.sub('o', '', line['text'])
            # search for german number plate via regular expression
            match = re.search("[A-ZÖÜÄ]{1,3}[ |-][A-ZÖÜÄ]{1,2}[ |-][0-9]{1,4}[E|H]?", text)
            if (match):
                print('')
                print("Plate: "+ text)
                print('')

            else:
                print('Not a plate: '+text)

```

This part looks through all the recognized text lines. The recognized lines are all stored in the response body as 'lines'.  
We delete all small 'o's, as they are misinterpreted circles (there are no lower case letters in number plates) and match the result against a regular expression to see, if they are in german number plate format.  ********** Continue here ***************


Continue with Step 2:  
[Step 2](https://github.com/volkerhielscher/netnei/blob/master/tutorial/step_2/)

*If something in this step went wrong for you or if you're unsure where to put something, devCampStep1.py contains the code from the completed step 1 tutorial.*
 *'#-------' lines mark inserted parts*