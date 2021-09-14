from socket import *
import sys


def read_file(filename):
	f = open(filename)
	outputdata = f.read()
	f.close()
	return outputdata

def send(connection_socket, msg):
	size = len(msg)
	sent = connection_socket.send(msg.encode())
	print(msg, size, sent)

def handle_connection(connection_socket, addr):
	try:
		message = connection_socket.recv(4096)
		filename = message.split()[1]
		try:
			outputdata = read_file(filename[1:])
			#Send one HTTP header line into socket.
			print(filename[1:], len(outputdata))
			send(connection_socket, "HTTP/1.1 200 OK\r\n")
			send(connection_socket, ("Content-Length: " + str(len(outputdata))) + "\r\n")
			send(connection_socket, "\r\n")
			#Send the content of the requested file to the client
			send(connection_socket, outputdata)
		except IOError as error:
			print(error)
			# Send response message for file not found (404)
			send(connection_socket, "HTTP/1.1 404 File Not Found\r\n")

		#Close client socket
		connection_socket.close()
		print('Sent')
	except (ConnectionResetError, BrokenPipeError) as ex:
		print(ex)


def web_server(port=13331):
	server_socket = socket(AF_INET, SOCK_STREAM)

	#Prepare a server socket
	server_socket.bind(("", port))

	server_socket.listen()

	while True:
		#Establish the connection
		print('Ready to serve...')
		connection_socket, addr = server_socket.accept()
		handle_connection(connection_socket, addr)

	serverSocket.close()
	sys.exit()	# Terminate the program after sending the corresponding data


if __name__ == "__main__":
	web_server(13331)
