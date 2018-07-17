# -*- coding: utf-8 -*-
import struct

def send_with_length(data, sock):
    length = len(data)
    message = struct.pack('>I', length) + data
    sock.send(message)
