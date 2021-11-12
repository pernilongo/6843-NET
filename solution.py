from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1

r = [['1', '12ms', '10.10.111.10', 'hop1.com'],
     ['2', '30ms', '10.10.112.10', 'hostname not returnable'],
     ['3', '*', 'Request timed out'],
     ['4', '5ms', '10.10.110.1', 'target-host.com']]

# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise


def checksum(string):
    # In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    ID = os.getpid() & 0xFFFF  # Return the current process i
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    t = time.time()
    data = struct.pack("d", t)
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)

    packet = header + data
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = [
    ]  #This is your list to use when iterating through each trace
    #tracelist2 = []  #This is your list to contain all traces
    icmp = getprotobyname("icmp")
    destAddr = gethostbyname(hostname)

    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):

            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            packet = build_packet()
            try:
                mySocket.sendto(packet, (destAddr, 0))
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []:  # Timeout
                    tracelist1.append([str(ttl), '*', "Request timed out."])
                    #You should add the list above to your all traces list
                    #tracelist2.append("* * * Request timed out.")
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect

                (ver, ToS, l, id,
                 flags) = struct.unpack("!BBHHH", recvPacket[:8])
                (_ttl, prot, chksum, src,
                 dst) = struct.unpack("!BBH4s4s", recvPacket[8:20])
                # print(recvPacket[20:].hex('-'))
                (type, cd, chk) = struct.unpack("BBH", recvPacket[20:24])
                ip_addr = f"{src[0]:d}.{src[1]:d}.{src[2]:d}.{src[3]:d}"

                if timeLeft <= 0:
                    tracelist1.append([str(ttl), '*', "Request timed out."])
                    #You should add the list above to your all traces list
                    #tracelist2.append("* * * Request timed out.")
            except timeout:
                continue

            else:
                (ver, ToS, l, id,
                 flags) = struct.unpack("!BBHHH", recvPacket[:8])
                (_ttl, prot, chksum, src,
                 dst) = struct.unpack("!BBH4s4s", recvPacket[8:20])
                # print(recvPacket[20:].hex('-'))
                (type, cd, chk) = struct.unpack("BBH", recvPacket[20:24])
                ip_addr = f"{src[0]:d}.{src[1]:d}.{src[2]:d}.{src[3]:d}"
                try:  #try to fetch the hostname
                    host_nm = gethostbyaddr(ip_addr)[0]
                except herror:  #if the host does not provide a hostname
                    host_nm = 'hostname not returnable'

                print(str(ttl), f'{round(howLongInSelect*1000)}ms',
                      f"{src[0]:d}.{src[1]:d}.{src[2]:d}.{src[3]:d}", host_nm,
                      type)
                if type == 11:
                    #You should add your responses to your lists here
                    tracelist1.append([
                        str(ttl), f'{round(howLongInSelect*1000)}ms',
                        f"{src[0]:d}.{src[1]:d}.{src[2]:d}.{src[3]:d}", host_nm
                    ])
                elif type == 3:
                    #You should add your responses to your lists here
                    tracelist1.append(['Destination Unreachable'])
                elif type == 0:
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    tracelist1.append([
                        str(ttl), f'{round(howLongInSelect*1000)}ms',
                        f"{src[0]:d}.{src[1]:d}.{src[2]:d}.{src[3]:d}", host_nm
                    ])
                    return tracelist1
                else:
                    #If there is an exception/error to your if statements, you should append that to your list here
                    tracelist1.append([])
                break
            finally:
                mySocket.close()


if __name__ == '__main__':
    list = get_route("13.107.21.200")
    print(list)
