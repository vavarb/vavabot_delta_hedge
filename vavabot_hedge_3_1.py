from PyQt5.QtWidgets import QInputDialog, QLineEdit
from gui_hedge import *
from connection_hedge import *
from websocket import create_connection
from datetime import datetime
import json
import hmac
import hashlib
import time
global index_greeks_print_on_off
global strategy_on_off
global list_monitor_log
global greeks_value_dict
global hedge_on_off
global connect
global counter_send_order
global sender_rate_dict
global password_dict
global counter_send_order_for_function


# Classe de Sinais.
class Sinais(QtCore.QObject):
    # Elementos.
    textedit_instruments_saved_signal = QtCore.pyqtSignal(str)
    ui_signal1 = QtCore.pyqtSignal(dict)  # ['object_signal': , 'action_signal': , 'info': ]
    ui_signal2 = QtCore.pyqtSignal(str)
    ui_signal3 = QtCore.pyqtSignal(dict)
    set_version_and_icon_signal = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)


sinal = Sinais()  # Instância da Classe Sinais.
delay_delay = 0
delay = 0


class CredentialsSaved:
    def __init__(self):
        self.self = self

    @staticmethod
    def api_secret_saved():
        import os
        import base64
        from cryptography.fernet import Fernet, InvalidToken, InvalidSignature
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from lists import password_dict
        global password_dict

        password1 = str(password_dict['pwd'])

        if os.path.isfile('api-key_hedge.txt') is False:
            with open('api-key_hedge.txt', 'a') as api_key_save_file:
                api_key_save_file.write(str('<Type your Deribit Key>'))
            api_secret_saved_file_read = str('<Type your Deribit Key>')
        else:
            with open('api-key_hedge.txt', 'r') as file:
                if '<Type your Deribit Key>' in str(file.read()):
                    file_read = str('<Type your Deribit Key>')
                else:
                    file_read = 'True'
            if file_read == 'True':
                salt = b'\x90"\x90J\r\xa6\x08\xb6_\xbdfEd\x1cDE'
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=390000,
                )

                key = base64.urlsafe_b64encode(kdf.derive(str(password1).encode('utf-8')))
                f = Fernet(key)

                with open('api-key_hedge.txt', 'rb') as enc_file:
                    encrypted = enc_file.read()
                try:
                    decrypted = f.decrypt(encrypted).decode('utf-8')
                    api_secret_saved_file_read = str(decrypted)
                except InvalidToken or InvalidSignature:
                    api_secret_saved_file_read = str('<Type your Deribit Key>')
                finally:
                    pass
            else:
                api_secret_saved_file_read = str('<Type your Deribit Key>')

        return api_secret_saved_file_read

    @staticmethod
    def secret_key_saved():
        import os
        import base64
        from cryptography.fernet import Fernet, InvalidToken, InvalidSignature
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from lists import password_dict
        global password_dict

        password2 = str(password_dict['pwd'])

        if os.path.isfile('secret-key_hedge.txt') is False:
            with open('secret-key_hedge.txt', 'a') as secret_key_saved_file:
                secret_key_saved_file.write(str('<Type your Deribit Secret Key>'))
            secret_key_saved_file_read = str('<Type your Deribit Secret Key>')
        else:
            with open('secret-key_hedge.txt', 'r') as file:
                if '<Type your Deribit Secret Key>' in str(file.read()):
                    file_read = str('<Type your Deribit Secret Key>')
                else:
                    file_read = 'True'
            if file_read == 'True':
                salt = b'\x90"\x90J\r\xa6\x08\xb6_\xbdfEd\x1cDE'
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=390000,
                )

                key = base64.urlsafe_b64encode(kdf.derive(str(password2).encode('utf-8')))
                f = Fernet(key)

                with open('secret-key_hedge.txt', 'rb') as enc_file:
                    encrypted = enc_file.read()
                try:
                    decrypted = f.decrypt(encrypted).decode('utf-8')
                    secret_key_saved_file_read = str(decrypted)
                except InvalidToken or InvalidSignature:
                    secret_key_saved_file_read = str('<Type your Deribit Secret Key>')
                finally:
                    pass
            else:
                secret_key_saved_file_read = str('<Type your Deribit Secret Key>')

        return secret_key_saved_file_read

    @staticmethod
    def testnet_saved_tru_or_false():
        from lists import list_monitor_log

        with open('testnet_true_or_false_hedge.txt', 'r') as testnet_saved_tru_or_false_file:
            testnet_saved_tru_or_false_file_read = str(testnet_saved_tru_or_false_file.read())
        if testnet_saved_tru_or_false_file_read == 'True':
            list_monitor_log.append('*** TEST Account ***')
            return True
        elif testnet_saved_tru_or_false_file_read == 'False':
            list_monitor_log.append('*** REAL Account ***')
            connect.logwriter('*** REAL Account ***')
            return False
        else:
            list_monitor_log.append('***** ERROR in testnet_saved_tru_or_false *****')
            connect.logwriter('***** ERROR in testnet_saved_tru_or_false *****')

    @staticmethod
    def url():
        from lists import list_monitor_log

        if CredentialsSaved.testnet_saved_tru_or_false() is True:
            list_monitor_log.append('*** URL: ' + 'wss://test.deribit.com/ws/api/v2' + ' ***')
            return 'wss://test.deribit.com/ws/api/v2'
        elif CredentialsSaved.testnet_saved_tru_or_false() is False:
            list_monitor_log.append('*** URL: ' + 'wss://deribit.com/ws/api/v2' + ' ***')
            return 'wss://deribit.com/ws/api/v2'
        else:
            list_monitor_log.append('***** URL ERROR in testnet True or False *****')


class Deribit:
    def __init__(self, client_id=None, client_secret=None, wss_url=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.wss_url = wss_url

        self._auth(client_id=client_id, wss_url=wss_url, client_secret=client_secret)

    # noinspection PyMethodMayBeStatic
    def logwriter(self, msg):
        from lists import list_monitor_log

        filename = 'log_hedge.log'

        try:
            out = datetime.now().strftime("\n[%Y/%m/%d, %H:%M:%S] ") + str(msg)
            list_monitor_log.append(str(msg))
            with open(filename, 'a') as logwriter_file:
                logwriter_file.write(str(out))

        except Exception as er:
            from connection_hedge import connect
            from lists import list_monitor_log
            global counter_send_order_for_function

            with open(filename, 'a') as logwriter_file:
                logwriter_file.write(str(datetime.now().strftime("\n[%Y/%m/%d, %H:%M:%S] ")) +
                                     '***** ERROR except in logwriter: ' +
                                     str(er) + str(msg) +
                                     '_' + str(counter_send_order_for_function) + ' *****')
            list_monitor_log.append('***** ERROR except in logwriter: ' + str(er) + ' *****')
        finally:
            pass

    def _auth(self, client_id=None, wss_url=None, client_secret=None):
        self.client_id = client_id
        self.wss_url = wss_url
        self.client_secret = client_secret

        from lists import list_monitor_log
        global sender_rate_dict
        global delay_delay
        global counter_send_order_for_function

        counter_send_order_for_function = 0

        sender_rate_dict = dict()
        sender_rate_dict['time_1'] = time.time()
        sender_rate_dict['counter_send_order_for_sender_rate'] = 1

        timestamp = round(datetime.now().timestamp() * 1000)
        nonce = "abcd"
        data = ""
        signature = hmac.new(
            bytes(client_secret, "latin-1"),
            msg=bytes('{}\n{}\n{}'.format(timestamp, nonce, data), "latin-1"),
            digestmod=hashlib.sha256
        ).hexdigest().lower()

        try:
            self._WSS = create_connection(wss_url, enable_multithread=True)
            msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "public/auth",
                "params": {
                    "grant_type": "client_signature",
                    "client_id": client_id,
                    "timestamp": timestamp,
                    "signature": signature,
                    "nonce": nonce,
                    "data": data
                }
            }
            self.logwriter('Auth OK\n############')
            list_monitor_log.append('Auth OK\n############')
            list_monitor_log.append('identified')
            return self._sender(msg)

        except Exception as er:
            from lists import list_monitor_log
            list_monitor_log.append('***** auth ERROR:' + ' error: ' + str(er) + ' *****')
            self.logwriter('***** auth ERROR:' + ' error: ' + str(er) + ' *****')

    # noinspection PyMethodMayBeStatic
    def sender_rate(self, counter_send_order_for_sender_rate, time_now):
        global sender_rate_dict

        if float(time_now - sender_rate_dict['time_1']) >= 120:
            delta_counter_send_order = float(
                counter_send_order_for_sender_rate) - float(sender_rate_dict['counter_send_order_for_sender_rate'])
            delta_time_for_sender_rate = float(time_now - sender_rate_dict['time_1'])
            rate_sender_orders = float(delta_counter_send_order) / float(delta_time_for_sender_rate)

            sender_rate_dict['time_1'] = time_now
            sender_rate_dict['counter_send_order_for_sender_rate'] = float(counter_send_order_for_sender_rate)

            return round(rate_sender_orders, 2)
        else:
            return False

    def _delay(self, sender_rate_rate_):
        global delay_delay
        from lists import list_monitor_log

        if sender_rate_rate_ is not False:
            orders_per_second_ = float(ConfigAndInstrumentsSaved().orders_rate_saved())

            list_monitor_log.append('*** Check Sent Orders Rate ***')
            self.logwriter(
                '*** Sent Orders Rate: ' + str(sender_rate_rate_) + ' Orders/Second ***')
            if float(sender_rate_rate_) > float(orders_per_second_):
                delay_delay = round(delay_delay + ((1 / orders_per_second_) - (1 / sender_rate_rate_)), 2)
                list_monitor_log.append('*** Sent Orders Rate Checked: > ' + str(orders_per_second_) +
                                        ' Orders/second ***')
                self.logwriter('*** Setup New Delay to send order: ' + str(delay_delay) + ' seconds ***')
            else:
                list_monitor_log.append('*** Sent Orders Rate Checked: < ' + str(orders_per_second_) +
                                        ' Orders/second ***')
                if delay_delay == 0:
                    self.logwriter('*** Setup Delay to send order Unmodified ***')
                else:
                    if round(delay_delay - ((1 / sender_rate_rate_) - (1 / orders_per_second_)), 2) > 0:
                        delay_delay = round(delay_delay - ((1 / sender_rate_rate_) - (1 / orders_per_second_)), 2)
                        self.logwriter('*** Setup New Delay to send order: ' + str(delay_delay) + ' seconds ***')
                    else:
                        delay_delay = 0
                        self.logwriter('*** Setup New Delay to send order: ' + str(delay_delay) + ' seconds ***')
            if delay_delay < 0:
                return 0
            else:
                return float(delay_delay)
        else:
            if delay_delay < 0:
                return 0
            else:
                return float(delay_delay)

    @staticmethod
    def counter_send_order_function():
        global counter_send_order_for_function

        counter_send_order_for_function = counter_send_order_for_function + 1
        return counter_send_order_for_function

    def _sender(self, msg):
        global delay
        from connection_hedge import led_color

        counter_send_order = self.counter_send_order_function()
        msg_id_before_counter = msg['id']
        msg['id'] = int(str(msg['id']) + str(counter_send_order))

        try:
            if str(msg['method']) == 'public/set_heartbeat':
                self.logwriter(str(msg['method']) + '(* Connection Test *)' + ' ID: ' + str(msg['id']))

            elif str(msg['method']) == "private/buy" or str(msg['method']) == "private/sell":
                if str(msg_id_before_counter) == "8" or str(msg_id_before_counter) == "9":
                    instrument_name = str(msg['params']['instrument_name'])
                    instrument_direction = str(msg['method']) + ' ' + str(msg['params']['type'])
                    order_amount_instrument = str(msg['params']['amount'])
                    instrument_price = str(msg['params']['price'])
                    self.logwriter(str(instrument_name) +
                                   ': ' + str(instrument_direction) +
                                   ' ' + str(order_amount_instrument) +
                                   ' at ' + str(instrument_price) +
                                   ' ID: ' + str(msg['id']) +
                                   '_' + str(counter_send_order))
                else:
                    pass

            else:
                self.logwriter(str(msg['method']) + ' ID: ' + str(msg['id']) + '_' + str(counter_send_order))

            self._WSS.send(json.dumps(msg))
            out = json.loads(self._WSS.recv())

            delay = self._delay(sender_rate_rate_=self.sender_rate(
                counter_send_order_for_sender_rate=counter_send_order, time_now=time.time()))

            if delay > 0 and (msg_id_before_counter != 8 and msg_id_before_counter != 9 and
                              msg_id_before_counter != 14):
                time.sleep(delay)
            else:
                pass

            if 'error' in str(out) or \
                    (msg['id'] != out['id'] and msg_id_before_counter != 1 and led_color() == 'green' and
                     msg_id_before_counter != 8 and msg_id_before_counter != 9):
                if msg['id'] != out['id']:
                    self.logwriter(' ***** ERROR: msgSentID != msgOutID *****\n***** msgSent: ' + str(msg) +
                                   ' *****\n***** msgOut: ' + str(out) + ' *****\n*** msgSent ID: ' + str(msg['id']) +
                                   '_' + str(counter_send_order) + ' ***''\n*** msgOut ID: ' + str(out['id']) + ' ***')
                    time.sleep(10)
                    out = {'error': {'code': 'error'}}
                else:
                    self.logwriter(' ***** _sender ERROR: msgOut: ' + str(out) + '*****\n ***msgSent ID: ' +
                                   str(msg['id']) + '_' + str(counter_send_order) + ' ***')

                if str(out['error']['code']) == '13009' or str(out['error']['code']) == '13004':
                    self.logwriter('***** _sender msg - VERIFY CREDENTIALS - Type your Deribit API and Secret Keys '
                                   '*****')
                    if str(msg_id_before_counter) == '19':
                        return float(0)
                    elif str(msg_id_before_counter) == '25':
                        return 0
                    else:
                        return out['error']

                elif str(msg_id_before_counter) == '19':
                    return float(0)

                elif str(msg_id_before_counter) == '25':
                    return 0

                else:
                    return out['error']
            else:
                return out['result']

        except Exception as er:
            from connection_hedge import connection_thread, run_thread
            import threading

            self.logwriter('***** _sender ERROR: ' + str(er) + ' msgSent ID: ' + str(msg['id']) +
                           '_' + str(counter_send_order) + ' *****')
            if run_thread.is_alive() is True:
                pass
            else:
                connection_thread()
        finally:
            pass

    def get_instruments(self, currency):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "public/get_instruments",
                "params": {
                    "currency": currency,
                    # "kind": "future",
                    "expired": False
                }
            }
        return self._sender(msg)

    def index_price(self, currency):
        msg = \
            {
                "jsonrpc": "2.0",
                "method": "public/get_index_price",
                "id": 3,
                "params": {
                    "index_name": currency
                }
             }
        return self._sender(msg)

    def set_heartbeat(self):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "public/set_heartbeat",
                "params": {
                    "interval": 60
                }
            }
        return self._sender(msg)

    def disable_heartbeat(self):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "public/disable_heartbeat",
                "params": {

                }
            }
        return self._sender(msg)

    def get_position(self, instrument_name=None):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "private/get_position",
                "params": {
                    "instrument_name": instrument_name
                }
            }
        return self._sender(msg)

    def get_order_book(self, instrument_name=None):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "public/get_order_book",
                "params": {
                    "instrument_name": instrument_name
                }
            }
        return self._sender(msg)

    def buy_limit(self, currency, amount, price):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "private/buy",
                "params": {
                    "instrument_name": currency,
                    "amount": amount,
                    "type": "limit",
                    "price": price
                }
            }
        return self._sender(msg)

    def sell_limit(self, currency, amount, price):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "private/sell",
                "params": {
                    "instrument_name": currency,
                    "amount": amount,
                    "type": "limit",
                    "price": price
                }
            }
        return self._sender(msg)

    def buy_pos_only(self, currency, amount, price):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "private/buy",
                "params": {
                    "instrument_name": currency,
                    "amount": amount,
                    "price": price,
                    "post_only": True
                }
            }
        return self._sender(msg)

    def sell_pos_only(self, currency, amount, price):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 11,
                "method": "private/sell",
                "params": {
                    "instrument_name": currency,
                    "amount": amount,
                    "price": price,
                    "post_only": True
                }
            }
        return self._sender(msg)

    def buy_market(self, currency, amount):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 12,
                "method": "private/buy",
                "params": {
                    "instrument_name": currency,
                    "amount": amount,
                    "type": "market"
                }
            }
        return self._sender(msg)

    def sell_market(self, currency, amount):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 13,
                "method": "private/sell",
                "params": {
                    "instrument_name": currency,
                    "amount": amount,
                    "type": "market"
                }
            }
        return self._sender(msg)

    def cancel_all(self):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 14,
                "method": "private/cancel_all",
                "params": {

                }
            }
        return self._sender(msg)

    def get_instruments_future(self, currency):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 15,
                "method": "public/get_instruments",
                "params": {
                    "currency": currency,
                    "kind": "future",
                    "expired": False
                }
            }
        return self._sender(msg)

    def get_book_summary_by_instrument(self, instrument_name):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 16,
                "method": "public/get_book_summary_by_instrument",
                "params": {
                    "instrument_name": instrument_name
                }
            }
        return self._sender(msg)

    def close_position(self, instrument_name):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 17,
                "method": "private/close_position",
                "params": {
                    "instrument_name": instrument_name,
                    "type": "market"
                }
            }
        return self._sender(msg)

    def get_account_summary(self, currency=None):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 18,
                "method": "private/get_account_summary",
                "params": {
                    "currency": currency,
                    "extended": True
                }
            }
        return self._sender(msg)

    def hello(self):
        msg = \
            {
                "jsonrpc": "2.0",
                "id": 26,
                "method": "public/hello",
                "params": {
                    "client_name": "VavaBot - Options Strategy",
                    "client_version": "7.5.1"
                }
            }
        return self._sender(msg)

    def test(self):
        global delay

        counter_send_order1 = self.counter_send_order_function()

        if delay > 0:
            time.sleep(delay)
        else:
            pass

        msg1 = \
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "public/test",
                "params": {
                }
            }

        try:
            self._WSS.send(json.dumps(msg1))
            out1 = json.loads(self._WSS.recv())
        except AttributeError as er1:
            self.logwriter(
                str('********** Connection Test Error: ' + str(er1) + ' **********\n msgSent ID: ' +
                    str(msg1['id']) + '_' + str(counter_send_order1)))
            return 'error'

        self.logwriter(
            str(msg1['method']) + '(* Connection Test *)' + ' ID: ' + str(msg1['id']) + '_' + str(
                counter_send_order1))

        if 'error' in str(out1):
            self.logwriter('**************** Connection Test ERROR *****************\n*** msgOUT: ' + str(out1) +
                           '*** \n*** msgOut ID: ' + str(out1['id']) + '_' + str(counter_send_order1) + ' ***')
            return 'error'
        else:
            if out1['id'] == 4:
                return out1['result']
            elif (isinstance(out1['id'], int) or isinstance(out1['id'], float)) and out1['id'] != 4:
                return 'version'
            else:
                return out1['result']


class ConfigAndInstrumentsSaved:
    def __init__(self):
        self.self = self
        self.instrument_number = None

    @staticmethod
    def orders_rate_saved():
        from lists import list_monitor_log
        import os

        if os.path.isfile('send_orders_rate.txt') is False:
            with open('send_orders_rate.txt', 'a') as send_orders_rate_file:
                send_orders_rate_file.write('5')
        else:
            pass

        with open('send_orders_rate.txt', 'r') as send_orders_rate_file:
            send_orders_rate_file_read = str(send_orders_rate_file.read())

        list_monitor_log.append('*** Order/Second Setup: ' + str(send_orders_rate_file_read) + ' ***')

        return round(float(send_orders_rate_file_read), 2)

    @staticmethod
    def orders_rate_saved2():
        from connection_hedge import connect
        import os

        if os.path.isfile('send_orders_rate.txt') is False:
            with open('send_orders_rate.txt', 'a') as send_orders_rate_file:
                send_orders_rate_file.write('5')
        else:
            pass

        with open('send_orders_rate.txt', 'r') as send_orders_rate_file:
            send_orders_rate_file_read = str(send_orders_rate_file.read())

        ui.lineEdit_orders_rate.setText(str(send_orders_rate_file_read))
        connect.logwriter('*** Order/Second Setup: ' + str(send_orders_rate_file_read) + ' ***')

    @staticmethod
    def instruments_check():
        with open('instrument_hedge.txt', 'r') as instruments_check_file:
            return str(instruments_check_file.read())

    @staticmethod
    def config_check():
        with open('targets_hedge.txt', 'r') as config_check_file:
            return str(config_check_file.read())

    def instrument_name_construction_from_file(self, instrument_number=None):
        file_open = 'instrument_hedge.txt'
        self.instrument_number = instrument_number

        instrument_number_adjusted_to_list = (int(instrument_number) - 1)

        # open file instruments

        with open(file_open, 'r') as file_instruments:
            lines_file_instruments = file_instruments.readlines()  # file instruments.txt ==> lines
            # Instrument
            list_line_instrument = lines_file_instruments[instrument_number_adjusted_to_list].split()  # line ==> list
            instrument_name = str(list_line_instrument[2])
            return instrument_name

    def instrument_available(self, instrument_number=None):
        from lists import list_monitor_log
        from connection_hedge import connect

        self.instrument_number = instrument_number

        instrument_name = ConfigAndInstrumentsSaved().instrument_name_construction_from_file(
            instrument_number=int(instrument_number))

        currency = str
        if 'BTC' in instrument_name:
            currency = 'BTC'
        elif 'ETH' in instrument_name:
            currency = 'ETH'
        else:
            list_monitor_log.append('********** Instrument currency Syntax ERROR *********')
        try:
            a10 = connect.get_instruments(currency)
            list_instrument_name = []
            for i in a10:
                list_instrument_name.append(i['instrument_name'])
            if instrument_name in list_instrument_name:
                list_instrument_name.clear()
                return 'instrument available'
            else:
                list_instrument_name.clear()
                return 'instrument NO available'
        except Exception as er:
            sinal.textedit_instruments_saved_signal.emit('*** ERROR - Instrument NO Checked ***')
            list_monitor_log.append('*** ERROR - Instrument NO Checked ***' + str(er))
            pass
        finally:
            pass

    @staticmethod
    def hedge_method():
        with open('targets_hedge.txt', 'r') as hedge_method:
            hedge_method_file = hedge_method.readlines()
            list_hedge_method_file = hedge_method_file[0].split()
            hedge_method_ = str(list_hedge_method_file[1])
            return str(hedge_method_)

    @staticmethod
    def hedge_target():
        with open('targets_hedge.txt', 'r') as a_file:
            lines_a_file = a_file.readlines()
            list_lines_a_file = lines_a_file[1].split()
            set_entry_position_in = str(list_lines_a_file[2])
            return float(set_entry_position_in)

    @staticmethod
    def superior_limit():
        with open('targets_hedge.txt', 'r') as a_file:
            lines_a_file = a_file.readlines()
            list_lines_a_file = lines_a_file[2].split()
            superior_limit = str(list_lines_a_file[2])
            return float(superior_limit)

    @staticmethod
    def inferior_limit():
        with open('targets_hedge.txt', 'r') as a_file:
            lines_a_file = a_file.readlines()
            list_lines_a_file = lines_a_file[3].split()
            inferior_limit = str(list_lines_a_file[2])
            return float(inferior_limit)

    @staticmethod
    def remove_log_hedge_log_if_bigger_500kb_when_open_app():
        import os
        from lists import list_monitor_log

        try:
            if os.path.isfile('log_hedge_backup.log') is True:
                if float(os.path.getsize('log_hedge_backup.log')) > 8000000:
                    os.unlink('log_hedge_backup.log')
                    list_monitor_log.append('*** Deleted log_hedge_backup.log (>8MB). ***')
                else:
                    list_monitor_log.append('*** Len log_hedge_backup.log < 8MB. ***')
            else:
                pass

            if os.path.isfile('log_hedge.log') is True:
                if float(os.path.getsize('log_hedge.log')) > 500000:
                    with open('log_hedge_backup.log', 'a') as file_backup:
                        with open('log_hedge.log', 'r') as log_file:
                            file_backup.writelines(log_file)
                            list_monitor_log.append('*** Appended log_hedge.log into log_hedge_backup.log ***')
                    os.unlink('log_hedge.log')
                    list_monitor_log.append('*** Deleted and Created log_hedge.log ***')
                else:
                    list_monitor_log.append('*** Len log_hedge.log < 0.5MB. ***')
            else:
                list_monitor_log.append('*** Created log_hedge.log ***')

        except Exception as er:
            from connection_hedge import connect
            list_monitor_log.append('***** ERROR in remove_log_hedge_log_if_bigger_500kb_when_open_app(): ' +
                                    str(er) + '. Error Code 758 *****')
            connect.logwriter('***** ERROR in remove_llog_hedge_log_if_bigger_500kb_when_open_app(): ' +
                              str(er) + '. Error Code 760 *****')


# noinspection PyShadowingNames
def credentials(ui):
    def message_box_reboot():
        import sys

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('If you update\nAPI key and secret key\nyou will need restart bot')
        msg.setWindowTitle('*** WARNING ***')
        msg.addButton('Ok', msg.AcceptRole)
        msg.addButton('Cancel', msg.RejectRole)
        pass
        if msg.exec_() == msg.Rejected:
            api_key_save()  # ok clicked
            time.sleep(1)
            sys.exit()
        else:
            pass  # cancel clicked

    def message_box_reboot1():
        if CredentialsSaved.testnet_saved_tru_or_false() == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('You need\nSet Test or Real Account')
            msg.setWindowTitle('INFO')
            msg.exec_()
            pass
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('Test or Real Account\nIs Correct?')
            msg.setWindowTitle('*** WARNING ***')
            msg.addButton('Yes', msg.AcceptRole)
            msg.addButton('No', msg.RejectRole)
            pass
            if msg.exec_() == msg.Rejected:
                message_box_reboot()  # ok clicked
            else:
                pass  # cancel clicked

    def message_box_reboot2():
        import sys
        if CredentialsSaved.testnet_saved_tru_or_false() is True:
            pass
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('Dou you want\nUpdate Account? ')
            msg.setWindowTitle('*** WARNING ***')
            msg.addButton('Yes', msg.AcceptRole)
            msg.addButton('No', msg.RejectRole)
            pass
            if msg.exec_() == msg.Rejected:
                testnet_true_save()  # ok clicked

                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Dou you want\nUpdate APIs? ')
                msg.setWindowTitle('*** WARNING ***')
                msg.addButton('Yes', msg.AcceptRole)
                msg.addButton('No', msg.RejectRole)
                pass
                if msg.exec_() == msg.Rejected:
                    message_box_reboot()  # ok clicked
                else:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setText('You need\nRestart bot')
                    msg.setWindowTitle('INFO')
                    msg.exec_()
                    pass  # cancel clicked
                    sys.exit()
            else:
                if CredentialsSaved.testnet_saved_tru_or_false() is True:
                    ui.radioButton_testnet_true.setChecked(True)
                    ui.radioButton_2_testnet_false.setChecked(False)
                elif CredentialsSaved.testnet_saved_tru_or_false() is False:
                    ui.radioButton_testnet_true.setChecked(False)
                    ui.radioButton_2_testnet_false.setChecked(True)
                else:
                    ui.radioButton_testnet_true.setChecked(False)
                    ui.radioButton_2_testnet_false.setChecked(False)
                    pass  # cancel clicked

    def message_box_reboot3():
        import sys
        if CredentialsSaved.testnet_saved_tru_or_false() is False:
            pass
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('Dou you want\nUpdate Account? ')
            msg.setWindowTitle('*** WARNING ***')
            msg.addButton('Yes', msg.AcceptRole)
            msg.addButton('No', msg.RejectRole)
            pass
            if msg.exec_() == msg.Rejected:
                testnet_false_save()  # ok clicked

                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Dou you want\nUpdate APIs? ')
                msg.setWindowTitle('*** WARNING ***')
                msg.addButton('Yes', msg.AcceptRole)
                msg.addButton('No', msg.RejectRole)
                pass
                if msg.exec_() == msg.Rejected:
                    message_box_reboot()  # ok clicked
                else:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setText('You need\nRestart bot')
                    msg.setWindowTitle('INFO')
                    msg.exec_()
                    pass  # cancel clicked
                    sys.exit()
            else:
                if CredentialsSaved.testnet_saved_tru_or_false() is True:
                    ui.radioButton_testnet_true.setChecked(True)
                    ui.radioButton_2_testnet_false.setChecked(False)
                elif CredentialsSaved.testnet_saved_tru_or_false() is False:
                    ui.radioButton_testnet_true.setChecked(False)
                    ui.radioButton_2_testnet_false.setChecked(True)
                else:
                    ui.radioButton_testnet_true.setChecked(False)
                    ui.radioButton_2_testnet_false.setChecked(False)
                    pass  # cancel clicked

    def api_key_saved_print():
        text = str(CredentialsSaved.api_secret_saved())

        if text == '<Type your Deribit Key>':
            ui.lineEdit_api_key_saved.setText(text)
        else:
            text1 = text[:3]
            list_text1 = list(text1)
            if len(text) >= 4:
                text2 = text[3:]
                list_text2 = list(text2)
                for i in list_text2:
                    list_text2[list_text2.index(i)] = '*'
                list_text1.extend(list_text2)
                text3 = "".join(list_text1)
                ui.lineEdit_api_key_saved.setText(text3)
            else:
                for i in list_text1:
                    list_text1[list_text1.index(i)] = '*'
                text3 = "".join(list_text1)
                ui.lineEdit_api_key_saved.setText(text3)

    def secret_key_saved_print():
        text = str(CredentialsSaved.secret_key_saved())

        if text == '<Type your Deribit Secret Key>':
            ui.lineEdit_api_secret_saved.setText(text)
        else:
            text1 = text[:3]
            list_text1 = list(text1)
            if len(text) >= 4:
                text2 = text[3:]
                list_text2 = list(text2)
                for i in list_text2:
                    list_text2[list_text2.index(i)] = '*'
                list_text1.extend(list_text2)
                text3 = "".join(list_text1)
                ui.lineEdit_api_secret_saved.setText(text3)
            else:
                for i in list_text1:
                    list_text1[list_text1.index(i)] = '*'
                text3 = "".join(list_text1)
                ui.lineEdit_api_secret_saved.setText(text3)

    def testnet_true_or_false_saved_print():
        testnet_true_or_false_saved_print_file = CredentialsSaved.testnet_saved_tru_or_false()
        if testnet_true_or_false_saved_print_file is True:
            ui.lineEdit_testenet_true_or_false_satatus.setText('Test Account')
            ui.radioButton_testnet_true.setChecked(True)
            ui.radioButton_2_testnet_false.setChecked(False)
        elif testnet_true_or_false_saved_print_file is False:
            ui.lineEdit_testenet_true_or_false_satatus.setText('Real Account')
            ui.radioButton_testnet_true.setChecked(False)
            ui.radioButton_2_testnet_false.setChecked(True)
        else:
            ui.lineEdit_testenet_true_or_false_satatus.setText('SET Account')
            ui.radioButton_testnet_true.setChecked(False)
            ui.radioButton_2_testnet_false.setChecked(False)
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('You need\nSet Test or Real Account')
            msg.setWindowTitle('*** Warning ***')
            msg.exec_()
            pass

    def api_key_save():
        import base64
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from lists import password_dict
        global password_dict

        password3 = str(password_dict['pwd'])

        salt = b'\x90"\x90J\r\xa6\x08\xb6_\xbdfEd\x1cDE'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(str(password3).encode('utf-8')))
        f = Fernet(key)
        original = str(ui.lineEdit_api_key_new.text()).encode('utf-8')
        token = f.encrypt(original)

        with open('api-key_hedge.txt', 'wb') as encrypted_file:
            encrypted_file.write(token)

        secret_key_save()
        api_key_saved_print()

    def secret_key_save():
        import base64
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from lists import password_dict
        global password_dict

        password4 = str(password_dict['pwd'])

        salt = b'\x90"\x90J\r\xa6\x08\xb6_\xbdfEd\x1cDE'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(str(password4).encode('utf-8')))
        f = Fernet(key)
        original = str(ui.lineEdit_api_secret_new.text()).encode('utf-8')
        token = f.encrypt(original)

        with open('secret-key_hedge.txt', 'wb') as encrypted_file:
            encrypted_file.write(token)

        secret_key_saved_print()

    def testnet_true_save():
        with open('testnet_true_or_false_hedge.txt', 'w') as testnet_true_save_file:
            testnet_true_save_file.write('True')
        testnet_true_or_false_saved_print()

    def testnet_false_save():
        with open('testnet_true_or_false_hedge.txt', 'w') as testnet_false_save_file:
            testnet_false_save_file.write('False')
        testnet_true_or_false_saved_print()

    def need_password_counter_smaller_three():
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('You need to create a password\nto recover API credentials')
        msg.setWindowTitle('WARNING')
        msg.exec_()
        pass
        time.sleep(0.5)

    def invalid_password():
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Invalid Password')
        msg.setWindowTitle('INFO')
        msg.exec_()
        pass
        time.sleep(0.5)

    def invalid_password_counter_bigger_three():
        import os
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Credentials will be reset\nAnd APP will be close')
        msg.setWindowTitle('INFO')
        msg.exec_()
        pass
        os.unlink('api-key_hedge.txt')
        os.unlink('secret-key_hedge.txt')
        time.sleep(1)
        sys.exit()

    def message_connection_only_public():
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Only public methods\nwill be executed')
        msg.setWindowTitle('INFO')
        msg.exec_()
        pass

    def message_box_password_input():
        from connection_hedge import connection1
        import os
        from lists import password_dict
        global password_dict

        if os.path.isfile('secret-key_hedge.txt') is True:
            with open('secret-key_hedge.txt', 'r') as file1:
                sks = file1.read()
        else:
            sks = '<Type your Deribit Secret Key>'

        if os.path.isfile('api-key_hedge.txt') is True:
            with open('api-key_hedge.txt', 'r') as file2:
                a_s_saved = file2.read()
        else:
            a_s_saved = '<Type your Deribit Key>'

        if '<Type your Deribit Key>' in str(a_s_saved) or '<Type your Deribit Secret Key>' in str(sks):
            connection1()
            api_key_saved_print()
            secret_key_saved_print()
            testnet_true_or_false_saved_print()
        else:
            password_input = 'User'
            invalid_password_counter = 0
            need_password_counter = 0

            while password_input == 'User':
                le = QLineEdit()
                le.setText('Password')

                text, ok = QInputDialog().getText(le, "WARNING",
                                                  "Password to recovey API Credentials:", le.Password)
                # QDir().home().dirName())
                if ok is False:
                    password_input = str(password_dict['pwd'])
                    message_connection_only_public()
                    connection1()
                    api_key_saved_print()
                    secret_key_saved_print()
                    testnet_true_or_false_saved_print()
                if ok:
                    le.setText(str(text))
                    if str(text) == '':
                        if need_password_counter <= 3:
                            need_password_counter = need_password_counter + 1
                            need_password_counter_smaller_three()
                        else:
                            invalid_password_counter_bigger_three()
                    else:
                        import base64
                        from cryptography.fernet import Fernet, InvalidToken, InvalidSignature
                        from cryptography.hazmat.primitives import hashes
                        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

                        password_dict['pwd'] = str(text)

                        salt = b'\x90"\x90J\r\xa6\x08\xb6_\xbdfEd\x1cDE'
                        kdf = PBKDF2HMAC(
                            algorithm=hashes.SHA256(),
                            length=32,
                            salt=salt,
                            iterations=390000,
                        )

                        key = base64.urlsafe_b64encode(kdf.derive(str(password_dict['pwd']).encode('utf-8')))
                        f = Fernet(key)

                        with open('api-key_hedge.txt', 'rb') as enc_file:
                            encrypted1 = enc_file.read()
                        with open('secret-key_hedge.txt', 'rb') as enc_file:
                            encrypted2 = enc_file.read()

                        if invalid_password_counter <= 3:
                            try:
                                f.decrypt(encrypted1).decode('utf-8')
                                f.decrypt(encrypted2).decode('utf-8')
                            except InvalidToken or InvalidSignature:
                                invalid_password_counter = invalid_password_counter + 1
                                invalid_password()
                            else:
                                password_input = str(password_dict['pwd'])
                                connection1()
                                api_key_saved_print()
                                secret_key_saved_print()
                                testnet_true_or_false_saved_print()
                            finally:
                                pass
                        else:
                            invalid_password_counter_bigger_three()

    message_box_password_input()
    ui.pushButton_submit_new_credintals.clicked.connect(message_box_reboot1)
    ui.radioButton_testnet_true.clicked.connect(message_box_reboot2)
    ui.radioButton_2_testnet_false.clicked.connect(message_box_reboot3)


# noinspection PyShadowingNames
def config(ui):
    def save_orders_rate():
        from connection_hedge import connect
        import os

        try:
            orders_per_second_from_line_edit = round(float(str.replace(ui.lineEdit_orders_rate.text(), ',', '.')), 2)
        except ValueError:
            orders_per_second_from_line_edit = float(5)
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('Order/Second must be > 0')
            msg.setWindowTitle('***** ERROR *****')
            msg.exec_()

        if orders_per_second_from_line_edit > 0:
            orders_per_second = round(float(orders_per_second_from_line_edit), 2)

        else:
            orders_per_second = round(float(5), 2)
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('Order/Second must be > 0')
            msg.setWindowTitle('***** ERROR *****')
            msg.exec_()

        if os.path.isfile('send_orders_rate.txt') is False:
            with open('send_orders_rate.txt', 'a') as send_orders_rate_file:
                send_orders_rate_file.write(str(orders_per_second))
        else:
            with open('send_orders_rate.txt', 'w') as send_orders_rate_file:
                send_orders_rate_file.write(str(orders_per_second))

        with open('send_orders_rate.txt', 'r') as send_orders_rate_file:
            send_orders_rate_file_read = str(send_orders_rate_file.read())

        ui.lineEdit_orders_rate.setText(str(send_orders_rate_file_read))
        connect.logwriter('*** Order/Second Setup: ' + str(send_orders_rate_file_read) + ' ***')

    def set_version_and_icon_signal_receive():
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "VavaBot - Delta Hedge 3.1"))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".../icon_noctuline_wall_e_eve.ico"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)

        ui.pushButton_submit_new_instruments_2.setText(_translate("MainWindow", "UPDATE Setup"))
        ui.label_10.setText(_translate("MainWindow", "Setup:"))

        # Set text License
        try:
            with open('LICENSE.txt', 'r') as license_txt_file:
                license_txt = license_txt_file.read()
                ui.textEdit_license.append(license_txt)
        except FileNotFoundError:
            license_txt = 'License file NOT found\n\nCopyright 2022 Vavarb vavarb@protonmail.com ' \
                          'https://github.com/vavarb\n\nVisit: http://www.apache.org/licenses/LICENSE-2.0'
            ui.textEdit_license.append(license_txt)
        finally:
            pass

        # Set text Contact us
        contact_text = 'Contact us: vavarb@protonmail.com\n' \
                       'Source Code: https://github.com/vavarb/vavabot_options_strategy'
        ui.textEdit_contact_us.append(contact_text)

        # Set text Buy me a coffee
        buy_me_a_coffee_text = 'Buy me a Coffe ☕? If you have found anything useful and you want to support me, ' \
                               'feel free to do it with ₿ITCOIN or Lightning Network! And many thanks in advance. ' \
                               '😁\n\n' \
                               '>>> Lightning Network Adress: vavarb@bipa.app\n' \
                               '>>> ₿ITCOIN Adress: 36RbpSZVNiSxK69kNMH3WHFJqAhfXppU5N'
        ui.textEdit_buy_me_a_coffee.append(buy_me_a_coffee_text)

    def set_date():
        date_now_instrument = QtCore.QDate.currentDate()
        ui.lineEdit_maturity_instrumet1.setDate(date_now_instrument.addDays(-1))

    def textedit_instruments_saved_signal(info):
        ui.textEdit_instruments_saved.setText(str(info))

    def instruments_saved_print_and_check_available():
        from lists import list_monitor_log
        info = str(ConfigAndInstrumentsSaved.instruments_check())
        sinal.textedit_instruments_saved_signal.emit(info)
        try:
            instument_available_for_config = ConfigAndInstrumentsSaved().instrument_available(instrument_number=1)
            if instument_available_for_config == 'instrument available':
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Instrument Syntax OK')
                msg.setWindowTitle('INFO')
                msg.exec_()
                pass
            elif instument_available_for_config == 'instrument NO available':
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Instrument Syntax ERROR')
                msg.setWindowTitle('***** ERROR *****')
                msg.exec_()
                pass
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Instrument Syntax no checked')
                msg.setWindowTitle('***** ERROR *****')
                msg.exec_()
                pass
        except Exception as er:
            list_monitor_log.append(str(er))
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('Instrument Syntax Check ERROR')
            msg.setWindowTitle('***** ERROR *****')
            msg.exec_()
            pass

    def ui_signal3(info):
        ui.textEdit_instruments_saved_2.setText(info['textEdit_instruments_saved_2'])
        ui.comboBox_value_given_4.setCurrentText(str(info['comboBox_value_given_4']))
        ui.comboBox_value_given_4.setEnabled(False)
        ui.label_6.setText(str(info['label_6']))
        ui.label_11.setText(str(info['label_11']))

    def config_saved_print():
        info1 = str(ConfigAndInstrumentsSaved.config_check())

        if 'BTC' in str(ConfigAndInstrumentsSaved().instrument_name_construction_from_file(instrument_number=1)):
            btc_or_eth = ' BTC'
        else:
            btc_or_eth = ' ETH'

        info2 = str(
                ConfigAndInstrumentsSaved().hedge_method()) + ': ' + str(
                ConfigAndInstrumentsSaved().superior_limit()) + str(
                btc_or_eth)

        info3 = str(
                str(ConfigAndInstrumentsSaved().hedge_method()) + ': ' +
                str(ConfigAndInstrumentsSaved().inferior_limit()) + str(btc_or_eth)
            )

        info4 = {
            'textEdit_instruments_saved_2': str(
                info1), 'comboBox_value_given_4': 'Delta TOTAL ', 'label_6': str(
                info2), 'label_11': str(info3)
        }

        sinal.ui_signal3.emit(info4)

    def instruments_save():
        from lists import list_monitor_log
        try:
            date_now_instrument = QtCore.QDate.currentDate()
            if ui.lineEdit_currency_instrumet1.currentText() == 'Set BTC or ETH:' or \
                (ui.lineEdit_maturity_instrumet1.date() == date_now_instrument.addDays(-1) and
                    ui.checkBox_perpetual_1.checkState() == 0):
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('All fields are required - ERROR')
                msg.setWindowTitle('***** ERROR *****')
                msg.exec_()
                pass

            elif (ui.lineEdit_currency_instrumet1.currentText() == 'BTC' or
                  ui.lineEdit_currency_instrumet1.currentText() == 'ETH'):
                if ui.checkBox_perpetual_1.isChecked():
                    instrument1_to_save = str(
                        'Instrument 1: ' +
                        str(ui.lineEdit_currency_instrumet1.currentText()) +
                        '-PERPETUAL'
                    )
                else:
                    instrument1_to_save = str(
                        'Instrument 1: ' +
                        str(ui.lineEdit_currency_instrumet1.currentText()) + '-' +
                        str(ui.lineEdit_maturity_instrumet1.text().upper())
                    )
                    pass

                with open('instrument_hedge.txt', 'w') as instruments_save_file:
                    instruments_save_file.write(str(instrument1_to_save))
                instruments_saved_print_and_check_available()
            else:
                pass
        except Exception as er:
            list_monitor_log.append(str(er))
            instruments_save_file.close()

        ui.pushButton_submit_new_credintals.setEnabled(False)
        ui.radioButton_testnet_true.setEnabled(False)
        ui.radioButton_2_testnet_false.setEnabled(False)

    def config_save():
        from lists import list_monitor_log
        try:
            if ui.comboBox_value_given_4.currentText() == 'Set Hedge Method':
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('All fields Setup are required - ERROR')
                msg.setWindowTitle('***** ERROR *****')
                msg.exec_()
                pass

            else:
                try:
                    if float(str.replace(str(
                            ui.lineEdit_currency_exchange_rate_for_upper_and_lower1_2.text()), ',', '.')) == 0 or \
                            float(str.replace(str(
                                ui.lineEdit_currency_exchange_rate_upper1_2.text()), ',', '.')) == 0 or \
                            float(str.replace(str(
                                ui.lineEdit_currency_exchange_rate_lower1_3.text()), ',', '.')) == 0:
                        pass
                    else:
                        pass

                    with open('targets_hedge.txt', 'w') as config_save_file:
                        config_save_file.write(
                            str(ui.comboBox_value_given_4.currentText()) +
                            '\n Hedge Target: ' + str.replace(str(
                                ui.lineEdit_currency_exchange_rate_for_upper_and_lower1_2.text()), ',', '.') +
                            '\n SUPERIOR Limit: ' + str(
                                float(str.replace(str(
                                    ui.lineEdit_currency_exchange_rate_for_upper_and_lower1_2.text()), ',', '.')) +
                                abs(float(str.replace(str(
                                    ui.lineEdit_currency_exchange_rate_upper1_2.text()), ',', '.')))) +
                            '\n INFERIOR Limit: ' + str(
                                float(str.replace(str(
                                    ui.lineEdit_currency_exchange_rate_for_upper_and_lower1_2.text()), ',', '.')) -
                                abs(float(str.replace(str(
                                    ui.lineEdit_currency_exchange_rate_lower1_3.text()), ',', '.'))))
                        )

                except ValueError:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setText('Only numbers are accepted')
                    msg.setWindowTitle('*** ERROR ***')
                    msg.exec_()
                    pass

                config_saved_print()

        except Exception as er:
            list_monitor_log.append(str(er))
            config_save_file.close()

    sinal.set_version_and_icon_signal.connect(set_version_and_icon_signal_receive)
    sinal.set_version_and_icon_signal.emit()
    set_date()
    sinal.textedit_instruments_saved_signal.connect(textedit_instruments_saved_signal)
    sinal.ui_signal3.connect(ui_signal3)
    instruments_saved_print_and_check_available()
    config_saved_print()
    ui.pushButton_submit_new_instruments.clicked.connect(instruments_save)
    ui.pushButton_submit_new_instruments_2.clicked.connect(config_save)
    ConfigAndInstrumentsSaved().orders_rate_saved2()
    ui.pushButton_orders_rate.clicked.connect(save_orders_rate)


# noinspection PyShadowingNames
def summary(ui):
    def message_box_instrument_syntax_error():
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Instrument syntax ERROR')
        msg.setWindowTitle('*** WARNING ***')
        msg.exec_()
        pass

    def instrument_currency_saved():
        with open('instrument_hedge.txt', 'r') as instrument_currency_file:
            if 'BTC' in instrument_currency_file.read():
                return 'BTC'
            elif 'ETH' in instrument_currency_file.read():
                return 'ETH'
            else:
                return 'ERROR'

    def total_account_print():
        try:
            from connection_hedge import connect
            if instrument_currency_saved() == 'ERROR':
                message_box_instrument_syntax_error()
            else:
                if CredentialsSaved().api_secret_saved() == '<Type your Deribit Key>' or \
                        CredentialsSaved.secret_key_saved() == '<Type your Deribit Secret Key>':
                    unauthorized_token_code_13009_or_13004 = True
                else:
                    unauthorized_token_code_13009_or_13004 = False

                if unauthorized_token_code_13009_or_13004 is False:
                    currency = str(instrument_currency_saved())
                    summary_total = connect.get_account_summary(currency=currency)

                    instrument_name = str(
                        ConfigAndInstrumentsSaved().instrument_name_construction_from_file(instrument_number=1))
                    position_instrument_hedge = connect.get_position(instrument_name=instrument_name)

                    sinal.ui_signal1.emit({
                        'object_signal': 'textEdit_balance', 'info': summary_total, 'info2': position_instrument_hedge,
                        'info3': str(currency)})
                else:
                    sinal.ui_signal1.emit({
                        'object_signal': 'textEdit_balance_unauthorized_token_code_13009_or_13004', 'info': ''})
                    pass

        except Exception as er:
            ui.textEdit_balance.append('********** ERROR: ' + str(er) + ' **********')
            list_monitor_log.append(' ********** ERROR - total acount print **********' + str(er))
            pass
        finally:
            pass

    def options_account_print():
        try:
            from connection_hedge import connect
            from lists import list_monitor_log
            if instrument_currency_saved() == 'ERROR':
                message_box_instrument_syntax_error()
            else:
                if CredentialsSaved().api_secret_saved() == '<Type your Deribit Key>' or \
                        CredentialsSaved.secret_key_saved() == '<Type your Deribit Secret Key>':
                    unauthorized_token_code_13009_or_13004 = True
                else:
                    unauthorized_token_code_13009_or_13004 = False

                if unauthorized_token_code_13009_or_13004 is False:
                    currency = str(instrument_currency_saved())
                    summary_total = connect.get_account_summary(currency=currency)

                    sinal.ui_signal1.emit({
                        'object_signal': 'textEdit_balance_after', 'info': summary_total})
                else:
                    pass

        except Exception as er:
            from lists import list_monitor_log
            ui.textEdit_balance_after.append('********** ERROR: ' + str(er) + ' **********')
            list_monitor_log.append('********** ERROR - options account print **********' + str(er))
            pass
        finally:
            pass

    ui.pushButton_update_balance.clicked.connect(total_account_print)  # tem signal na função
    ui.pushButton_update_balance.clicked.connect(options_account_print)  # tem signal na função
    total_account_print()  # tem signal na função
    options_account_print()  # tem signal na função


# noinspection PyShadowingNames
def run_hedge(ui):
    from lists import list_monitor_log

    def ui_signal1(info):
        try:
            object_signal = str(info['object_signal'])

            if object_signal == 'textEdit_balance':
                summary_total = info['info']

                instrument_position_hedge = info['info2']
                instrument_position_hedge_size = float(instrument_position_hedge['size'])
                instrument_position_hedge_size_currency = float(instrument_position_hedge['size_currency'])

                currency = str(info['info3'])

                ui.textEdit_balance.clear()
                ui.textEdit_balance.append('Account: ' +
                                           str(summary_total['system_name'])
                                           )
                ui.textEdit_balance.append(str(summary_total['type']).upper() +
                                           ': ' +
                                           str(summary_total['username'])
                                           )
                ui.textEdit_balance.append('Currency: ' +
                                           str(summary_total['currency'])
                                           )

                portfolio_margining_enabled = summary_total['portfolio_margining_enabled']
                if portfolio_margining_enabled is True:
                    ui.textEdit_balance.append('Portfolio Margining: ENABLED')
                elif portfolio_margining_enabled is False:
                    ui.textEdit_balance.append('Portfolio Margining: DISABLED')
                else:
                    pass

                ui.textEdit_balance.append('Balance: ' +
                                           str(round(summary_total['balance'], 4))
                                           )
                ui.textEdit_balance.append('DELTA TOTAL: ' +
                                           str(round(summary_total['delta_total'], 4))
                                           )
                ui.textEdit_balance.append('Projected DELTA TOTAL: ' +
                                           str(round(summary_total['projected_delta_total'], 4))
                                           )
                ui.textEdit_balance.append('Available funds: ' +
                                           str(round(summary_total['available_funds'], 4))
                                           )
                ui.textEdit_balance.append('Equity: ' +
                                           str(round(summary_total['equity'], 4))
                                           )
                ui.textEdit_balance.append('Total PL: ' +
                                           str(round(summary_total['total_pl'], 4))
                                           )
                ui.textEdit_balance.append('Session RPL: ' +
                                           str(round(summary_total['session_rpl'], 4))
                                           )
                ui.textEdit_balance.append('Session UPL: ' +
                                           str(round(summary_total['session_upl'], 4))
                                           )
                ui.textEdit_balance.append('Futures PL: ' +
                                           str(round(summary_total['futures_pl'], 4))
                                           )
                ui.textEdit_balance.append('Futures Session RPL: ' +
                                           str(round(summary_total['futures_session_rpl'], 4))
                                           )
                ui.textEdit_balance.append('Futures Session UPL: ' +
                                           str(round(summary_total['futures_session_upl'], 4))
                                           )
                ui.textEdit_balance.append('Margin Balance: ' +
                                           str(round(summary_total['margin_balance'], 4))
                                           )
                ui.textEdit_balance.append('Initial Margin: ' +
                                           str(round(summary_total['initial_margin'], 4))
                                           )
                ui.textEdit_balance.append('Maintenance Margin: ' +
                                           str(round(summary_total['maintenance_margin'], 4))
                                           )
                ui.textEdit_balance.append('Projected Maintenance Margin: ' +
                                           str(round(summary_total['projected_maintenance_margin'], 4))
                                           )
                ui.textEdit_balance.append('Size: ' +
                                           str(round(instrument_position_hedge_size, 2)) +
                                           'USD'
                                           )
                ui.textEdit_balance.append('Size Currency: ' +
                                           str(round(instrument_position_hedge_size_currency, 8)) +
                                           str(currency)
                                           )

            elif object_signal == 'textEdit_balance_unauthorized_token_code_13009_or_13004':
                ui.textEdit_balance.clear()
                ui.textEdit_balance.append('***************')
                ui.textEdit_balance.append('Verify Credentials')
                ui.textEdit_balance.append('Type your Deribit')
                ui.textEdit_balance.append('API and')
                ui.textEdit_balance.append('SECRET Keys')
                ui.textEdit_balance.append('***************')

            elif object_signal == 'textEdit_balance_after':
                summary_total = info['info']
                ui.textEdit_balance_after.clear()
                ui.textEdit_balance_after.append('Account: ' +
                                                 str(summary_total['system_name'])
                                                 )
                ui.textEdit_balance_after.append(str(summary_total['type']).upper() +
                                                 ': ' +
                                                 str(summary_total['username'])
                                                 )
                ui.textEdit_balance_after.append('Currency: ' +
                                                 str(summary_total['currency'])
                                                 )
                ui.textEdit_balance_after.append('Options PL: ' +
                                                 str(round(summary_total['options_pl'], 4))
                                                 )
                ui.textEdit_balance_after.append('Options Session RPL: ' +
                                                 str(round(summary_total['options_session_rpl'], 4))
                                                 )
                ui.textEdit_balance_after.append('Options Session UPL: ' +
                                                 str(round(summary_total['options_session_upl'], 4))
                                                 )
                ui.textEdit_balance_after.append('Options DELTA: ' +
                                                 str(round(summary_total['options_delta'], 4))
                                                 )
                ui.textEdit_balance_after.append('Options GAMMA: ' +
                                                 str(round(summary_total['options_gamma'], 4))
                                                 )
                ui.textEdit_balance_after.append('Options THETA: ' +
                                                 str(round(summary_total['options_theta'], 4))
                                                 )
                ui.textEdit_balance_after.append('Options VEGA: ' +
                                                 str(round(summary_total['options_vega'], 4))
                                                 )

            elif object_signal == 'Run_Tab':
                summary_total = info['info']

                ui.lineEdit_24.setText(
                    str(round(summary_total['delta_total'], 4))
                )

                ui.lineEdit_26.setText(
                    str(round(summary_total['options_delta'], 4))
                )

                ui.lineEdit_25.setText(
                    str(round(summary_total['options_theta'], 4))
                )

                ui.lineEdit_27.setText(
                    str(round(summary_total['options_gamma'], 4))
                )

                ui.lineEdit_28.setText(
                    str(round(summary_total['options_vega'], 4))
                )

                ui.lineEdit_29.setText(
                    str(summary_total['currency'])
                )

                ui.lineEdit_31.setText(
                    str(round(summary_total['balance'], 4))
                )

                ui.lineEdit_30.setText(
                    str(round(summary_total['maintenance_margin'], 4))
                )

                ui.lineEdit_32.setText(
                    str(round(summary_total['total_pl'], 4))
                )

                ui.lineEdit_33.setText(
                    str(round(summary_total['futures_pl'], 4))
                )

                ui.lineEdit_34.setText(
                    str(round(summary_total['options_pl'], 4))
                )

            elif object_signal == 'lineEdit_24_btc_index':
                b = str(info['info'])
                ui.lineEdit_24_btc_index.setText(b)

            elif object_signal == 'lineEdit_58':
                ui.lineEdit_58.setText(str(info['info']))

            elif object_signal == 'textEdit_monitor':
                msg1 = str(info['msg'])
                msg2 = msg1.replace('\n', '')
                ui.textEdit_monitor.append(str(msg2))

            elif object_signal == 'Hedge_Stopped':
                from connection_hedge import connect
                # New
                ui.pushButton_submit_new_credintals.setEnabled(True)
                ui.radioButton_testnet_true.setEnabled(True)
                ui.radioButton_2_testnet_false.setEnabled(True)
                ui.pushButton_submit_new_instruments.setEnabled(True)
                ui.pushButton_submit_new_instruments_2.setEnabled(True)
                # old:
                red_icon = "./red_led_icon.png"
                ui.label_34.setPixmap(QtGui.QPixmap(red_icon))
                ui.pushButton_stop_arbitrage.setEnabled(False)
                ui.pushButton_start_trading.setEnabled(True)
                thread_btc_index_print()

                connect.logwriter('***** Hedge_Stopped *****')

                ui.lineEdit_orders_rate.setEnabled(True)
                ui.pushButton_orders_rate.setEnabled(True)

            elif object_signal == 'led_connection':
                led_color1 = str(info['led_color'])
                if led_color1 == 'green':
                    green_icon = "./green_led_icon.png"
                    ui.label_29.setPixmap(QtGui.QPixmap(green_icon))
                elif led_color1 == 'red':
                    red_icon = "./red_led_icon.png"
                    ui.label_29.setPixmap(QtGui.QPixmap(red_icon))
                else:
                    pass

            elif object_signal == 'pushbutton_2_click_signal':
                ui.textEdit_monitor.clear()

            elif object_signal == 'btc_index_print':
                ui.pushButton.setEnabled(False)
                ui.pushButton.setText('Chronometer\nEnabled')
                ui.pushButton_stop_arbitrage.setEnabled(False)
                ui.pushButton_start_trading.setEnabled(True)

                red_icon = "./red_led_icon.png"
                ui.label_34.setPixmap(QtGui.QPixmap(red_icon))

            elif object_signal == 'Hedge_Started':
                ui.pushButton_submit_new_credintals.setEnabled(False)
                ui.radioButton_testnet_true.setEnabled(False)
                ui.radioButton_2_testnet_false.setEnabled(False)
                ui.pushButton_submit_new_instruments.setEnabled(False)
                ui.pushButton_submit_new_instruments_2.setEnabled(False)
                ui.pushButton_start_trading.setEnabled(False)
                ui.pushButton_stop_arbitrage.setEnabled(True)
                ui.pushButton_start_trading.setEnabled(False)
                ui.pushButton.setText('Hedge\nStarted')
                ui.lineEdit_orders_rate.setEnabled(False)
                ui.pushButton_orders_rate.setEnabled(False)

            elif object_signal == 'Hedge_Started_icon':
                green_icon = "./green_led_icon.png"
                ui.label_34.setPixmap(QtGui.QPixmap(green_icon))

            else:
                pass

        except Exception as er:
            from lists import list_monitor_log
            from connection_hedge import connect
            list_monitor_log.append('***** ERROR - ui_signal1 error code 1213. ' + str(er))
            connect.logwriter('***** ERROR - ui_signal1 error code 1214. ' + str(er))
            time.sleep(5)
        finally:
            pass

    def ui_signal2(info):
        if info == 'True':
            ui.textEdit_monitor.verticalScrollBar().setValue(999999)
        else:
            ui.textEdit_monitor.verticalScrollBar()

    def message_box_start_hedge_confirmation():
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Are you sure\nSTART Hedge?')
        msg.setWindowTitle('*** WARNING ***')
        msg.addButton('Ok', msg.AcceptRole)
        msg.addButton('Cancel', msg.RejectRole)
        pass
        if msg.exec_() == msg.Rejected:
            global index_greeks_print_on_off
            index_greeks_print_on_off = 'off'  # ok clicked
        else:
            pass  # cancel clicked

    def message_box_instrument_syntax_error():
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Instrument syntax ERROR')
        msg.setWindowTitle('*** WARNING ***')
        msg.exec_()
        pass

    def instrument_currency_saved():
        with open('instrument_hedge.txt', 'r') as instrument_currency_file:
            if 'BTC' in instrument_currency_file.read():
                return 'BTC'
            elif 'ETH' in instrument_currency_file.read():
                return 'ETH'
            else:
                message_box_instrument_syntax_error()
                pass

    def account_summary_print_tab_run_hedge():
        from connection_hedge import connect
        from lists import list_monitor_log

        try:
            global greeks_value_dict
            currency = str(instrument_currency_saved())
            summary_total = connect.get_account_summary(currency=currency)

            # Run Tab
            sinal.ui_signal1.emit({
                'object_signal': 'Run_Tab', 'info': summary_total})

            # greeks_value_dict
            greeks_value_dict = {
                'delta_total': round(float(summary_total['delta_total']), 4),
                'options_delta': round(float(summary_total['options_delta']), 4),
                'options_theta': round(float(summary_total['options_theta']), 4),
                'options_vega': round(float(summary_total['options_vega']), 4),
                'options_gamma': round(float(summary_total['options_gamma']), 4)
            }

        except Exception as er:
            from connection_hedge import connect
            connect.logwriter('********** ERROR - Account summary print tab run **********' + str(er))
            list_monitor_log.append('********** ERROR - Account summary print tab run **********' + str(er))
            pass
        finally:
            pass

    def btc_index_print():
        import time
        global index_greeks_print_on_off
        from lists import list_monitor_log

        if instrument_currency_saved() == 'ERROR':
            message_box_instrument_syntax_error()

        else:
            index_greeks_print_on_off = 'on'

            sinal.ui_signal1.emit({
                'object_signal': 'btc_index_print', 'info': ''})

            if CredentialsSaved().api_secret_saved() == '<Type your Deribit Key>' or \
                    CredentialsSaved.secret_key_saved() == '<Type your Deribit Secret Key>':
                unauthorized_token_code_13009_or_13004 = True
            else:
                unauthorized_token_code_13009_or_13004 = False

            while index_greeks_print_on_off == 'on':
                try:
                    from connection_hedge import connect

                    a = connect.index_price('btc_usd')
                    b = str(a['index_price'])

                    sinal.ui_signal1.emit({
                        'object_signal': 'lineEdit_24_btc_index', 'info': b})

                    if unauthorized_token_code_13009_or_13004 is True:
                        list_monitor_log.append('***** UPDATE CREDENTIALS - VERIFY API AND SECRET KEYS *****')
                        time.sleep(5)
                    else:
                        account_summary_print_tab_run_hedge()  # Já tem signal na função

                    for item in range(10, -1, -1):
                        sinal.ui_signal1.emit({
                            'object_signal': 'lineEdit_58', 'info': str(item)})
                        time.sleep(1)
                except Exception as error1:
                    from connection_hedge import connect
                    connect.logwriter('********** ERROR: BTC index print **********' + str(error1))
                    list_monitor_log.append('********** ERROR: BTC index print **********' + str(error1))
                    time.sleep(10)
                    pass
                finally:
                    pass
            thread_start_hedge()

    def btc_index_print_while_hedge():
        global index_greeks_print_on_off
        if instrument_currency_saved() == 'ERROR':
            message_box_instrument_syntax_error()
        else:
            try:
                index_greeks_print_on_off = 'on'
                from connection_hedge import connect

                a = connect.index_price('btc_usd')
                b = str(a['index_price'])

                sinal.ui_signal1.emit({
                    'object_signal': 'lineEdit_24_btc_index', 'info': b})

                account_summary_print_tab_run_hedge()  # Já tem singal na função

            except Exception as error1:
                from connection_hedge import connect
                connect.logwriter('********** ERROR: BTC index print while started hedge **********'
                                  + str(error1))
                time.sleep(10)
                pass
            finally:
                pass

    def autoscroll_monitor():
        if ui.checkBox_autoScrollBar.isChecked() is True:
            sinal.ui_signal2.emit(str(True))
        else:
            sinal.ui_signal2.emit(str(False))

    def thread_btc_index_print():
        import threading
        btc_index_thread = threading.Thread(daemon=True, target=btc_index_print)
        btc_index_thread.start()

    def lists_monitor():
        import time
        from lists import list_monitor_log
        from connection_hedge import connect

        counter = 0
        led1 = led_color()

        if led1 == 'green':
            info = {'object_signal': 'led_connection', 'led_color': 'green'}
            sinal.ui_signal1.emit(info)
        elif led1 == 'red':
            info = {'object_signal': 'led_connection', 'led_color': 'red'}
            sinal.ui_signal1.emit(info)
        else:
            connect.logwriter('*** ERROR - lists_monitor() Error Code:: 1296 ***')
            msg2 = str('*** ERROR - lists_monitor() Error Code:: 1297 ***')
            info = {'object_signal': 'textEdit_monitor', 'msg': msg2}
            sinal.ui_signal1.emit(info)

        while True:
            try:
                if len(list_monitor_log) > 0:
                    for i in list_monitor_log:
                        info = {'object_signal': 'textEdit_monitor', 'msg':
                                datetime.now().strftime("[%Y/%m/%d, %H:%M:%S] ") + str(i)}
                        sinal.ui_signal1.emit(info)
                        counter = counter + 1
                    list_monitor_log.clear()
                else:
                    time.sleep(0.0001)

                if led1 != led_color():
                    if led_color() == 'green':
                        led1 = led_color()
                        info = {'object_signal': 'led_connection', 'led_color': 'green'}
                        sinal.ui_signal1.emit(info)
                    elif led_color() == 'red':
                        led1 = led_color()
                        info = {'object_signal': 'led_connection', 'led_color': 'red'}
                        sinal.ui_signal1.emit(info)
                    else:
                        connect.logwriter('*** ERROR - lists_monitor() Error Code:: 1397 ***')
                        msg4 = str('*** ERROR - lists_monitor() Error Code:: 1398 ***')
                        info = {'object_signal': 'textEdit_monitor', 'msg': msg4}
                        sinal.ui_signal1.emit(info)
                else:
                    pass

                if counter >= 10000:
                    counter = 0
                    info = {'object_signal': 'pushbutton_2_click_signal', 'msg': ''}
                    sinal.ui_signal1.emit(info)
                    time.sleep(0.5)
                else:
                    pass

            except Exception as er:
                from connection_hedge import connect
                connect.logwriter(str(er) + ' Error Code:: 1414')
                msg5 = str('*** ERROR - lists_monitor() Error Code:: 1415: ' + str(er) + ' ***')
                info = {'object_signal': 'textEdit_monitor', 'msg': msg5}
                sinal.ui_signal1.emit(info)
                time.sleep(5)
            finally:
                pass

    def thread_lists_monitor():
        import threading
        lists_monitor_thread = threading.Thread(daemon=True, target=lists_monitor)
        lists_monitor_thread.start()

    def thread_start_hedge():
        import threading
        start_hedge_thread = threading.Thread(daemon=True, target=hedge)
        start_hedge_thread.start()

    def number_multiple_10_and_round_0_digits(number=None):
        a3 = number % 10
        b3 = float(number - a3)
        if abs(number) > 0 and round(b3, 0) == 0:
            return 10
        else:
            return round(b3, 0)

    def hedge_stop():
        global hedge_on_off
        hedge_on_off = 'off'

    def hedge():
        import time
        from connection_hedge import connect
        global greeks_value_dict
        global hedge_on_off

        sinal.ui_signal1.emit({
                'object_signal': 'Hedge_Started', 'info': ''})

        list_monitor_log.append('***** Hedge started *****')
        connect.logwriter('***** Hedge started *****')

        # Args fixed
        hedge_instrument = str(ConfigAndInstrumentsSaved().instrument_name_construction_from_file(instrument_number=1))
        hedge_type_saved = str(ConfigAndInstrumentsSaved().hedge_method())
        hedge_target = float(ConfigAndInstrumentsSaved().hedge_target())
        hedge_superior_limit = float(ConfigAndInstrumentsSaved().superior_limit())
        hedge_inferior_limit = float(ConfigAndInstrumentsSaved().inferior_limit())

        hedge_type = str
        if hedge_type_saved == 'TOTAL':
            hedge_type = 'delta_total'
        else:
            pass

        if hedge_type == 'delta_total':
            global hedge_on_off
            hedge_on_off = 'on'

            sinal.ui_signal1.emit({
                'object_signal': 'Hedge_Started_icon', 'info': ''})

            counter_while_hedge_on = 11
            currency = str(instrument_currency_saved())

            while hedge_on_off == 'on':
                try:
                    from connection_hedge import connect

                    counter_while_hedge_on = counter_while_hedge_on - 1
                    sinal.ui_signal1.emit({
                        'object_signal': 'lineEdit_58', 'info': str(counter_while_hedge_on)})

                    if counter_while_hedge_on <= 0:
                        counter_while_hedge_on = 11
                        btc_index_print_while_hedge()  # Já tem signal na função
                        greeks_value = greeks_value_dict
                        hedge_greeks_value = float(greeks_value[hedge_type])
                    else:
                        summary_total = connect.get_account_summary(currency=currency)
                        hedge_greeks_value = round(float(summary_total[hedge_type]), 4)

                    if float(hedge_superior_limit) >= float(hedge_greeks_value) >= float(hedge_inferior_limit):
                        list_monitor_log.append('*** Values according to defined parameters ***')

                    elif float(hedge_greeks_value) > float(hedge_superior_limit):
                        amount_in_btc = abs(float(hedge_greeks_value) - float(hedge_target))
                        order_book = connect.get_order_book(instrument_name=hedge_instrument)
                        hedge_price = abs(float(order_book['best_bid_price']))
                        order_book_best_bid_amount = number_multiple_10_and_round_0_digits(
                            number=abs(float(order_book['best_bid_amount'])))
                        amount_hedge_in_usd = number_multiple_10_and_round_0_digits(
                            number=float((amount_in_btc * hedge_price)))
                        if order_book_best_bid_amount < amount_hedge_in_usd:
                            amount_hedge = order_book_best_bid_amount
                        else:
                            amount_hedge = amount_hedge_in_usd
                        connect.cancel_all()
                        connect.sell_market(currency=hedge_instrument, amount=amount_hedge)
                        list_monitor_log.append('*** Value above the inferior limit ***')
                        list_monitor_log.append('*** Sell order sent ***')
                        list_monitor_log.append('Instrument: ' + str(hedge_instrument))
                        list_monitor_log.append('Amount:' + str(amount_hedge))
                        time.sleep(5)
                        connect.cancel_all()
                        time.sleep(2)

                    elif float(hedge_greeks_value) < float(hedge_inferior_limit):
                        amount_in_btc = abs(float(hedge_target) - float(hedge_greeks_value))
                        order_book = connect.get_order_book(instrument_name=hedge_instrument)
                        hedge_price = abs(float(order_book['best_ask_price']))
                        order_book_best_ask_amount = number_multiple_10_and_round_0_digits(
                            number=abs(float(order_book['best_ask_amount'])))
                        amount_hedge_in_usd = number_multiple_10_and_round_0_digits(
                            number=float((amount_in_btc * hedge_price)))
                        if order_book_best_ask_amount < amount_hedge_in_usd:
                            amount_hedge = order_book_best_ask_amount
                        else:
                            amount_hedge = amount_hedge_in_usd
                        connect.cancel_all()
                        connect.buy_market(currency=hedge_instrument, amount=amount_hedge)
                        list_monitor_log.append('*** Value below the inferior limit ***')
                        list_monitor_log.append('*** Buy order sent ***')
                        list_monitor_log.append('Instrument: ' + str(hedge_instrument))
                        list_monitor_log.append('Amount:' + str(amount_hedge))
                        time.sleep(5)
                        connect.cancel_all()
                        time.sleep(2)

                    else:
                        from connection_hedge import connect
                        connect.logwriter('********** ERROR while running hedge - line 1553 **********')
                        list_monitor_log.append('********** ERROR while running hedge - line 1554 **********')
                        time.sleep(10)

                except Exception as error1:
                    from connection_hedge import connect
                    connect.logwriter('********** ERROR while running hedge **********' + str(error1))
                    list_monitor_log.append('********** ERROR while running hedge **********' + str(error1))
                    time.sleep(10)
                finally:
                    pass
            list_monitor_log.append('***** Hedge Stopped *****')
            sinal.ui_signal1.emit({
                'object_signal': 'Hedge_Stopped', 'info': ''})
        else:
            from connection_hedge import connect
            connect.logwriter('********** ERROR while running hedge - line 1571 **********')
            list_monitor_log.append('********** ERROR while running hedge - line 1572 **********')

    sinal.ui_signal1.connect(ui_signal1)
    sinal.ui_signal2.connect(ui_signal2)
    thread_lists_monitor()
    ui.pushButton_start_print_loglog.hide()
    ui.pushButton_2.hide()
    ui.textEdit_monitor.textChanged.connect(autoscroll_monitor)
    thread_btc_index_print()
    ui.pushButton_start_trading.clicked.connect(message_box_start_hedge_confirmation)
    ui.pushButton_stop_arbitrage.clicked.connect(hedge_stop)
    ui.checkBox_autoScrollBar.clicked.connect(autoscroll_monitor)


# noinspection PyShadowingNam
def about(ui):
    def disagree_license_when_open_app():
        ui.tab_credentials.setDisabled(True)
        ui.tab_instruments.setDisabled(True)
        ui.tab_targets.setDisabled(True)
        ui.tab_run_trading.setDisabled(True)

    def disagree_license():
        from connection_hedge import connect

        ui.tab_credentials.setDisabled(True)
        ui.tab_instruments.setDisabled(True)
        ui.tab_targets.setDisabled(True)
        ui.tab_run_trading.setDisabled(True)

        connect.logwriter('License: I Disagreed')

        ui.radioButton_agree.setEnabled(False)
        ui.radioButton_disagree.setEnabled(False)

    def agree_license():
        from connection_hedge import connect

        ui.tab_credentials.setDisabled(False)
        ui.tab_instruments.setDisabled(False)
        ui.tab_targets.setDisabled(False)
        ui.tab_run_trading.setDisabled(False)

        connect.logwriter('License: I Disagreed')

        ui.radioButton_agree.setEnabled(False)
        ui.radioButton_disagree.setEnabled(False)

    disagree_license_when_open_app()
    ui.radioButton_agree.clicked.connect(agree_license)
    ui.radioButton_disagree.clicked.connect(disagree_license)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    credentials(ui=ui)
    config(ui=ui)
    summary(ui=ui)
    run_hedge(ui=ui)
    about(ui=ui)
    sys.exit(app.exec_())
