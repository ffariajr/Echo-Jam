"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from urllib2 import Request

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
            "amzn1.echo-sdk-ams.app.b36bad7c-ffbd-492d-8725-88c71aabba91"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "Rhyme":
        return rhyme(intent_request)
    elif intent_name == "Metronome":
        return metronome(intent_request)
    elif intent_name == "OneChord":
        return one_chord(intent_request)
    elif intent_name == "ChordProgression":
        return chord_progression(intent_request)
    elif intent_name == "AMAZON.HelpIntent" or intent_name == "HelpMe":
        return halp(intent_request)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here
    #handle_session_end_request()
# --------------- Functions that control the skill's behavior ------------------

def rhyme(request):
    session_attributes = {}
    card_title = "Rhyme"
    rhyme = request['intent']['slots']['TheWord']['value']
    req = Request("https://api.datamuse.com/words?rel_rhy=" + rhyme)
    speech_output = "How about "
    for(x in req(json)):
        speech_output = speech_output + " " + x[u'word']
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
def metronome(request):
    session_attributes = {}
    card_title = "Metronome"
    bpm = request['intent']['slots']['Rate']['value']
    speech_output = "<speak>" + bpm + " bpm <audio src='https://s3.amazonaws.com/echo-jam-audio-files/metronome/" + bpm + "bpm.mp3' /> </speak>"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response_ssml(
        card_title, speech_output, None, should_end_session))

def one_chord(request):
    session_attributes = {}
    card_title = "Chord"
    chord = request['intent']['slots']['TheChord']['value']
    speech_output = "<speak>" + chord + " chord <audio src='https://s3.amazonaws.com/echo-jam-audio-files/chords/" + chord + " chord.mp3' /> </speak>"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response_ssml(
        card_title, speech_output, None, should_end_session))
def chord_progression(request):
    return ""
def halp(request):
    session_attributes = {}
    card_title = "Help"
    feature = request['intent']['slots']['Help']
    if(len(feature) > 1):
        feature = feature['value']
    else:
        feature = ""
    speech_output = ""
    if(feature == "metronome"):
        speech_output = "You can ask for a tempo by saying, 'Give me a beat at 100 bpm'"
    elif(feature == "chord" or feature == "chords"):
        speech_output = "You can ask for a chord by saying, 'Give me an ay chord'"
    elif(feature == "chord progression"):
        speech_output = "You can ask for a chord progression by saying, 'Give me a chord progression in key, ay'"
    elif(feature == "rhyme" or feature == "rhyming"):
        speech_output = "You can ask for rhyming words by saying, 'Give me words that rhyme with, Amazon'"
    else:
        speech_output = "You can ask for help for specific features by saying, 'Help chords, help rhyming, help metronome, or help chord progression'"
    reprompt_text = "What do you need help with?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Echo Jam. " \
                    "To get help, say help. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = getHelpMessage()
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getHelpMessage():
    return "You can ask me 'Give me a metronome at blank bpm' or 'Give me words that rhyme with blank'." \
           "You can also ask me 'Give me a chord progression in key blank' or 'Give me chord blank'."

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for making music with Echo Jam. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Echo Jam - ' + title,
            'content': 'Echo Jam - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
def build_speechlet_response_ssml(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Echo Jam - ' + title,
            'content': 'Echo Jam - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }    


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
