
from vavabot_hedge_beta2_0 import Deribit, client_ID, client_secret
import time
from lists import list_monitor_log
import threading
global connect


with open('testnet_true_or_false_hedge.txt', 'r') as testnet_saved_tru_or_false1_file:
    testnet_saved_tru_or_false1_file_read = str(testnet_saved_tru_or_false1_file.read())
    testnet_saved_tru_or_false1 = testnet_saved_tru_or_false1_file_read

if 'False' in testnet_saved_tru_or_false1:
    test = False
else:
    test = True

connect = Deribit(test=test, only_public=False, client_ID=client_ID, client_secret=client_secret)

led = 'red'


def led_color():
    global led
    led_color1 = led
    return str(led_color1)


def connection():
    global connect
    global led
    while True:
        try:
            connect_set_heartbeat = connect.set_heartbeat()
            if connect_set_heartbeat == 'ok':
                list_monitor_log.append('connection ok')
                led = 'green'
                time.sleep(2)
                pass
            else:
                list_monitor_log.append('********** Offline - Connection ERROR **********')
                led = 'red'
                time.sleep(10)
                connect = Deribit(test=test, only_public=False, client_ID=client_ID, client_secret=client_secret)
        except Exception as e:
            led = 'red'
            time.sleep(10)
            list_monitor_log.append('********** Thread_connection - Connection ERROR ********** ' + str(e))
            pass


run_thread = threading.Thread(daemon=True, target=connection)
run_thread.start()
