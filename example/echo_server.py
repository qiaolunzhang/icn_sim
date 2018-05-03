import socket
import select

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), 9876))
server.listen(10)

inputs = [server]
running = 1

while running:
    inready, outready, excready = select.select(inputs, [], []);

    for s in inready:
        if s == server:
            client, address = server.accept()
            inready.append(client)
        else:
            data = s.recv(1024)
            if data:
                s.send(data)
            else:
                inputs.remove(s)
                s.close()
