import argparse
import socket
import time
import threading
import urllib.request
import urllib.error
from queue import Queue


def get_address(arg):
    if try_to_connect() is not None:
        try:
            return socket.gethostbyname(arg)
        except:
            print("Unable to resolve domain name")
    else:
        return


def try_to_connect():
    try:
        return urllib.request.urlopen('http://google.com/', timeout=10)
    except:
        print("No connection")


# смотрим на открытые порты проверяя доступны ли они
def check_out_tcp_ports(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(3)
        try:
            sock.connect((address, port))
            print('TCP Port is open:', str(port))
        except:
            print('TCP Port is open close:', str(port))
            pass


# смотрим на открытые порты проверяя доступны ли они
def check_out_udp_ports(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(3)
        try:
            s.sendto(b'\x00' * 64, (address, port))
            data, _ = s.recvfrom(512)
            print("UDP Port Open:", str(port))
        except socket.error:
            print("UDP Port not responding = close:", str(port))
            pass


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tcp', action='store_true', help='TCP ports')
    parser.add_argument('-udp', action='store_true', help='UDP ports')
    parser.add_argument('host_name', type=str)
    parser.add_argument('-s', default=1, type=int, help='Ports along the lower border')
    parser.add_argument('-f', default=100, type=int, help='Ports along the upper border')

    args = parser.parse_args()
    if not args.tcp and not args.udp:
        args.tcp = args.udp = True
    return args


# многопоточно
def thread(scan, ip):
    socket.setdefaulttimeout(1)
    q = Queue()
    start_time = time.time()

    def threader():
        while True:
            port_num = q.get()
            scan(ip, port_num)
            q.task_done()

    for _ in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    for port in range(parse().s, parse().f):
        q.put(port)

    q.join()
    print('Time taken for {}'.format(scan.__name__), time.time() - start_time)


def decide():
    address = get_address(parse().host_name)
    if address != None:
        print('Starting scan on host: ', address)
        if parse().tcp:
            thread(check_out_tcp_ports, address)
        if parse().udp:
            thread(check_out_udp_ports, address)


if __name__ == "__main__":
    decide()
