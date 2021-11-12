from socket import *
import os
import sys
import struct
import time
import select
import binascii
import statistics
# Should use stdev

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_RESPONSE = 0


def printICMP(txt, packet):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    # type = 0
    # cd = 0
    # chk = 0
    # id = 0
    # seq = 0
    # t = 0.0
    (type, cd, chk, id, seq, t) = struct.unpack("bbHHHd", packet)
    print(txt, len(packet), type, cd, chk, id, seq, t)


def checksum(string):
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


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = time.time() - startedSelect
        # print('.', whatReady[0])
        if whatReady[0] == []:  # Timeout
            print("Request timed out.")
            return None

        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        # Fetch the ICMP header from the IP packet
        # print("RESP: ", recPacket.hex('-'))

        (ver, ToS, l, id, flags) = struct.unpack("!BBHHH", recPacket[:8])
        # print(f"ver: {ver>>4}, IHL: {ver&0xF} ToS: {ToS}, len: {l}, id: {id}, flags: {flags}")

        (ttl, prot, chksum, src, dst) = struct.unpack("!BBH4s4s",
                                                      recPacket[8:20])
        # print(f"ttl: {ttl}, prot: {prot}, chk: {chksum}, src: {src}, dst: {dst}")

        (type, cd, chk, id, seq, t) = struct.unpack("BBHHHd", recPacket[20:])
        # print(f"type: {type}, cd: {cd}, chk: {chk}, id: {id}, seq: {seq}, time: {t}")

        endSelect = (howLongInSelect) * 1000
        src = f"{src[0]:d}.{src[1]:d}.{src[2]:d}.{src[3]:d}"
        print(f"Reply from {src}: bytes={l} time={endSelect:f}ms TTL={ttl}")

        return endSelect

        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    t = time.time()
    # print(t)
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

    #printICMP("REQ:", packet)

    # AF_INET address must be tuple, not str
    mySocket.sendto(packet, (destAddr, 1))

    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details: http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    try:
        dest = gethostbyname(host)
    except:
        print("Host not found: ", host)
        print()
        return ['0', '0.0', '0', '0.0']

    print("Pinging " + dest + " using Python:")
    print()
    # Calculate vars values and return them
    delays = []
    n = 4
    for i in range(0, n):
        delay = doOnePing(dest, timeout)
        if delay != None:
            delays.append(delay)
        time.sleep(1)  # one second

    print("")
    print("--- " + host + " stattistics ---")
    print(
        f"{n} packets transmitted, {len(delays)} packets received, {round(100*(n-len(delays))/n, 1)}% packet loss"
    )
    vars = [
        str(round(min(delays), 2)),
        str(round(statistics.mean(delays), 2)),
        str(round(max(delays), 2)),
        str(round(statistics.stdev(delays), 2))
    ]
    print(
        f"round-trip min/avg/max/stddev = {vars[0]}/{vars[1]}/{vars[2]}/{vars[3]} ms"
    )
    print()
    # Send ping requests to a server separated by approximately one second

    return vars


if __name__ == '__main__':
    ping("no.no.e")
    ping("google.co.il")
    ping("gaia.cs.umass.edu")
    ping("localhost")
    ping("yahoo.com")
