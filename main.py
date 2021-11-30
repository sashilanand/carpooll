#Welcome to my carpool app 
#Firstly, we will import the items necessary for the app
import flask
import json, os
from flask import render_template, request, session


app = flask.Flask(__name__)
app.secret_key = 'A0Zr98jRT#142DS4#sdfs4'
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)# This means that the browser can only return the cookie to the server over an encrypted connection, making it more secure

@app.route("/",methods=['GET', 'POST'])
def root():#This function returns the login page, which is the intial page the user will visit
    return render_template("login.html")

@app.route("/forgot",  methods=['GET', 'POST'])
def forgot():#This function returns the page which gives instructions on what to do when a user forgets their password
    return render_template("forgot.html")


@app.route("/driver", methods=['GET', 'POST'])
def driver():#This function returns the page which has the necessary fields a driver has to complete(if the user chooses to be a driver)
  return render_template("driver.html")



@app.route("/list_trips", methods=['GET', 'POST'])
def list_trips():#This function returns the list confirmed current trips which is the page the user will see once they login
  session["uname"] = request.form['username']#This allows me to store the username of the user, as it is an essential aspect of this app
  if os.path.exists("data.json"):
    # If there are new trips, load it into the saveddata dict
    with open("data.json") as datafile:
      saveddata = json.load(datafile)
  else:
    #If there aren't, start a new empty dict
    saveddata = {}

  return render_template("trips.html", form = saveddata)#saveddata is sent to trips.html as a variable named 'form' so that we can access it in the html file

@app.route("/final", methods=['GET', 'POST'])
def final():# This function returns the list of updated trips once the user has filled up the fields required if they were to driver
  dkeys = 0#dkeys will be used as the main key in order to differentiate each trip, and will be going in an incremental order
  if os.path.exists("data.json"):
    # If there are new trips, load it into the saveddata dict
    with open("data.json") as datafile:
      saveddata = json.load(datafile)
      d = {int(k) for k in saveddata.keys()}
      dkeys = sorted(d)[-1]

  else:
    #If there aren't, start a new empty dict
    saveddata = {}

  if request.method == "POST":
    # If new trips are entered and received via POST method
    newkey = dkeys + 1#The new key will be 1 more than the previous key
    #formObj = request.form.to_dict(flat=False)
    start = request.form["start"]# The starting location of the trip is received here
    end = request.form["end"]# The destination of the trip is received here
    meeting_time = request.form["meeting_time"]#The time at which the trip will begin is received here

    formObj={"start":start, "end":end, "meeting_time":meeting_time}#This is the order in which the information about the trip will be stored in the json data file, and is stored in a variable called formObj

    formObj["count"]= 0#This count refers to the number of passengers currently joined. Since cars can only have a limited amount of passengers, the users will not be able to join a trip once this limit is reached. As for my code, I have standardised it as a maximum of 3 passengers, meaning a vehicle capacity for 4 passengers. 

    #These 3 lines below create a value named p1,p2,p3, where p stands for passenger and when users click join for a particular trip, their username will be added to this list and will be stored in the dictionary
    formObj[ "p1"]= ""
    formObj[ "p2"]= ""
    formObj[ "p3"]= ""

    #The new key is assigned to the formObj variable
    saveddata[newkey] = formObj

  # This code stores the latest trip information by overwriting the old file
  with open("data.json", "w") as datafile:
    json.dump(saveddata, datafile)

  return render_template("final.html", form = saveddata)#Once again, saveddata is sent to final.html as a variable named 'form' so that we can access it in the html file

    
@app.errorhandler(404)
def not_found(error):# This function returns the error page which leads back to the login page 
  return render_template("404.html")


@app.route("/joined", methods=['GET', 'POST'])
def joined():# This function returns the confirmation page after a user has clicked join in any of the code
  if request.method == 'POST':
    tid = int(request.form['trip_id'])#the variable tid stores the key of whichever trip the user wants to join
    
    name = session.get("uname")#The variable name is assigned the username of the user
  if os.path.exists("data.json"):
    # If there is a file already created called data.json(which there should be as there should have already been some trips stored for the user to join them), load it into the saveddata dict
    with open("data.json") as datafile:
      saveddata = json.load(datafile)
      # load the into the saveddata dict
      finaldata = {}
      #The following for looop searches for the key which matches the trip-id which the user wanted to join, and then adds to the data the username of the passenger and increases the count of the passengers
      for key,value in saveddata.items():
        if int(key) == tid:
          finaldata =value
          if finaldata["count"] <=3 :# If there are less than or 2 passengers already(to ensure there is only a total of 3 passengers,
            finaldata["count"] +=1#add to the count of passengers
            if finaldata["count"] == 1:#If the count is at 1, add the username to the first passenger
              finaldata['p1']=name
            elif finaldata["count"] == 2:
              #If the count is at 2, add the username to the second passenger
              finaldata['p2']=name
            else:
              #Else, when the count is at 3(only viable possibility), add the username to the third passenger slot
              finaldata['p3']=name
          saveddata[key] = finaldata#replace the changed value for the respective key
          break
    with open("data.json", "w") as datafile:
      json.dump(saveddata, datafile)
      #Dump the new data back into the json file
  

  return render_template("joined.html", form = finaldata, id=key)
  #Return joined.html template, along with the finaldata and id as the trip id

app.run(host="0.0.0.0", port=8080, debug=True)
