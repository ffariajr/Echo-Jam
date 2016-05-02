from __future__ import print_function
import httplib
import json
import logging

# Below, we create 4 arrays. Each array holds individual chords, with corresponding indexes in each array representing
# a chord progression. For example, prog1[0] holds "c", and prog2[0] holds "f". Each of the [0] index slots together forms the 
# "chord progression in key C". The fifth slot in the chord progression is the same as the first one (ex. C progression begins 
# and ends with "C". The progs{} stores each of the chords in its slots for Alexa to later play to the user in order

prog1 = ["c", "d flat", "d", "e flat", "e", "f", "g flat", "g", "a flat", "a", "b flat", "b"]
prog2 = ["f", "g flat", "g", "a flat", "a", "b flat", "b", "c", "d flat", "d", "e flat", "e"]
prog3 = ["g", "a flat", "a", "b flat", "b", "c", "d flat", "d", "e flat", "e", "f", "f sharp"]
prog4 = ["a minor", "b flat minor", "b minor", "c minor", "c sharp minor", "d minor", "e flat minor", "e minor", "f minor", "f sharp minor", "g minor", "g sharp minor"]
progs = {"0": prog1, "1": prog2, "2": prog3, "3": prog4, "4": prog1}

# base url for where our audio files are stored
sssrc = "'https://s3.amazonaws.com/echo-jam-audio-files/"

# "main" function
def lambda_handler(event, context):
    
    # checks if the skill that called this function is actually the skill I created, and not another developer's skill
    if (event['session']['application']['applicationId'] != "amzn1.echo-sdk-ams.app.b36bad7c-ffbd-492d-8725-88c71aabba91"):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "LaunchRequest" or event['session']['new'] == "true": # skill session started
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest": # skill feature requested after the session has started
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest": # user has ended the session
        return goodbye()
    else:
        return error_message()

# simple welcome message
def on_launch(launch_request, session):
    return get_welcome_response()

# Below, we are telling Alexa to take the user utterance and pass it to the corresponding function or command.
# For example, line 50 and 51 are referenced when a user says a command related to rhyming. Our code will take that user request
# and call the rhyme() function with the user's request as a parameter.
def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name'] # based on our intent schema and sample utterances, Alexa passes in what intent the user asked for
    if intent_name == "AMAZON.RepeatIntent":
        return handle_repeat(intent_request, session["attributes"])
    elif intent_name == "AMAZON.HelpIntent" or intent_name == "HelpMe":
        return halp(intent_request) # help is a keyword
    elif intent_name == "Rhyme":
        return rhyme(intent_request, {"attr": ""})
    elif intent_name == "Metronome":
        return metronome(intent_request, {"attr": ""})
    elif intent_name == "OneChord":
        return one_chord(intent_request, {"attr": ""})
    elif intent_name == "ChordProgression":
        return chord_progression(intent_request, {"attr": ""})
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return goodbye()
    else:
        return error_message()

def handle_repeat(request, attribs):
    if "attr" not in attribs and "feature" not in attribs["attr"]:  # redirects to error message if user asks to repeat and the previous request was a help request or a session start request
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

# This is the rhyming function, which allows users to give Alexa a word to rhyme or find words with similar meanings
# We make use of the Datamuse public API to allow for commands such as "Give me word that rhymes with 'dog'" or
# "Give me words that rhyme with 'cat' that have to do with 'Canada'"

def rhyme(request, attribs):
    reqrestrictions = "" # request restrictions
    attributes = attribs["attr"]
    if ("attr" not in attribs) or ("attr" in attribs and "feature" not in attribs["attr"]) or ("attr" in attribs and "feature" in attribs["attr"] and attribs["attr"]["feature"] != "rhyme"):
        attributes = {"feature": "rhyme", "word1": "", "word2": ""}
        mrsdrw = ["", "", "", "", ""]     #means, rhymes, sounds, describes, relates
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
            attributes["word" + words] = mrsdrw[1]                              # These if-statements handle the different rhyming statements and resulting responses from  Alexa. 
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
            return response(card_title, speech_output, "", should_end_session, "PlainText", {})
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
    return response(card_title, speech_output, "", should_end_session, "PlainText", attributes)

# This feature allows users to request a metronome to play at a specified BPM range. The files for the different tempos are stored
# on our Google Drive.

def metronome(request, attribs):
    attributes = attribs["attr"]
    bpm = ""
    if ("attr" not in attribs) or ("attr" in attribs and "feature" not in attribs["attr"]) or ("attr" in attribs and "feature" in attribs["attr"] and attribs["attr"]["feature"] != "metronome"):
        bpm = request['intent']['slots']['Rate']['value']
        attributes = {"feature": "metronome", "bpm": bpm}
    else:
        bpm = attribs["attr"]["bpm"]
    playbpm = str(int(bpm) - (int(bpm) % 5)) # this line handles users who give a value such as '67 bpm' and rounds it to the nearest interval of 5 (for example, '67' rounds to '70').
    card_title = "Metronome"
    speech_output = "<speak>" + bpm + " bpm <audio src=" + sssrc + "metronome/" + playbpm + "bpm.mp3' /> </speak>"
    should_end_session = False
    return response(card_title, speech_output, "", should_end_session, "SSML", attributes)

# This function allows users to request a single chord that Alexa will play back after repeating what she heard.

def one_chord(request, attribs):
    attributes = attribs["attr"]
    chord = ""
    if ("attr" not in attribs) or ("attr" in attribs and "feature" not in attribs["attr"]) or ("attr" in attribs and "feature" in attribs["attr"] and attribs["attr"]["feature"] != "one_chord"):
        chord = request['intent']['slots']['TheChord']['value']
        attributes = {"feature": "one_chord", "chord": chord}
    else:
        chord = attribs["attr"]["chord"]
    card_title = "Chord"                        # Below is the line where we construct Alexa's returned speech based and request for the specific chord file (the chord files are located in our Google Drive)
    speech_output = "<speak>" + chord + " chord <audio src=" + sssrc + "chords/" + chord.replace(" ", "+").replace(".", "").lower() + "+chord.mp3' /> </speak>"
    should_end_session = False
    return response(card_title, speech_output, "", should_end_session, "SSML", attributes)

# This function allows users to request chord progressions beginning with a root key (ex. "Give m a chord progression in key 'C'")

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
    for z in range(0, 5):                                                               # this line loops for 5 iterations, creating a chord progression with the 5 determined chords from our Google Drive storage
        speech_output += progs[str(z)][root].replace(" ", "-") + ", "
        theprog[z] = progs[str(z)][root].replace(" ", "+").replace(".", "").lower()
    for z in range(0, 5):
        speech_output += " <audio src=" + sssrc + "chords/" + theprog[z] + "+chord.mp3' />"
    speech_output += " </speak>"
    should_end_session = False
    return response(card_title, speech_output, "", should_end_session, "SSML", attributes)

# This is our help method, which allows uers to interact with vocal commands to find out which commands Alexa can respond to
# while in Echo Jam

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
        speech_output = "You can ask for a chord by saying, 'Give me an ay chord'"  # ay is written this way to aid in Alexa's pronunciation of the letter 'a'
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
    return response(card_title, speech_output, "", should_end_session, "PlainText", {})

# This is the generic help message, which offers four general statements that users can ask Alexa. These categories can be explored in more detail through the help commands defined above.

def getHelpMessage():
    return "You can ask me 'Give me a metronome at blank bpm' or 'Give me words that rhyme with blank'. You can also ask me 'Give me a chord progression in key blank' or 'Give me chord blank'."

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
