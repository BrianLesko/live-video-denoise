# Brian Lesko
# 5/28/2024

import streamlit as st
import cv2
import socket
import numpy as np
import Portkiller

# Kill previous ports if they are busy
def kill_ports():
    # Kill any running processes on the ports needed for this code
    ports = [8000, 8001]
    killer = Portkiller.PortKiller(ports)
    killer.kill_processes()
kill_ports()

# make the width video height and framerate variable via a slider
# vary compression methods

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FPS, 24) # FPS
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # compression method

# image placeholders
col1, col2, col3 = st.columns([1,8,1])
st.write("Original Video")
with col2: Image1 = st.empty()
st.write("Received Video")
with col2: Image2 = st.empty()
st.write("Denoised")
with col2: Image3 = st.empty()

# UDP server socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('Host:', host_ip)
server.bind((host_ip, 8000))  # Bind the socket to a specific address

# Server Sends to this client 
client_address = ('127.0.0.1', 8001)  # Replace with the client's IP address and port

# UDP client socket 
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_address = ('172.20.10.2', 8001)  # Replace with the client's IP address and port
client.bind(client_address)
print('Client is listening at', client_address)

data = b''  # initialize the data variable for received frames
while True:
    _, frame = camera.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    Image1.image(frame, use_column_width=True)

    # Send the image over UDP 
    chunk_size = 500  # Maximum UDP packet size
    for i in range(0, len(frame), chunk_size):
        chunk = frame[i:i+chunk_size]
        server.sendto(chunk, client_address)
    #print("frame sent", len(data))
    server.sendto(b'END', client_address)  # send an empty chunk to signal the end of the frame

    # bounce the signal a number of times for some additional noise? 
    # a ping is a bounce? can we hijack a ping to send our image

    # Receive the image over UDP
    chunk, addr = client.recvfrom(1000)
    if chunk == b'END':  # check for the "END" delimiter
        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        # show the image
        frame_resized = cv2.resize(frame, None, fx=6, fy=6)
        Image2.image(frame_resized, channels="BGR")
        data = b''
    else:
        data += chunk

    # denoise the image
    #Save the images to train a denoise neural net? 
    # first lets just see how we can balance framerate latency and noise
    # compare other sending methods too