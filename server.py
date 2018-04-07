# Member 1: Onimisi Ayira with ID: 1548437
# Member 2: Luke Patrick Dela Cruz with ID: 1504816
# Cmput 275 Wi18, Project


from flask import Flask, render_template
from flask_sockets import Sockets
from codegen import gen_password
# from pynput import Button, Controller
import pyautogui
import socket
import os

# initialize network objects
app = Flask(__name__)
sockets = Sockets(app)

# set up environment
received_coords = [[[-1, -1], False], False]
security_code = ""
# mouse = Controller()
sensitivity_factor = 4.5  # recommended to be in the range [3,5] for comfort
leap_bound = 20  # assertion that the cursor can't be moved more than 25 pixels
pyautogui.PAUSE = 0.01  # remove delay! can't be zero from hardware limitations
pyautogui.FAILSAFE = False  # allow for the corners to be reached by the cursor


@sockets.route('/move_mouse')
def echo_socket(ws):
    if not ws.closed:
        print("Android device acknowledged! Server IP accepted!")
        if ws.receive() != security_code:  # now we are ready to receive the security code
            print("Invalid security code! Please try again by hitting the >terminate< button.")
        else:
            print("Security code accepted!")
        global received_coords  # globalize the coordinate tracker
    while not ws.closed:
        message = ws.receive()
        if not message:
            break
        elif message == "C":
            pyautogui.click(button='left')
            # mouse.press(Button.left)
            received_coords[0][1] = False
        elif message == "RC":
            pyautogui.click(button='right')
            print('right!')
            received_coords[0][1] = False
        else:
            # print(received_coords)
            coords = message.split(",")
            new_x = int(coords[0].strip())
            new_y = int(coords[1].strip())
            if not received_coords[0][1]:
                received_coords[0][0][0] = new_x
                received_coords[0][0][1] = new_y
                received_coords[0][1] = True
            elif not received_coords[1]:
                curr_x, curr_y = pyautogui.position()
                trans_x = (new_x - received_coords[0][0][0])
                trans_y = (new_y - received_coords[0][0][1])
                if abs(trans_x) > leap_bound or abs(trans_y) > leap_bound:
                    received_coords[0][1] = False
                    continue
                trans_x *= sensitivity_factor
                trans_y *= sensitivity_factor
                pyautogui.moveTo(curr_x + trans_x , curr_y + trans_y)
                received_coords[0][1] = False
            else:
                print(message)
                received_coords[0][1] = False

    # or how to disconnect server from phone
    # such that they know the other was disconnected ???
    print("Android device terminated!")
    return

# @app.route('/')
# def hello():
#     return 'Hello World!'

if __name__ == "__main__":

    # set up command line and authentication
    security_code = gen_password(1)
    print("Enter this 5-character-case-sensitive security code:", security_code)
    serverIP = socket.gethostbyname(socket.gethostname())
    print("Use this as the server IP in the app:", serverIP)
    print("Use Ctrl + c to exit.")

    # run server from the random port of 5000
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
