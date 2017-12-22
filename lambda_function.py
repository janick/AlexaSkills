import logging

import requests
import time
import datetime


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#
# Response object
#
class Response:
    def __init__(self, title, say):
        self.rsp = {}
        self.rsp['outputSpeech'] = {'type': 'SSML',
                                    'ssml':  "<speak>" + say + "</speak>"}
        self.rsp['card'] = {'type': 'Simple',
                            'title': "PortlandMaps - " + title,
                            'content': say}
        self.rsp['shouldEndSession'] = True

    def card(self, type, args):
        args['type'] = type
        self.rsp['card'] = args

    def reprompt(self, say):
        self.rsp['reprompt'] = {'outputSpeech': {'type': 'SSML',
                                                 'ssml':  "<speak>" + say + "</speak>"}}
        self.rsp['shouldEndSession'] = False

    def keepSessionOpen(self):
        self.rsp['shouldEndSession'] = False




class EventHandler:

    def __init__(self, context, state):
        self.context        = context
        self.state          = state
        self.response       = None


    def my_intent(self):
        self.response = Response("My Intent",
                                 "This is my intent response")

        return True


    # When the skill gets launched
    def onLaunch(self):
        self.response = Response("Welcome",
                                 "Welcome to my skill.")
        self.response.reprompt("I am unable to answer this question. For sample questions, say Help.")
        return True


    def help(self):
        self.response = Response("Help",
                                 "I can help you query information about something. " + \
                                     "For example, you can ask me, " + \
                                     "Utterance, or" + \
                                     "Question")
        self.response.keepSessionOpen()
        return True


    def onEnd(self):
        self.response = Response("Session Ended",
                                 "Have a nice day")
        return True


    # When the skill gets an intent
    def onIntent(self, intent):
        if intent['name'] == "HelpIntent":
            return self.help()
        if intent['name'] == "AMAZON.HelpIntent":
            return self.help()
        if intent['name'] == "MyIntent":
            return self.my_intent()
        if intent['name'] == "AMAZON.CancelIntent" or intent['name'] == "AMAZON.StopIntent":
            return self.onEnd()

        raise ValueError("Invalid intent")


    # When the skill gets an event
    def onRequest(self, request):
        isOK = False

        if request['type'] == "LaunchRequest":
            isOK = self.onLaunch()
        elif request['type'] == "IntentRequest":
            isOK = self.onIntent(request['intent'])
        elif request['type'] == "SessionEndedRequest":
            isOK = self.onEnd()
        else:
            logging.error("Unexpected request " + request['type'] + " received.")

        if self.response == None:
            if isOK:
                return None

            self.response = Response("Sorry",
                                     "Sorry. Something went wrong")

        return {'version': '1.0',
                'sessionAttributes': self.state,
                'response': self.response.rsp}



# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    logging.info("event.session.application.applicationId=" +
                 event['session']['application']['applicationId'])

    """
    Prevent someone else from configuring a skill that sends requests to this function.
    """
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.<UUID>"):
        raise ValueError("Invalid Application ID")

    attributes = {}
    if 'attributes' in event['session']:
        attributes = event['session']['attributes']

    return EventHandler(event['context'], attributes).onRequest(event['request'])
