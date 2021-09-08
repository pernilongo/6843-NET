from socket import *
import sys


def readFile(filename):
	f = open(filename)
	outputdata = f.read()
	f.close()
	return outputdata

def send(connectionSocket, msg):
	size = len(msg)
	sent = connectionSocket.send(msg.encode())
	print(msg, size, sent)

def handleConnection(connectionSocket, addr):
	try:
		message = connectionSocket.recv(4096)
		filename = message.split()[1]
		try:
			outputdata = readFile(filename[1:])
			#Send one HTTP header line into socket.
			print(filename[1:], len(outputdata))
			send(connectionSocket, "HTTP/1.1 200 OK\r\n")
			send(connectionSocket, ("Content-Length: " + str(len(outputdata))) + "\r\n")
			send(connectionSocket, "\r\n")
			#Send the content of the requested file to the client
			send(connectionSocket, outputdata)
		except IOError as error:
			print(error)
			# Send response message for file not found (404)
			send(connectionSocket, "HTTP/1.1 404 File Not Found\r\n")

		#Close client socket
		connectionSocket.close()
		print('Sent')
	except (ConnectionResetError, BrokenPipeError) as ex:
		print(ex)


def webServer(port=13331):
	serverSocket = socket(AF_INET, SOCK_STREAM)

	#Prepare a server socket
	serverSocket.bind(("", port))

	serverSocket.listen()

	while True:
		#Establish the connection
		print('Ready to serve...')
		connectionSocket, addr = serverSocket.accept()
		handleConnection(connectionSocket, addr)

	serverSocket.close()
	sys.exit()	# Terminate the program after sending the corresponding data


if __name__ == "__main__":
	webServer(13331)
