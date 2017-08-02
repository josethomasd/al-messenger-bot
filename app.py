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
    q1= "what is alula?"
    q2 ="is alula protective for my phone?"
    q3 = "how does it work?"
    q4 = "will radiation from the phone affect my pills?"
    q5 = "can i leave alula in the sun for extended amounts of time?"
    q6 = "how should i load it?"
    q7 = "what kind of birth control pills does it hold?"
    q8 = "how will i know what day i am on?"
    q9 = "how many pills does it hold?"
    q10 = "is there an app?"
    q11 = "is this fda approved?"
    q12 = "where can i reach out to if i have further questions or want to get in contact with the my alula team?"
    q13 = "how much does alula cost?"
    q14 = "where can i buy alula?"
    if(incoming_msg.lower() in q1):
        message_data = "Alula is the first phone case to hold, protect, and dispense your brith control pills!  You simply put your pills into the case every month and our app will remind you everyday at the optimal time to take them!"
    elif(incoming_msg.lower() in q2):
        message_data = "Absolutely! Alula uses those same materials which are used in some of the best selling phone cases on the market."
    elif(incoming_msg.lower() in q3):
        message_data = "Visit your website http://www.myalula.com/ for more details."
    elif(incoming_msg.lower() in q4):
        message_data = "Radiation means heat! Heat would be bad for your pill but luckily we are using materials that will protect and insulate the pills from your iPhone's maximum operating temperature. If your phone overheats, we recommend removing the case to keep your pills as safe as possible!"
    elif(incoming_msg.lower() in q5):
        message_data = "It is not recommended to leave your phone in the sun for extended amount of time as it acts as a conductor and will cause your phone to overheat. If your phone overheats, we recommend removing the case to keep your pills as safe as possible!"
    elif(incoming_msg.lower() in q6):
        message_data = "Load it by day as marked on your blister pack! There are letters to represent the day of the week, just match em up!"
    elif(incoming_msg.lower() in q7):
        message_data = "All kinds! Though the case pill plate dimensions are the appropriate depth for the average birth control pill regardless of brand."
    elif(incoming_msg.lower() in q8):
        message_data = "You should download the alula app! It will help you stay up to date not only on when to take your pill but what day you're on and how many are left in alula! If you are unsure, feel free to open alula to double check!"
    elif(incoming_msg.lower() in q9):
        message_data = "21! Sorry for those of you who like your sugar pills, but the app will keep you on track and you can feel free to still take them or reload alula! If you take 28 days worth of true birth control pills we recommend reloading alula with the final week and then restarting the process after your menstrual cycle."
    elif(incoming_msg.lower() in q10):
        message_data = "Hell yeah there is! It is the my alula app and it is available on the app store.  We recommend downloading the app as it will help you track your progress, keep you on time, and make sure you're up to date!"
    elif(incoming_msg.lower() in q11):
        message_data = "Pill cases are considered a class I medical device and do not need approved by the FDA as long as they meet industry standards as far as keeping it air-tight and out of direct sunlight, which we have."
    elif(incoming_msg.lower() in q12):
        message_data = '''You can reach out directly on our website on the "contact us" page, via email at info@myalula.com'''
    elif(incoming_msg.lower() in q13):
        message_data = "Right now we are pricing alula at $35 in efforts to cover start-up costs, shipping costs, and production costs. As it gains in popularity and more alula cases are sold we will be looking forward to reducing that price to make it more affordable."
    elif(incoming_msg.lower() in q14):
        message_data = "Right now we are holding a pre-sale Indiegogo launch which you can place your order on, and after that has reached its conclusion and we begin manufacturing we will begin pre-orders via our e-commerce website www.myalula.com, and once they go on sale officially we will be operating online on our website and as an amazon store."
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
