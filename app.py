import os, json, requests
import sys, time

from flask import jsonify
from flask import Flask, request, redirect, url_for, flash

from flask_heroku import Heroku

app = Flask(__name__)
heroku = Heroku(app)


@app.route("/")
def index():
    return "Hello World"

@app.route('/webhook', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "ok", 200

@app.route('/webhook', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    base_url = "https://graph.facebook.com/v2.8/"
    access_token = os.environ["PAGE_ACCESS_TOKEN"]
    data = request.get_json()
    try:
        if data["object"] == "page":
            if data["entry"][0]["messaging"]:
                sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]
                # the facebook ID of the person sending you the message 
                message_text = data["entry"][0]["messaging"][0]["message"]["text"]  # the message's text
                print message_text
                message_data = get_message(message_text)
                send_message(sender_id, message_data)
    except Exception,e: 
        print str(e)

    return "ok", 200
def get_message(incoming_msg):
    if(incoming_msg.lower()=="what is alula"):
        message_data = "Alula is the first phone case to hold, protect, and dispense your brith control pills!  You simply put your pills into the case every month and our app will remind you everyday at the optimal time to take them!"
    elif(incoming_msg.lower()=="is alula protective for my phone?"):
        message_data = "Absolutely! Alula uses (enter materials here) those same materials are used in some of the best selling phone cases on the market."
    elif(incoming_msg.lower()=="how does it work?"):
        message_data = "Insert how to video"
    elif(incoming_msg.lower()=="will radiation from the phone affect my pills?"):
        message_data = "Radiation means heat! Heat would be bad for your pill but luckily we are using (enter material here) that will protect and insulate the pills from your iPhone's maximum operating temperature. If your phone overheats, we recommend removing the case to keep your pills as safe as possible!"
    elif(incoming_msg.lower()=="can I leave alula in the sun for extended amounts of time?"):
        message_data = "It is not recommended to leave your phone in the sun for extended amount of time as it acts as a conductor and will cause your phone to overheat. If your phone overheats, we recommend removing the case to keep your pills as safe as possible!"
    elif(incoming_msg.lower()=="how should I load it?"):
        message_data = "Load it by day as marked on your blister pack! There are letters to represent the day of the week, just match em up!"
    elif(incoming_msg.lower()=="what kind of birth control pills does it hold?"):
        message_data = "All kinds! Though the case pill plate dimensions are the appropriate depth for the average birth control pill regardless of brand."
    else:
        message_data = "Thanks for messaging us! We will get back to you shortly."
    return message_data
def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    r = requests.post("https://graph.facebook.com/v2.9/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    return "ok", 200

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
