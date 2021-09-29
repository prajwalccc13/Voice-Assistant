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

            status_change = next(tracker.get_latest_entity_values("status_change"), None)

            room = next(tracker.get_latest_entity_values("room"), None)

            appliance = next(tracker.get_latest_entity_values("appliance"), None)


            message = "Status Change: " + status_change + "\n Room: " + room + "\n Appliance: " + appliance

            # if top_headlines['status']== 'ok':
                
            #     message = "Turned On the light"
            # else:
            #     message = (
            #         "Sorry, couldn't fetch news right now. Please try again later."
            #     )

            dispatcher.utter_message(message)

            return []