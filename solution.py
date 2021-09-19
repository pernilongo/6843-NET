
from socket import *

def assert_response(resp, code):
	#print(resp)
	if resp[:3] != code:
		print(code, 'reply not received from server.')


def send_cmd(cmd, client_socket):
	cmd = cmd + '\r\n'
	client_socket.send(cmd.encode())
	resp = client_socket.recv(1024).decode()
	return resp


def send_email(from_addr, to_addrs, msg, client_socket):
	assert_response(send_cmd('MAIL FROM: ' + from_addr, client_socket), '250')
	assert_response(send_cmd('RCPT TO: ' + to_addrs, client_socket), '250')
	assert_response(send_cmd('DATA', client_socket), '354')
	msg = msg + '\r\n'
	client_socket.send(msg.encode())
	assert_response(send_cmd('.', client_socket), '250')


def smtp_client(port=1025, mailserver='127.0.0.1'):

	# Choose a mail server (e.g. Google mail server) if you want to verify the script beyond GradeScope

	# Create socket called clientSocket and establish a TCP connection with mailserver and port

	client_socket = socket(AF_INET, SOCK_STREAM)
	client_socket.connect((mailserver, port))

	resp = client_socket.recv(1024).decode()
	assert_response(resp, '220')

	# Send HELO command and print server response.
	assert_response(send_cmd('HELO localhost', client_socket), '250')

	send_email('juan.rovirosa@nyu.edu', 'rp1912@nyu.edu', 'Testing SMTP client program', client_socket)

	# Send QUIT command and get server response.
	assert_response(send_cmd('QUIT', client_socket), '221')

	client_socket.close()


if __name__ == '__main__':
	smtp_client(1025, '127.0.0.1')
