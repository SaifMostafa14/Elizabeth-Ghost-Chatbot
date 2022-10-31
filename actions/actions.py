# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

class ActionLibraryHours(Action):
    
    def name(self) -> Text:
        return "action_library_hours"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="The library opens at 8 am and closes at midnight Monday to Thursday. On Friday 8 AM to 6 PM. On Saturday 10 AM to 6 PM And on Sunday 11 AM to Midnight.")
		
        return []

class ActionPrinting(Action):
    def name(self) -> Text:
        return "action_printing"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text= "You can use the printers located on the main floor with your 800-number. Visit https://printing.stetson.edu/user and upload the documents you with to print to the website")
        return []

class ActionRoomReservation(Action):
    def name(self) -> Text: 
        return "action_room_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text= "You can reserve a study room at the library through this link https://www2.stetson.edu/library/services/reserve-a-library-room/")

        return []


