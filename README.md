# Basic multiplayer game in python

This repo contains the code for a very basic multiplayer game built with `pygame`.

This game only supports 2 clients (the two players) and the interface only starts if there are two players connected.

The commands:
 - move with ASDW
 - shoot with E
 
## Basic logic
 
The server will listen for new clients -- that must connect t the server via socket.
 
Then, each client will constantly send information to the server about its intentions and the server will continuously update the game status (players' position, health, ...).

## How to play

Make sure you first run the server with

```
python ws_server.py
```

and then connect with at least two clients:

```
python ws_main.py
```

Ideally, you would deploy the server (and run the command `python ws_server.py` from a place that two clients, on two different computers, can reach.

## Testing

TBA

## Deploy on Heroku

To deploy on [Heroku](https://devcenter.heroku.com/articles/git), the first step is to create a new application from the web interface. Assume the app name is `example-app`, then

```
heroku git:remote -a example-app
```

Then, simply push to heroku:

```
git push heroku master
```

Try on heroku: change the `host` variable in the `ws_main.py` with the heroku URL of your app. Then, you should see the window popping up.

### Check on my heroku

My app is deployed at https://basic-multiplayer-gam.herokuapp.com/ . You can use this URL as value for `host` in the `ws_main.py`.
