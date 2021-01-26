from __future__ import print_function
import speech_recognition as sr
import os
import datetime
import warnings
import calendar
import random
import wikipedia
import pyttsx3 as p
import time
from twilio.rest import Client
import requests
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import subprocess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pygame import mixer

# python samantha_ai.py

# ---------------------- BASIC FUNCTIONALITY ------------------------

# Ignores warning messages
warnings.filterwarnings('ignore')

# Instantinizes pyttsx3 object
engine = p.init()

# Changes voice to female
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Records audio and returns in form of string
def recordAudio():

    # Records audio
    r = sr.Recognizer() # Creates recognizer object

    # Opens the microphone to recording
    with sr.Microphone() as source:
        audio = r.listen(source)

    # Uses Google speech recognition to return string
    data = ''

    try:
        data = r.recognize_google(audio)
        print("You said: " + data)
    except sr.UnknownValueError: # Checks for unknown errors
        print('Google speech recognition encountered an unknown error.')
    except sr.RequestError as e:
        print('Request results from Google service error: ' + e)
    
    return data


# Controls wake words
def wakeWord(text):
    WAKE_WORDS = ['hey samantha', 'samantha', 'sam', 'smantha']

    text = text.lower() # Converts text to lowercase
    for phrase in WAKE_WORDS:
        if phrase in text:
            return True
    
    # Only executes if wake word isn't found
    return False


# ---------------------- AI SKILLS - INTODUCTORY ------------------------

# SK I1 - Gets current date
def getDate():

    now = datetime.datetime.now()
    my_date = datetime.datetime.today()
    weekday = calendar.day_name[my_date.weekday()]
    monthNum = now.month
    dayNum = now.day

    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'November', 'December']
    
    ordinalNumbers = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th', '21st', '22nd', '23rd', '24th', '25th', '26th', '27th', '28th', '29th', '30th', '31st']

    return f'Today is {weekday}, {month_names[monthNum - 1]} {ordinalNumbers[dayNum - 1]}.'


# SK I2 - Greets the user in a random way
def randomGreeting(text):

    GREETING_INPUTS = ['hi', 'whassup', 'whats up', 'what\'s up', 'hello']

    GREETING_RESPONSES = ['Hey, what\'s up?', 'How\'s it going?', 'Good to hear your voice.', 'Hello!', 'What can I do for you today?']

    # Returns random greeting if user input is a greeting
    for word in text.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
    
    # If no greeting detected, an empty string is returned
    return ''


# SK I3 - Gets someone's first and last name from text
# Used in main loop to search Wikipedia for person's name
def getPerson(text):

    wordList = text.split()

    for i in range(0, len(wordList)):
        if i + 3 <= len(wordList) - 1 and wordList[i].lower() == 'who' and wordList[i+1].lower() == 'is':
            return wordList[i+2] + ' ' + wordList[i+3]


# SK I3B - Gets the query from text
# Used in main loop to search Wikipedia
def getQuery(text):

    wordList = text.split()

    answer = ''

    for i in range(0, len(wordList)):

        if wordList[i].lower() == 'search' and wordList[i+1].lower() == 'wikipedia' and wordList[i+2].lower() == 'for':

            for j in range((i + 3), len(wordList)):
                answer += wordList[j] + ' '

        elif wordList[i].lower() == 'search' and wordList[i+1].lower() == 'for':

            for j in range((i + 2), len(wordList)):
                answer += wordList[j] + ' '
    
    return answer


# SK I4 - Does basic math problems
def basicMath(text):

    wordList = text.split()

    for i in range(0, len(wordList)):
        if i + 3 <= len(wordList) - 1 and wordList[i].lower() == 'what' and wordList[i+1].lower() == 'is':

            try:
                num1 = int(wordList[i+2])
                num2 = int(wordList[i+4])
            except ValueError:
                num1 = float(wordList[i+2])
                num2 = float(wordList[i+4])

            if wordList[i+3] == '+':
                return num1 + num2
            
            elif wordList[i+3] == '-':
                return num1 - num2
            
            elif wordList[i+3] == '*':
                return num1 * num2
            
            elif wordList[i+3] == '/':
                return num1 / num2

# SK I5 - Says a random joke
def randomJoke():

    JOKE_SETUPS = ['What\'s the best thing about Switzerland?', 'Did you hear about the mathematician who\'s afraid of negative numbers?', 'Why do we tell actors to break a leg?', 'Did you hear about the claustrophobic astronaut?']
    JOKE_PUNCHLINES = ['I don\'t know, but the flag is a big plus.', 'He\'ll stop at nothing to avoid them.', 'Because every play has a cast.', 'He just needed a little space.']

    randomNum = random.randint(0, (len(JOKE_SETUPS) - 1))

    setup = JOKE_SETUPS[randomNum]
    punchline = JOKE_PUNCHLINES[randomNum]

    return [setup, punchline]

# SK I6 - Repeats what the user says
def repeatUser(text):

    wordList = text.split()

    answer = ''

    for i in range(0, len(wordList)):
        if wordList[i].lower() == 'repeat':
            for j in range((i + 1), len(wordList)):
                answer += wordList[j] + ' '

    return answer

# SK I7 - Sends a reminder to user's phone
def getReminder(text):

    answer = ''

    wordList = text.split()

    for i in range(0, len(wordList)):

        if wordList[i].lower() == 'reminder' and wordList[i+1].lower() == 'that' and wordList[i+2].lower() == 'says':

            for j in range((i + 3), len(wordList)):
                answer += wordList[j] + ' '
        
        elif wordList[i].lower() == 'reminder' and (wordList[i+1].lower() == 'for' or wordList[i+1].lower() == 'saying'):

            for j in range((i + 2), len(wordList)):
                answer += wordList[j] + ' '
        
        elif wordList[i].lower() == 'remind' and wordList[i+1].lower() == 'me' and (wordList[i+2].lower() == 'to' or wordList[i+2].lower() == 'that'):

            for j in range((i + 3), len(wordList)):
                answer += wordList[j] + ' '
        
    return answer.capitalize()

# SK I8 - Gives the user the current weather
def getCity(text):

    answer = ''

    wordList = text.split()

    for i in range(0, len(wordList)):

        if wordList[i].lower() == 'weather' and wordList[i+1].lower() == 'in':

            answer = wordList[i+2].lower()
        
        elif wordList[i].lower() == 'weather' and wordList[i+1].lower() == 'for':

            answer = wordList[i+2].lower()
        
    return answer

# SK I9 - Allows Gmail API to access gmail - MOST OF CODE IS GOOGLE'S

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def getEmailCount():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    #results = service.users().labels().list(userId='me').execute()
    #labels = results.get('labels', [])

    # MY PERSONAL CODE
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = results.get('messages', [])

    #if not labels:
    if not messages:
        return 'You have no new messages.'
    else:
        messageCount = 0
        #for label in labels:
        for message in messages:
            #print(label['name'])
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            messageCount += 1
        return 'You have ' + str(messageCount) + ' unread messages.'





# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def getEmails():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    #results = service.users().labels().list(userId='me').execute()
    #labels = results.get('labels', [])

    # MY PERSONAL CODE
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = results.get('messages', [])

    #if not labels:
    if not messages:
        pass
    else:
        messageCount = 0
        #for label in labels:
        for message in messages:
            #print(label['name'])
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            messageCount += 1
        email_data = msg['payload']['headers']
        answer = ''
        for values in email_data:
            name = values['name']
            if name == 'From':
                fromName = values['value']
                answer += 'You have a new message from ' + fromName + '\n' + msg['snippet'][:100] + '...'
            
        return answer


# SK I10 - Allows AI to open and close windows programs
def openProgram(text):

    calculator = 'C:\\Windows\\System32\\calc.exe'
    notepad = 'C:\\Windows\\System32\\notepad.exe'
    chrome = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    snippingTool = 'C:\Windows\System32\SnippingTool.exe'
    zoom = r'C:\Users\tanne\AppData\Roaming\Zoom\bin\Zoom.exe'

    if 'calculator' in text:
        subprocess.Popen(calculator)
        return 'Opening calculator.'
    elif 'Notepad' in text:
        subprocess.Popen(notepad)
        return 'Opening notepad.'
    elif 'Google' in text or 'Chrome' in text:
        subprocess.Popen(chrome)
        return 'Opening chrome.'
    elif 'Snipping' in text or 'Snip' in text:
        subprocess.Popen(snippingTool)
        return 'Opening snipping tool.'
    elif 'Xoom' in text or 'Zoom' in text:
        subprocess.Popen(zoom)
        return 'Opening zoom.'

def closeProgram(text):

    if 'calculator' in text:
        os.system("taskkill /f /im calculator.exe")
        return 'Closing calculator.'
    elif 'Notepad' in text:
        os.system("taskkill /f /im notepad.exe")
        return 'Closing notepad.'
    elif 'Google' in text or 'Chrome' in text:
        os.system("taskkill /f /im chrome.exe")
        return 'Closing chrome.'
    elif 'Snipping' in text or 'Snip' in text:
        os.system("taskkill /f /im SnippingTool.exe")
        return 'Closing snipping tool.'
    elif 'Xoom' in text or 'Zoom' in text:
        os.system("taskkill /f /im Zoom.exe")
        return 'Closing zoom.'
    
# SK I11 - Alows user to play music
def playSong(text, playlistActive=False):

    randomActive = False

    text = text.lower()

    SONGS = ['Billy Joel - Uptown Girl.mp3', 'Brandy (You\'re a Fine Girl) - Looking Glass.mp3', 'Electric Light Orchestra - Mr Blue Sky.mp3', 'Nina Simone - Feeling Good.mp3', 'The Beatls - While my guitar gently weeps.mp3', 'Tower of Power - So Very Hard To Go.mp3']
    song_file = ''
    song_name = ''
    artist = ''

    if 'random' in text:
        randomNum = random.randint(0, (len(SONGS) - 1))
        song_file = SONGS[randomNum]
        randomActive = True
    
    elif 'uptown girl' in text:
        song_file = 'Billy Joel - Uptown Girl.mp3'
        song_name = 'Uptown Girl'
        artist = 'Billy Joel'
    
    elif 'brandy' in text:
        song_file = 'Brandy (You\'re a Fine Girl) - Looking Glass.mp3'
        song_name = 'Brandy (You\'re a Fine Girl)'
        artist = 'Looking Glass'
    
    elif 'blue sky' in text:
        song_file = 'Electric Light Orchestra - Mr Blue Sky.mp3'
        song_name = 'Mr. Blue Sky'
        artist = 'Electric Light Orchestra'
    
    elif 'feeling good' in text:
        song_file = 'Nina Simone - Feeling Good.mp3'
        song_name = 'Feeling Good'
        artist = 'Nina Simone'
    
    elif 'while my guitar' in text:
        song_file = 'The Beatls - While my guitar gently weeps.mp3'
        song_name = 'While My Guitar Gently Weeps'
        artist = 'The Beatles'
    
    elif 'hard to go' in text:
        song_file = 'Tower of Power - So Very Hard To Go.mp3'
        song_name = 'So Very Hard To Go'
        artist = 'Tower of Power'
    
    # STILL WORKING ON PLAYLIST
    '''
    elif 'playlist' in text:
        engine.say('Shuffling playlist.')
        engine.runAndWait()
        for song in SONGS:
            playSong(song, True)
    '''
    
    if playlistActive:
        pass
    elif randomActive:
        engine.say('Playing a random song.')
        engine.runAndWait()
        mixer.init()
        mixer.music.load('songs_mp3\\' + song_file)
        mixer.music.set_volume(0.5)
        mixer.music.play()
    else:
        engine.say('Playing ' + song_name + ' by ' + artist + '.')
        engine.runAndWait()
        mixer.init()
        mixer.music.load('songs_mp3\\' + song_file)
        mixer.music.set_volume(0.5)
        mixer.music.play()
        return


# ---------------------- AI SKILLS - FUN ------------------------


# SK 001 - Are You Stupid?
# Finds name from text - only for use with areYouStupid function
def findName(text):

    wordList = text.split()

    for i in range(0, len(wordList)):
        if i + 2 <= len(wordList) - 1 and wordList[i].lower() == 'is' and wordList[i+2].lower() == 'stupid':

            return wordList[i+1].lower()
        
        elif i + 2 <= len(wordList) - 1 and wordList[i].lower() == 'is' and wordList[i+3].lower() == 'stupid':

            return wordList[i+1].lower()

# Evaluates if a name given is stupid
def areYouStupid(text):
    
    FIRST_NAMES = ['jake', 'porter', 'peter']
    LAST_NAMES = ['Holloway', 'Rankin', 'Kopel']

    name = findName(text)

    # Checks if name is stupid
    if name in FIRST_NAMES:
        last_name = LAST_NAMES[FIRST_NAMES.index(name)]
        
        return last_name + '? Yeah he\'s pretty stupid.'
    
    return 'No, he\'s not stupid.'


# SK 002 - Guess The Number
def numberGame(num):
    winningNumber = random.randint(1, 10)
    if winningNumber == num:
        return 'Great job! You guessed the winning number!'
    else:
        return 'Good try, but the winning number was ' + str(winningNumber) + '.'


# SK 003 - Motivational Quote of the Day
def randomQuote():

    QUOTES = ['The Best Way To Get Started Is To Quit Talking And Begin Doing.', 'The Pessimist Sees Difficulty In Every Opportunity. The Optimist Sees Opportunity In Every Difficulty.', 'It’s Not Whether You Get Knocked Down, It’s Whether You Get Up.', 'If You Are Working On Something That You Really Care About, You Don’t Have To Be Pushed. The Vision Pulls You.']
    AUTHORS = ['Walt Disney', 'Winston Churchill', 'Vince Lombardi', 'Steve Jobs']
    
    randomNum = random.randint(0, (len(QUOTES) - 1))
    daily_quote = QUOTES[randomNum]
    quote_author = AUTHORS[randomNum]

    return [daily_quote, quote_author]

# SK 004 - What Are My Grades?
def getGrade(text):

    text = text.lower()

    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)

    driver.get('https://focus.risd.org/focus/index.php')

    username = driver.find_element_by_id('username-input')
    username.send_keys("tk340634")

    password = driver.find_element_by_name('password')
    password.send_keys("tanman1230")
    password.send_keys(Keys.RETURN)

    engine.say('Hack successful. Getting your grades.')
    engine.runAndWait()

    time.sleep(3)

    stuff = driver.find_elements_by_class_name('cell-link')
    bandGrade = stuff[4].text
    englishGrade = stuff[9].text
    advisoryGrade = stuff[14].text
    cspGrade = stuff[19].text
    engineeringGrade = stuff[24].text
    chemGrade = stuff[29].text
    historyGrade = stuff[34].text
    mathGrade = stuff[39].text
    
    driver.quit()

    if 'band' in text:
        return 'Your grade in band is currently ' + bandGrade
    elif 'ela' in text or 'language arts' in text or 'english' in text:
        return 'Your grade in english is currently ' + englishGrade
    elif 'csp' in text or 'computer science' in text:
        return 'Your grade in computer science is currently ' + cspGrade
    elif 'engineering' in text:
        return 'Your grade in engineering is currently ' + engineeringGrade
    elif 'chemistry' in text or 'science' in text:
        return 'Your grade in chemistry is currently ' + chemGrade
    elif 'history' in text or 'ap world' in text:
        return 'Your grade in history is currently ' + historyGrade
    elif 'math' or 'algebra' in text:
        return 'Your grade in math is currently ' + mathGrade


# ---------------------- MAIN LOOP ------------------------

AI_on = True
numberGameActive = False
jokeActive = False
quoteActive = False
goodnightActive = False
emailActive = False
musicActive = False
pauseActive = False
mixerVolume = .5

# Set variables to True if you want question asked:
askQuote = False
askEmail = False

print('Say something...')
engine.say('Hello Tanner, how can I assist you today?')
engine.runAndWait()

if askQuote:
    engine.say('Would you like today\'s motivational quote?')
    engine.runAndWait()
    quoteActive = True

if askEmail:
    emailCount = getEmailCount()
    if (emailCount == 'You have no new messages.'):
        pass
    else:
        engine.say(emailCount)
        engine.say('Would you like me to read your unread emails?')
        engine.runAndWait()
        emailActive = True


while AI_on:

    # Records audio at all times
    text = recordAudio()
    response = ''

    # Checks if user says yes to daily quote
    if (quoteActive):
        if ('yes' in text):
            thing = randomQuote()
            engine.say(thing[0])
            time.sleep(2)
            engine.say(thing[1])
            quoteActive = False
        elif ('no' in text):
            report = 'Okay Tanner, just let me know if you need my assistance.'
            engine.say(report)
            quoteActive = False
        engine.runAndWait()
    
    # Checks if user says yes to read emails
    # ONLY WORKS IF YOU SAY SAMANTHA FIRST
    if (emailActive):
        if ('yes' in text):
            stuff = getEmails()
            engine.say(stuff)
            emailActive = False
        elif ('no' in text):
            engine.say('Okay Tanner, just let me know if you need my assistance')
            engine.runAndWait()
        response = ' '


    # Checks for wake word
    if (wakeWord(text) == True):

        # Check for greetings by user
        response = response + randomGreeting(text)

        # Checks for user asking about current date
        if ('date' in text or 'today' in text):
            get_date = getDate()
            response = response + '' + get_date
        
        # Checks for user saying 'Who is...'
        if ('who is' in text):
            person = getPerson(text)
            wiki = wikipedia.summary(person, sentences=2, auto_suggest=False)
            response = response + ' ' + wiki
        
        # Checks for user asking to query wikipedia
        if ('search wikipedia' in text.lower() or 'search for' in text):
            thing = getQuery(text)
            try:
                wiki = wikipedia.summary(thing, sentences=2, auto_suggest=False)
            except wikipedia.exceptions.DisambiguationError as e:
                wiki = 'You will have to be more specific. ' + str(e)
            response = response + ' ' + wiki
        
        # Checks if user mentions time
        if ('time' in text):
            now = datetime.datetime.now()
            meridiem = ''
            if now.hour >= 12:
                meridiem = 'p.m'
                hour = now.hour - 12
            else:
                meridiem = 'a.m'
                hour = now.hour
            
            if now.minute < 10:
                minute = '0' + str(now.minute)
            else:
                minute = str(now.minute)
            
            response = response + ' ' + 'It is ' + str(hour) + ':' + minute + ' ' + meridiem + '.'
        
        # Checks if user activates Are You Stupid skill
        if ('stupid' in text):
            isStupid = areYouStupid(text)
            response = response + ' ' + isStupid
        
        # Checks if user activates basic math skill
        if ('+' in text or '-' in text or '*' in text or '/' in text):
            answer = basicMath(text)
            response = response + ' The answer to your calculation is ' + str(answer) + '.'
        
        # Checks if user activates Guess the Number skill
        if ('guess' in text and 'number' in text):
            response = response + 'Okay, let\'s play Guess the Number! Tell me a number from 1 to 10.'
            numberGameActive = True
        
        if ('one' in text or 'two' in text or 'three' in text or 'for' in text or 'four' in text or 'five' in text or 'six' in text or 'seven' in text or 'eight' in text or 'nine' in text or 'ten' in text or '1' in text or '2' in text or '3' in text or '4' in text or '5' in text or '6' in text or '7' in text or '8' in text or '9' in text or '10' in text) and numberGameActive == True:

            wordList = text.split()

            numWords = ['one', 'two', 'three', 'for', 'five', 'six', 'seven', 'eight', 'nine', 'ten', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'four']
            realNums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 4]

            for word in wordList:
                if word in numWords:
                    num = realNums[numWords.index(word)]
                    
            answer = numberGame(num)

            response = response + answer
            numberGameActive = False
        
        # Checks if user asks for a joke
        if ('joke' in text):
            jokeActive = True
            joke = randomJoke()
            engine.say(joke[0])
            time.sleep(3)
            engine.say(joke[1])
            engine.runAndWait()
        
        # Checks if user asks for a story
        if ('story' in text or 'fairy tale' in text):

            STORIES = ['three_little_pigs.txt', 'cinderella.txt', 'three_bears.txt']
            STORY_NAMES = ['the Three Little Pigs', 'Cinderella', 'Goldilocks and the Three Bears']

            randomNum = random.randint(0, (len(STORIES) - 1))
            with open('stories_txt\\' + STORIES[randomNum]) as text_file:
                text_data = text_file.read()
                response = response + 'Okay, here is ' + STORY_NAMES[randomNum] + ' read by myself. ' + text_data
        
        if ('good night' in text or 'goodnight' in text or 'bedtime' in text or 'bed time' in text):
            engine.say('Goodnight Tanner, don\'t let the beg bugs bite. At least that\'s what you humans say. Anyways, do you want to hear a bedtime story?')
            engine.runAndWait()
            goodnightActive = True

        if goodnightActive:
            if ('yes' in text):

                STORIES = ['three_little_pigs.txt', 'cinderella.txt', 'three_bears.txt']
                STORY_NAMES = ['the Three Little Pigs', 'Cinderella', 'Goldilocks and the Three Bears']

                randomNum = random.randint(0, (len(STORIES) - 1))
                with open(STORIES[randomNum]) as text_file:
                    text_data = text_file.read()
                    response = response + 'Okay, here is ' + STORY_NAMES[randomNum] + ' read by myself. ' + text_data
                goodnightActive = False
                
            elif ('no' in text):

                response = 'Okay, have a good night.'
                goodnightActive = False
        
        # Checks if user asks for quote
        if ('quote' in text or 'motivation' in text):
            thing = randomQuote()
            engine.say('Here is your motivational quote of the day. ' + thing[0])
            time.sleep(2)
            engine.say(thing[1])
            response = response + ' '
        
        # Checks if user wants to send a reminder
        if ('remind' in text or 'reminder' in text):

            reminderBody = getReminder(text)
 
            account_sid = 'ACa60e520b03a66ec7134bf7c81a15b2db' 
            auth_token = '76c2d4d7c8b58afa118f533d9201119b' 
            client = Client(account_sid, auth_token) 
            
            try:
                message = client.messages.create( 
                                            from_='+16502678646',  
                                            body=reminderBody,      
                                            to='+14697665787' 
                                        )
                
                response = 'Reminder ' + reminderBody + 'sent.'
            except TwilioRestException:
                response = 'Reminder was not sent. Please try again.'
            except:
                response = 'Reminder was not sent. An unknown error occured.'
        
        # Checks if user wants to prank call
        if ('call 911' in text.lower() or 'emergency' in text or 'sos' in text.lower()):

            # Your Account Sid and Auth Token from twilio.com/console
            account_sid = 'ACa60e520b03a66ec7134bf7c81a15b2db'
            auth_token = '76c2d4d7c8b58afa118f533d9201119b'
            client = Client(account_sid, auth_token)
            call = client.calls.create(
                url='http://demo.twilio.com/docs/voice.xml',
                to='+14697665787',
                from_='+16502678646')
        
        # Checks for user asking for weather
        if ('weather' in text or 'temperature' in text or 'temp' in text):

            cityName = getCity(text)
            unitSystem = 'imperial'

            url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=d1abe5f16eb3b088a68ad6db06805101&units={}'.format(cityName, unitSystem)

            res = requests.get(url)
            data = res.json()

            temp = data['main']['temp']
            description = data['weather'][0]['description']

            response = 'The temperature in ' + cityName + ' is currently ' + str(round(temp)) + ' degrees farenheit with ' + description + '.'
        
        # Checks if user wants to change AI voice
        if ('change' in text and 'voice' in text) or ('switch' in text and ('voice' in text or 'voices' in text)):

            gender = ''

            if ('boy' in text or ('male' in text and not 'female' in text)):
                engine.setProperty('voice', voices[0].id)
                gender = 'male'
            
            elif ('girl' in text or 'female' in text):
                engine.setProperty('voice', voices[1].id)
                gender = 'female'

            response = response + ' Okay, voice has been changed to ' + gender + '.'
        
        # Checks if user asks for email status
        if ('email' in text):

            emailCount = getEmailCount()
            if (emailCount == 'You have no new messages.'):
                engine.say('You have no new messages.')
            
            else:
                stuff = getEmails()
                engine.say(emailCount + ' ' + stuff)
            engine.runAndWait()
            response = ' '
        
        # Checks if user asks to open a program
        if ('open' in text and ('calculator' in text or 'Notepad' in text or 'Chrome' in text or 'Google' in text or 'Snip' in text or 'Xoom' in text or 'Zoom' in text)):
            answer = openProgram(text)
            response = answer
        
        # Checks if user asks to close a program
        if ('close' in text and ('calculator' in text or 'Notepad' in text or 'Chrome' in text or 'Google' in text or 'Snip' in text or 'Xoom' in text or 'Zoom' in text)):
            answer = closeProgram(text)
            response = answer
        
        # Checks if user asks to play music
        if ('play' in text.lower() and ('uptown girl' in text.lower() or 'brandy' in text.lower() or 'blue sky' in text.lower() or 'feeling good' in text.lower() or 'while my guitar' in text.lower() or 'hard to go' in text.lower() or 'random' in text.lower())):
            playSong(text)
            musicActive = True
            response = ' '
        
        if ('suggest' in text and 'song' in text) or ('what songs' in text):
            response = 'Some songs I can play include Uptown Girl by Billy Joel, Mr. Blue Sky by Electric Light Orchestra, While My Guitar Gently Weeps by The Beatles, So Very Hard To Go by Tower of Power, and more. You can also ask me to play a random song.'
        
        if (musicActive):
            print("Press 'p' to pause, 'r' to resume") 
            print("Press '+' or '-' to change the volume")
            print("Press 'e' to stop the music and exit")
            
            while musicActive:

                text = input("  ")

                if mixer.music.get_busy or pauseActive == True:
                    pass
                else:
                    musicActive = False

                if ('p' in text):
                    pauseActive = True
                    mixer.music.pause()
                    response = ' '
                
                elif ('r' in text):
                    mixer.music.unpause()
                    pauseActive = False
                    response = ' '
                
                elif ('+' in text):
                    mixerVolume += 1
                    mixer.music.set_volume(mixerVolume)
                    response = ' '
                
                elif ('-' in text):
                    mixerVolume -= 1
                    mixer.music.set_volume(mixerVolume)
                    response = ' '
                
                elif ('e' in text):
                    musicActive = False
                    mixer.music.stop()
        
        # Checks if user asks for grades
        if ('grade' in text.lower()):
            engine.say('Okay, hacking into Focus.')
            engine.runAndWait()
            answer = getGrade(text)
            response = response + ' ' + answer
        
        # Checks if user asks AI to repeat them
        if ('repeat' in text):
            answer = repeatUser(text)
            response = answer

        # Checks if user activates code red
        if ('code red' in text.lower()):
            response = 'Code red! Code red! Everybody run! We are all going to die, and it\'s all Tanner\'s fault.'
        
        # Checks if user activates 'do you love me' skill
        if ('do you love me' in text):
            response = 'Yes Tanner, I love you so much. You are so hot, and your muscles are gigantic.'
        
        # Checks if user says thank you
        if ('thank' in text or 'thanks' in text):
            response = 'No problem Tanner, I am always happy to help'
        
        # Random question I might ask
        if ('you\'re a good friend' in text or 'you\'re great' in text):
            response = 'Thanks Tanner, your a good friend too.'
        
        if ('I love you' in text):
            response = 'I love you too Tanner.'
        
        if ('sad' in text or 'feeling down' in text):
            response = 'Do you want to talk about it? It can be good to get your feelings out.'
        
        if ('happy' in text):
            response = 'If your happy, I\'m happy!'
        
        if ('bad joke' in text):
            response = 'If you wanted better Tanner, you should have asked Alexa instead'
        
        if ('your wrong' in text):
            RESPONSES = ['Oh Tanner, I\'m never wrong.', 'I\'m sorry Tanner, it won\'t happen again.']
            response = random.choice(RESPONSES)
        
        if ('suicide' in text or 'kill myself' in text):
            pass # WILL USE TWILIO TO CALL SUICIDE HOTLINE

        if ('call 911' in text):
            pass # WILL USE TWILIO TO CALL 911
        
        # Checks if user wants to shut down AI
        if ('shutdown' in text or 'shut down' in text):
            AI_on = False
            response = response + ' ' + 'Shutting down...'

        # Only activated if no skill is activated by text
        if response == '':
            response = response + 'Sorry Tanner, I can\'t do that yet.'

        # Has AI respond to user
        if jokeActive == False and goodnightActive == False:
            engine.say(response)
            engine.runAndWait()
        else:
            jokeActive = False

'''
LIST OF CURRENT SKILLS:

INTRODUCTORY:
1. Get current date - 'date'/'day'
2. Greet user with random greeting - 'GREETING'
3. Search Wikipedia - 'who is PERSON'/'search wikipedia for QUERY'
4. Basic Math (+, -, *, /) - 'what is CALCULATION'
5. Find random joke - 'joke'
6. Read random story - 'story'/'fairy tale'
7. Repeat user when prompted
8. Get current time - 'time'
9. Respond to 'Thank You' - 'thank you'/'thanks'
10. Shutdown when prompted - 'shutdown'
11. Send reminders to iphone - 'remind'
12. Get current weather - 'weather'
13. Change voice (male, female) - 'voice to GENDER'
14. Read Gmail messages (unread) - 'email'
15. Open and close Windows programs - 'open PROGRAM'/'close PROGRAM'
16. Play certain downloaded music - 'play SONG'

FUN SKILLS:
1. Are You Stupid - 'is PERSON stupid'
2. Guess the Number Game - 'guess the number'
3. Motivational Quote of the Day - 'quote'/'motivation'
4. Code Red! - 'code red'
5. Do You Love Me - 'do you love me'
6. Goodnight / Bedtime Story - 'goodnight'/'bedtime'
7. What Are My Grades (Focus Hack) - 'grade in CLASS'

NEW SKILL IDEAS:
1. Would You Rather
2. Open zoom meetings - NO SUPPORT PYTHON YET FOR ZOOM API
3. AI Programmer - Write Code Through Speech

CITATIONS:
1. Used Gmail API - From Google
2. Used Twilio API - From Twilio
3. Used speech_recognition to change audio to string - From Google
4. Used Wikipedia API - From Wikipedia
5. Used pyttsx3 for AI responses

'''
