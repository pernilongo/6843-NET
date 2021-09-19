
from socket import *

def assert_response(resp, code):
	print(resp)
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
	send_cmd(msg, client_socket)
	assert_response(send_cmd('.', client_socket), '250')


def smtp_client(port=1025, mailserver='127.0.0.1'):
	msg = "\r\n My message"
	endmsg = "\r\n.\r\n"

	# Choose a mail server (e.g. Google mail server) if you want to verify the script beyond GradeScope

	# Create socket called clientSocket and establish a TCP connection with mailserver and port

	# Fill in start
	# Fill in end

	resp = clientSocket.recv(1024).decode()
	assert_response(resp, '220')

	# Send HELO command and print server response.
	assert_response(send_cmd('HELO Alice', clientSocket), '250')

	send_email('juan.rovirosa@nyu.edu', 'juan.rovirosa@gmail.com', 'Testing SMTP client program', clientSocket)

	# Send QUIT command and get server response.
	assert_response(send_cmd('QUIT', clientSocket), '250')


if __name__ == '__main__':
	smtp_client(1025, '127.0.0.1')
