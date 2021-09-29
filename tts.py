import pyttsx3

engine = pyttsx3.init(driverName='flite')

engine.setProperty('rate',140)

"""VOICE"""
voices = engine.getProperty('voices')       #getting details of current voice
# engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty('voice', voices[2].id)   #changing index, changes voices. 1 for female

engine.say("I will speak this text.")
engine.runAndWait()