import pyttsx3
from dotenv import load_dotenv
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
from selenium import webdriver
import time
import os,sys,subprocess
import smtplib
from selenium.webdriver.common.keys import Keys
import pyautogui
from googletrans import Translator
import tkinter as tk
from PIL import ImageTk, Image
import mysql.connector
import nltk
from nltk.corpus import stopwords
import requests
from bs4 import BeautifulSoup

load_dotenv()

translator = Translator()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishhMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")
    elif hour>=12 and hour<18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")

    speak("How are you? How may I help you")

def naturalLanguageProcessing(query):
    global updated_query
    token = nltk.tokenize.word_tokenize(query)
    updated_query = []
    stop_words = set(stopwords.words("english"))
    for word in token:
        if word not in stop_words and word not in "want" and word not in "please":
            updated_query.append(word)
    space = " "
    updated_query = space.join(updated_query)
    return updated_query

def takeCommand():
    global label_text
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(query)

    except:
        print("Say that again please...")
        speak("Say that again please...")
        return "None"
    return query

def sendEmail(to,content):
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(os.getenv('GMAIL_ID'), os.getenv('GMAIL_PASSWORD'))
    print("success4")
    speak("do you want to send the email")
    confirm = takeCommand().lower()
    if "yes" in confirm:
        server.sendmail(os.getenv('GMAIL_ID'), to, content)
        server.close()
    else:
        speak("email not sent")

def main():
    wishhMe()
    if 1:
        query = takeCommand().lower()
        keywords = ['wikipedia', 'google', 'youtube', 'website', 'song', 'time', 'app', 'email', 
        'news', 'weather', 'what', 'timer', 'direction', 'joke', 'notes', 'date', 'translate', 'none','calculator','movie','order']
        queryList = query.split(" ")

        for i in keywords:
            if (i in queryList):
                category = i

        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="voiceTranslator"
        )
        mycursor = mydb.cursor()
        val = (query,)
        query_exe = 'INSERT INTO dataStored(query) VALUES (%s)'
        mycursor.execute(query_exe,val)
        try:
            val1 = (query,category,)
        except:
            category = "none"
            val1 = (query,category,)
        query_exe1 = 'INSERT INTO trainingModel(query, keyword) VALUES (%s, %s)'
        mycursor.execute(query_exe1,val1)

        mydb.commit()

        if "open google" in query:
            webbrowser.open("https://www.google.com")
            speak("sure...")
        elif "open youtube" in query:
            webbrowser.open("https://www.youtube.com")
            speak("sure...")
        elif "open website" in query:
            naturalLanguageProcessing(query)
            query = updated_query
            print(query)
            query = query.replace("open website","")
            query = str.strip(query)
            chrome_path = r"/Users/keshavnarang/Desktop/project/chromedriver"
            driver = webdriver.Chrome(chrome_path)
            url = "https://www."+query
            driver.get(url)
        elif "time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"the time is {strTime}")
        elif ("open app" in query) or ("launch app" in query) or ("open the app" in query):
            naturalLanguageProcessing(query)
            query = updated_query
            if("open app" in query):
                query = query.replace("open app","")
            else:
                query = query.replace("launch app","")
            query = str.lstrip(query)
            query = query.title()
            query = query.replace(" ","\ ")
            print(query)
            try:
                path = "/System/Applications/"+query+".app"
                opener ="open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, path])
            except:
                speak("unable to find the app")
        elif "send email" in query:
            try:
                speak("tell me the email ID of that person")
                to = takeCommand().lower()
                to = str.strip(to)
                to = to.replace(" ","")
                print(to)
                speak("what should I send")
                content = takeCommand()
                print(content)
                sendEmail(to, content)
                speak("email has been sent")
            except:
                speak("sorry unable to send the email")
        elif "news" in query:
            url = "https://news.google.com/?hl=en-IN&gl=IN&ceid=IN:en"
            r = requests.get(url)
            htmlcontent = r.content
            soup = BeautifulSoup(htmlcontent, 'html.parser')
            allNews = soup.find_all("h3", class_="ipQwMb")
            news = []
            for i in range(5):
                news.append(allNews[i].text)
                print(allNews[i].text)
            speak("Here are your top 5 news")
            for i in news:
                speak(i)
        elif "weather" in query:
            chrome_path = r"/Users/keshavnarang/Desktop/project/chromedriver"
            driver = webdriver.Chrome(chrome_path)
            url = "https://www.msn.com/en-in/weather/today?gps=1"
            driver.get(url)
            speak("Do you want the current location or some other?.. say current for current location else say the location name")
            location = takeCommand().lower()
            time.sleep(5)
            if "current" in location:
                driver.find_element_by_css_selector("div.header").click()
                driver.find_element_by_css_selector("li.buttons").click()
                time.sleep(5)
            else:
                driver.find_element_by_css_selector("div.header").click()
                btn = driver.find_element_by_css_selector("div.add-loc-as-container").click()
                btn = driver.find_element_by_xpath('//*[@id="main"]/div/div[1]/div[1]/div[2]/div[2]/div[1]/form/div[1]/input').send_keys(location)
                time.sleep(5)
                driver.find_element_by_css_selector("input.query").send_keys(Keys.ENTER)
            temp = driver.find_element_by_css_selector("span.current").get_attribute("aria-label")
            print(temp)
            location = driver.find_element_by_css_selector("div.header").text
            print(location)
            speak(f"{temp} Celsius at {location}")
        elif "set timer for" in query:
            naturalLanguageProcessing(query)
            query = updated_query
            print(query)
            chrome_path = r"/Users/keshavnarang/Desktop/project/chromedriver"
            driver = webdriver.Chrome(chrome_path)
            url = "https://www.google.com/search?q="+query
            driver.get(url)
            query = query.replace("set timer for","")
            speak(f"your timer for {query} starts now")
        elif ("direction" in query) or ("route" in query):
            naturalLanguageProcessing(query)
            query = updated_query
            print(query)
            chrome_path = r"/Users/keshavnarang/Desktop/project/chromedriver"
            driver = webdriver.Chrome(chrome_path)
            url = "https://www.google.com/search?q="+query
            driver.get(url)
            driver.find_element_by_css_selector("div.udku3").click()
            time.sleep(5)
            try:
                driver.find_element_by_id("section-directions-trip-0").click()
                speak("Here is your direction on the screen.. have a safe journey")
            except:
                speak("sorry unable to find the direction")
        elif "joke" in query:
            speak("sorry I have a bad sense of humor... it's better I keep my speaker shut.. Ha Ha Ha Ha")
        elif "create notes" in query:
            path = "/System/Applications/Notes.app"
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path])
        elif "emails" in query:
            path = "/System/Applications/Mail.app"
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path])
        elif ("date" in query) or ("calendar" in query):
            path = "/Applications/Calendar.app"
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path])
        elif ("movie" in query) or ("netflix" in query):
            chrome_path = r"/Users/keshavnarang/Desktop/project/chromedriver"
            driver = webdriver.Chrome(chrome_path)
            speak("which movie do you want to watch")
            movie_name = takeCommand()
            movie_name = str.lstrip(movie_name)
            movie_name = movie_name.replace(" ","%20")
            url = "https://www.netflix.com/search?q="+movie_name
            driver.get(url)
            username = driver.find_element_by_id("id_userLoginId")
            username.send_keys(os.getenv('NETFLIX_ID'))
            password = driver.find_element_by_id("id_password")
            password.send_keys(os.getenv('NETFLIX_PASSWORD'))
            loginbutton = driver.find_element_by_css_selector("button.btn.login-button.btn-submit.btn-small").click()
            time.sleep(5)
            profile = driver.find_elements_by_css_selector("div.profile-icon")
            profile[0].click()
            search_button = driver.find_element_by_css_selector("button.searchTab").click()
            search_button1 = driver.find_element_by_css_selector("div.searchInput")
            search_button1.send_keys(movie_name)
        elif "buy" in query or "order" in query:
            chrome_path = r"/Users/keshavnarang/Desktop/project/chromedriver"
            driver = webdriver.Chrome(chrome_path)
            url = "https://www.amazon.in/"
            driver.get(url)
            speak("what do you want to order")
            item = takeCommand()
            searchBox = driver.find_element_by_id("twotabsearchtextbox")
            searchBox.send_keys(item)
            searchBoxButton = driver.find_element_by_css_selector("input.nav-input")
            searchBoxButton.click()
            speak(f"here is the list of all the {item} you searched for")
        elif 'calculator' in query or 'calculate' in query:
            speak("tell me the first number")
            number1 = takeCommand()
            number1 = int(number1)
            speak("tell me the second number")
            number2 = takeCommand()
            number2 = int(number2)
            speak("what do you want me to do? add,subtract,multiply or divide")
            task = takeCommand()
            if "add" in task:
                number3 = number1 + number2
                number3 = str(number3)
                speak(number3)
            if "subtract" in task:
                number3 = number1 - number1
                number3 = str(number3)
                speak(number3)
            if "multiply" in task:
                number3 = number1 * number2
                number3 = str(number3)
                speak(number3)
            if "divide" in task:
                number3 = number1 / number2
                number3 = str(number3)
                speak(number3)
        elif "translate" in query:
            speak("In which language you want me to translate your language?")
            language = takeCommand().lower()
            print(language)
            global lang
            global translated
            flag = True
            if 'spanish' in language:
                value = 'es'
                lang = 14
            elif 'chinese' in language:
                value = 'zh-CN'
                lang = 25
            elif 'italian' in language:
                value = 'it'
                lang = 7
            elif 'hindi' in language:
                value = 'hi'
                lang = 20
            elif 'mongolian' in language:
                value = 'mn'
                lang = 27
            elif 'russian' in language:
                value = 'ru'
                lang = 33
            elif 'ukrainian' in language:
                value = 'uk'
                lang = 33
            elif 'french' in language:
                value = 'fr'
                lang = 25
            elif 'indonesian' in language:
                value = 'id'
                lang = 24
            elif 'japanese' in language:
                value = 'ja'
                lang = 18
            elif 'slovak' in language:
                value = 'sk'
                lang = 24
            else:
                speak("Unable to translate the language you selected")
                flag = False
            if flag == True:
                speak("what do you want me to translate?")
                text = takeCommand()
                translated = translator.translate(text, dest=value).text
                print(translated)
                engine.setProperty('voice',voices[lang].id)
                engine.say(translated)
                engine.runAndWait()
        elif "search wikipedia" in query:
            speak("searching Wikipedia...")
            naturalLanguageProcessing(query)
            query = updated_query
            print(query)
            query = query.replace("search wikipedia for","")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            speak(results)
        elif "do wikipedia search" in query:
            speak("searching Wikipedia...")
            naturalLanguageProcessing(query)
            query = updated_query
            print(query)
            query = query.replace("do a wikipedia search for","")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            speak(results)
        elif ("play song" in query) or ("play the song"):
            song_length = query.find("song")
            song_name = query[song_length+5:]
            song_name1 = song_name
            song_name = song_name.replace(" ","%20")
            chrome_path = r"/Users/keshavnarang/Desktop/project/chromedriver"
            driver = webdriver.Chrome(chrome_path)
            url = "https://gaana.com/search/"+song_name
            driver.get(url)
            time.sleep(5)
            speak(f"here is your song {song_name1}")
            driver.find_element_by_css_selector("h3.item-heading").click()
        else:
            query = str.lstrip(query)
            query = query.replace(" ","+")
            chrome_path = r"/Users/keshavnarang/Desktop/project/chromedriver"
            driver = webdriver.Chrome(chrome_path)
            url = "https://www.google.com/search?q="+query
            driver.get(url)
            speak("sorry unable to find query here is what I found on google")
            time.sleep(5)
            result = driver.find_element_by_css_selector("span.st").text
            print(result)
            speak(result)

root = tk.Tk()
root.title("Virtual Assistant")
img = ImageTk.PhotoImage(Image.open("/Users/keshavnarang/Desktop/project/asistente-virtual.png"))
panel = tk.Label(root, image = img)
panel.pack(side = "top", fill = "both", expand = "yes")
label = tk.Label(root, text="Welcome to Virtual Assistant.. Click the Command button and speak the query")
label.pack()
button1 = tk.Button(root, text="command", width=20, command=main)
button1.pack()
button2 = tk.Button(root, text='Quit', width=20, command=root.destroy)
button2.pack()
root.mainloop()
