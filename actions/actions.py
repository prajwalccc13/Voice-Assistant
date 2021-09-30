# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions



from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import Dict, Text, Any, List, Union, Type, Optional

import typing
import logging
import requests
import json
import re
import csv
import random

import actions.tracing

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset, EventType
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.executor import CollectingDispatcher

from datetime import datetime, date, time, timedelta

from newsapi import NewsApiClient


logger = logging.getLogger(__name__)
tracer = actions.tracing.init_tracer("action_server")


# This is a simple example for a custom action which utters "Hello World!"
class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


class ActionRandomJoke(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_random_joke"

    def run(self, dispatcher, tracker, domain):
        with actions.tracing.extract_start_span(
            tracer, domain.get("headers"), self.name()
        ):
            # request = json.loads(requests.get("http://api.icndb.com/jokes/random").text)
            # joke = request["value"][
            #     "joke"
            # ]  # extract a joke from returned json response
            request = json.loads(requests.get("https://v2.jokeapi.dev/joke/Any?type=single").text)
            joke = request["joke"]
            dispatcher.utter_message(joke)  # send the message back to the user
            return []


class ActionInspiringQuote(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_inspiring_quote"

    def run(self, dispatcher, tracker, domain):
        with actions.tracing.extract_start_span(
            tracer, domain.get("headers"), self.name()
        ):
            # what your action should do
            request = requests.get(
                "https://api.forismatic.com/api/1.0/?method=getQuote&lang=en&format=json"
            )
            if request.status_code == 200:
                logger.info("request.text: {}".format(request.text))
                fixed = re.sub(
                    r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r"", request.text
                )
                resp = json.loads(fixed)
                author = resp["quoteAuthor"]
                quote = resp["quoteText"]
                # permalink = resp["quoteLink"]
                # message = quote + ' - ' + author + ' ' + permalink
                message = quote + " By " + author
            else:
                message = (
                    "Sorry, couldn't fetch quote right now. Please try again later."
                )
            # dispatcher.utter_message(message) #send the message back to the user
            dispatcher.utter_message(message)  # send the message back to the user
            return []


class ActionTellTime(Action):

    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        message = "Current System Time is " + current_time

        dispatcher.utter_message(message)

        return []


class ActionTellDate(Action):

    def name(self) -> Text:
        return "action_tell_date"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        today = date.today()

        current_date = today.strftime("%B %d, %Y")
        message = "It is " + current_date

        dispatcher.utter_message(message)

        return []


class ActionReadNews(Action):

    def name(self) -> Text:
        return "action_read_news"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            newsapi = NewsApiClient(api_key='a58184c8b6014a9ea17772a36ff15f01')
            top_headlines = newsapi.get_top_headlines(language='en')

            if top_headlines['status']== 'ok':
                newsapi = NewsApiClient(api_key='a58184c8b6014a9ea17772a36ff15f01')

                # /v2/top-headlines
                top_headlines = newsapi.get_top_headlines(language='en')
                resp = list(top_headlines['articles'])
                news = ""

                for i in range(5):
                    news = news + resp[i]['title'] + '\n'
                    # permalink = resp["quoteLink"]
                    # message = quote + ' - ' + author + ' ' + permalink
                message = news + "\n" + "Please read detailed news from mobile app or website."
            else:
                message = (
                    "Sorry, couldn't fetch news right now. Please try again later."
                )

            dispatcher.utter_message(message)

            return []


class ActionChangeStatusAppliances(Action):

    def name(self) -> Text:
        return "action_change_status_appliances"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            # Entities
            status_change = next(tracker.get_latest_entity_values("status_change"), None)
            room = next(tracker.get_latest_entity_values("room"), None)
            appliance = next(tracker.get_latest_entity_values("appliance"), None)

            validate_flag = False
            status_flag = False
            room_flag = False
            device_flag = False

            url = "http://192.168.1.15:8000/"

            # Check if all data are provided
            if status_change and room and appliance:
                validate_flag = True
                status_change = status_change.lower()
                room = room.lower()
                appliance = appliance.lower()
            else:
                validate_flag = False
                message = "Couldn't get all data. Please say again."

            if validate_flag:
                if status_change == "turn on" or status_change == "turn off": 
                    status_flag = True
                    if status_change == 'turn on':
                        status_temp = True
                    if status_change == 'turn off':
                        status_temp = False
                else:
                    status_flag = False
                    message = "Couldn't recognize the voice. Please say again."

            # if - check if all data are provided
            if status_flag:
                if status_change and room and appliance:
                    
                    # For Rooms
                    room_url = url + 'api/room/'
                    rooms = requests.get(room_url).json()
                    if rooms:
                        for data in rooms:
                            # Check if provided room is added in database
                            if data['name'].lower() == room:
                                room_flag = True
                                room_id = data['id']

                                break
                        else:
                            room_flag = False
                            message = "No rooms named " + room + " found. Please check and say again"
                    else:
                        room_flag = False
                        message = "No rooms added. Please add rooms first."
                else:
                    room_flag = False
                    message = "Couldn't recognize the voice. Please say again."


            # Fetch all devices
            if room_flag:
                device_url = url + 'api/room/' + str(room_id) + '/device/'
                device = requests.get(device_url).json()

                if device:
                    # Check if provided device is added in database
                    for data in device:
                        # if device is available
                        if data['name'].lower() == appliance:
                            device_flag = True
                            device_id = data['id']
                            if status_temp:
                                if status_temp == data['status']:
                                    message = room + " " + appliance + " already turned on."
                                else:
                                    device_detail_url = url + 'api/device/' + str(device_id) + '/'
                                    device_patch = requests.patch(device_detail_url, data ={
                                        'status': True,
                                        'pin': int(data['pin'])
                                    })
                                    # message = "Turning on the " + room + " " + appliance
                                    if device_patch.status_code == 200:
                                        message = "Turned on the " + room + " " + appliance
                                    else: 
                                        message = "Couldn't turn on the " + room + " " + appliance + ". Please try again."
                            else:
                                if status_temp == data['status']:
                                    message = room + " " + appliance + " already turned off."
                                else:
                                    device_detail_url = url + 'api/device/' + str(device_id) + '/'
                                    device_patch = requests.patch(device_detail_url, data ={
                                        'status': False,
                                        'pin': int(data['pin'])
                                    })
                                    # message = "Turning on the " + room + " " + appliance
                                    if device_patch.status_code == 200:
                                        message = "Turned off the " + room + " " + appliance
                                    else: 
                                        message = "Couldn't turn off the " + room + " " + appliance + ". Please try again."      
                    if not device_flag:
                        message = "No device named " + appliance + ' found.'
                else:
                    message = "No devices added in " + room + " . Please add devices first."  

            dispatcher.utter_message(message)

            return []