## Run this command in terminal  before executing this program
## rasa run -m models --endpoints endpoints.yml --port 5002 --credentials credentials.yml
## and also run this in seperate terminal
## rasa run actions

import requests
import speech_recognition as sr     # import the library
import subprocess
from gtts import gTTS

bot_message = ""
message=""

# Start with only Hey Roger
while True:
    recognizer = sr. Recognizer()
    with sr.Microphone() as source:
        print("Say Hey Roger to start talking with chatbot: ")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            message = recognizer.recognize_google(audio).lower()
            print("You said : {}".format(message))
        except:
            pass
        
        if(message == "hey siri"):
            r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": "Hello"})
            print("Bot says, ",end=' ')
            for i in r.json():
                bot_message = i['text']
                print(f"{bot_message}")

            myobj = gTTS(text=bot_message)
            myobj.save("welcome.mp3")
            print('saved')
            # Playing the converted file
            subprocess.call(['mpg123', "welcome.mp3"])

            while (bot_message != "bye" or bot_message!='thanks'):
                message = " "

                print("Speak Anything :")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)  
                try:
                    message = recognizer.recognize_google(audio)  
                    print("You said : {}".format(message))

                except:
                    print("Sorry could not recognize your voice")
                    # bot_message = "Sorry could not recognize your voice"

                if len(message) == 0:
                    continue
                print("Sending message now...")

                r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message})

                print("Bot says, ",end=' ')
                for i in r.json():
                    bot_message = i['text'].lower()
                    print(f"{bot_message}")

                myobj = gTTS(text=bot_message)
                myobj.save("welcome.mp3")
                print('saved')
                # Playing the converted file
                subprocess.call(['mpg123', "welcome.mp3"])

                if (bot_message == "bye"):
                    break
    