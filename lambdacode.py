from __future__ import print_function
import httplib
import json
import logging

prog1 = ["c", "d flat", "d", "e flat", "e", "f", "g flat", "g", "a flat", "a", "b flat", "b"]
prog2 = ["f", "g flat", "g", "a flat", "a", "b flat", "b", "c", "d flat", "d", "e flat", "e"]
prog3 = ["g", "a flat", "a", "b flat", "b", "c", "d flat", "d", "e flat", "e", "f", "f sharp"]
prog4 = ["a minor", "b flat minor", "b minor", "c minor", "c sharp minor", "d minor", "e flat minor", "e minor", "f minor", "f sharp minor", "g minor", "g sharp minor"]
progs = {"0": prog1, "1": prog2, "2": prog3, "3": prog4, "4": prog1}

sssrc = "'https://s3.amazonaws.com/echo-jam-audio-files/"

def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] != "amzn1.echo-sdk-ams.app.b36bad7c-ffbd-492d-8725-88c71aabba91"):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "LaunchRequest" or event['session']['new'] == "true":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    if intent_name == "AMAZON.RepeatIntent":
        return handle_repeat(intent_request, session["attributes"])
    elif intent_name == "AMAZON.HelpIntent" or intent_name == "HelpMe":
        return halp(intent_request)
    elif intent_name == "Rhyme":
        return rhyme(intent_request, session["attributes"])
    elif intent_name == "Metronome":
        return metronome(intent_request, session["attributes"])
    elif intent_name == "OneChord":
        return one_chord(intent_request, session["attributes"])
    elif intent_name == "ChordProgression":
        return chord_progression(intent_request, session["attributes"])
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return error_message()

def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])
    return goodbye()

def handle_repeat(request, attribs):
    if "attr" not in attribs and "feature" not in attribs["attr"]:
        return error_message()
    if attribs["attr"]["feature"] == "rhyme":
        return rhyme(request, attribs)
    elif attribs["attr"]["feature"] == "metronome":
        return metronome(request, attribs)
    elif attribs["attr"]["feature"] == "one_chord":
        return one_chord(request, attribs)
    elif attribs["attr"]["feature"] == "chord_progression":
        return chord_progression(request, attribs)
    else:
        return halp(request)

def rhyme(request, attribs):
    reqrestrictions = ""
    attributes = attribs["attr"]
    if ("attr" not in attribs) or ("attr" in attribs and "feature" not in attribs["attr"]) or ("attr" in attribs and "feature" in attribs["attr"] and attribs["attr"]["feature"] != "rhyme"):
        attributes = {"feature": "rhyme", "word1": "", "word2": ""}
        mrsdrw = ["", "", "", "", ""]     #means rhymes sounds describes relates
        mrsdrws = 0
        words = "1"
        if "value" in request["intent"]["slots"]["Means"]:
            mrsdrw[0] = "ml=" + request["intent"]["slots"]["Means"]["value"]
            mrsdrws += 1
            attributes["word1"] = mrsdrw[0]
            words = "2"
        if "value" in request["intent"]["slots"]["Rhymes"]:
            mrsdrw[1] = "rel_rhy=" + request["intent"]["slots"]["Rhymes"]["value"]
            mrsdrws += 1
            attributes["word" + words] = mrsdrw[1]
            words = "2"
        if "value" in request["intent"]["slots"]["Sounds"]:
            mrsdrw[2] = "sl=" + request["intent"]["slots"]["Sounds"]["value"]
            mrsdrws += 1
            attributes["word" + words] = mrsdrw[2]
            words = "2"
        if "value" in request["intent"]["slots"]["Describes"]:
            mrsdrw[3] = "rel_jjb=" + request["intent"]["slots"]["Describes"]["value"]
            mrsdrws += 1
            attributes["word" + words] = mrsdrw[3]
            words = "2"
        if "value" in request["intent"]["slots"]["Relates"]:
            mrsdrw[4] = "topics=" + request["intent"]["slots"]["Relates"]["value"]
            mrsdrws += 1
            attributes["word" + words] = mrsdrw[4]
        if mrsdrws > 2:
            card_title = "Error! Too many restrictions."
            speech_output = "Please ask for words with one or two restrictions."
            should_end_session = False
            return response(card_title, speech_output, None, should_end_session, "PlainText", {})
        for z in range(0, 5):
            reqrestrictions += mrsdrw[z] + "&"
        reqrestrictions = reqrestrictions[:-2]
    else:
        reqrestrictions = attribs["attr"]["word1"]
        if attribs["attr"]["word2"]:
            reqrestrictions +=  "&" + attribs["attr"]["word2"]
    card_title = "Word Help"
    req = httplib.HTTPSConnection("api.datamuse.com")
    req.request("GET", "/words?" + reqrestrictions)
    req1 = req.getresponse()
    req2 = req1.read()
    req3 = json.loads(req2)
    speech_output = "There are no words that match the conditions you specified."
    if len(req3) > 0:
        speech_output = "How about: " + req3[0]["word"]
        q = 1
        while q < len(req3):
            speech_output = speech_output + ", " + req3[q]["word"]
            q += 1
    should_end_session = False
    return response(card_title, speech_output, None, should_end_session, "PlainText", attributes)

def metronome(request, attribs):
    attributes = attribs["attr"]
    bpm = ""
    if ("attr" not in attribs) or ("attr" in attribs and "feature" not in attribs["attr"]) or ("attr" in attribs and "feature" in attribs["attr"] and attribs["attr"]["feature"] != "metronome"):
        bpm = request['intent']['slots']['Rate']['value']
        attributes = {"feature": "metronome", "bpm": bpm}
    else:
        bpm = attribs["attr"]["bpm"]
    playbpm = str(int(bpm) - (int(bpm) % 5))
    card_title = "Metronome"
    speech_output = "<speak>" + bpm + " bpm <audio src=" + sssrc + "metronome/" + playbpm + "bpm.mp3' /> </speak>"
    should_end_session = False
    return response(card_title, speech_output, None, should_end_session, "SSML", attributes)

def one_chord(request, attribs):
    attributes = attribs["attr"]
    chord = ""
    if ("attr" not in attribs) or ("attr" in attribs and "feature" not in attribs["attr"]) or ("attr" in attribs and "feature" in attribs["attr"] and attribs["attr"]["feature"] != "one_chord"):
        chord = request['intent']['slots']['TheChord']['value']
        attributes = {"feature": "one_chord", "chord": chord}
    else:
        chord = attribs["attr"]["chord"]
    card_title = "Chord"
    speech_output = "<speak>" + chord + " chord <audio src=" + sssrc + "chords/" + chord.replace(" ", "+").replace(".", "").lower() + "+chord.mp3' /> </speak>"
    should_end_session = False
    return response(card_title, speech_output, None, should_end_session, "SSML", attributes)

def chord_progression(request, attribs):
    attributes = attribs["attr"]
    rootchord = ""
    if ("attr" not in attribs) or ("attr" in attribs and "feature" not in attribs["attr"]) or ("attr" in attribs and "feature" in attribs["attr"] and attribs["attr"]["feature"] != "chord_progression"):
        rootchord = request['intent']['slots']['Key']['value'].replace(".", "").lower()
        attributes = {"feature": "chord_progression", "key": rootchord}
    else:
        rootchord = attribs["attr"]["key"]
    card_title = "Chord Progression"
    root = prog1.index(rootchord)
    theprog = [0, 0, 0, 0, 0]
    speech_output = "<speak> chord progression in the key of " + rootchord + ": "
    for z in range(0, 5):
        speech_output += progs[str(z)][root].replace(" ", "-") + ", "
        theprog[z] = progs[str(z)][root].replace(" ", "+").replace(".", "").lower()
    for z in range(0, 5):
        speech_output += " <audio src=" + sssrc + "chords/" + theprog[z] + "+chord.mp3' />"
    speech_output += " </speak>"
    should_end_session = False
    return response(card_title, speech_output, None, should_end_session, "SSML", attributes)

def halp(request):
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
        speech_output = "You can ask for help with words by saying, 'Give me words that rhyme with, Amazon', or, 'Give me words that mean Amazon', or, 'Give me words that mean noisy which rhyme with Amazon', or 'Give me words used to describe Amazon'"
    else:
        speech_output = "You can ask for help for specific features by saying, 'Help chords, help rhyming, help metronome, or help chord progression'"
    reprompt_text = "What do you need help with?"
    should_end_session = False
    return response(card_title, speech_output, reprompt_text, should_end_session, "PlainText", {})

def get_welcome_response():
    card_title = "Welcome"
    speech_output = "Welcome to Echo Jam. To get help, say help. "
    reprompt_text = getHelpMessage()
    should_end_session = False
    return response(card_title, speech_output, reprompt_text, should_end_session, "PlainText", {})

def error_message():
    card_title = "Error"
    speech_output = "I could not understand the feature you want to use."
    reprompt_text = getHelpMessage()
    should_end_session = False
    return response(card_title, speech_output, reprompt_text, should_end_session, "PlainText", {})

def goodbye():
    card_title = "Goodbye"
    speech_output = "Thank you for using Echo Jam."
    should_end_session = True
    return response(card_title, speech_output, None, should_end_session, "PlainText", {})

def getHelpMessage():
    return "You can ask me 'Give me a metronome at blank bpm' or 'Give me words that rhyme with blank'. You can also ask me 'Give me a chord progression in key blank' or 'Give me chord blank'."

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for making music with Echo Jam. Have a nice day! "
    should_end_session = True
    return response(card_title, speech_output, None, should_end_session, "PlainText", {})

def response(title, output, reprompt, endsesh, outputtype, attributes):
    ttype = "text"
    cardoutput = output
    if outputtype == "SSML":
        ttype = "ssml"
        cardoutput = output.replace(sssrc, "").replace("<speak>", "")[:output.index("<audio")-8]
    return {
        'version': '1.0',
        'sessionAttributes': {"attr": attributes},
        'response': {
            'outputSpeech': {
                'type': outputtype,
                ttype: output
            },
            'card': {
                'type': 'Simple',
                'title': 'Echo Jam - ' + title,
                'content': 'Echo Jam - ' + cardoutput
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt
                }
            },
            'shouldEndSession': endsesh
        }
    }
