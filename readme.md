This is a basic single chatroom app that stores the entire chat log to a local db.

This utilizes Socket.io and Flask to create the API for an angular frontend app located in
the ChatAppFE repository

#Installation

All that needs to be done is run
pip install -r requirements.txt

following that simply run python app.py

#Endpoints
The app utilizes 3 endpoints:

##/LoginUser
This will either login the user if it is existing, or create a new user if it does
not exist and then login the user. It takes UserName as a parameter

##/PostMessage
This Endpoint posts a new message, saving it to the database with the name, post time,
and username. It also broadcasts on the open sockets so all open connections will be
able to update their chat.

##/RetreiveMessages
This endpoint on page load retreives the latest 20 messages from the database to display.
Furthermore, it also takes an optional parameter to retreive the next 20 messages based on
the post time.
