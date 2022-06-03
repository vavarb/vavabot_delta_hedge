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


# Classe de Sinais.
class Sinais(QtCore.QObject):
    # Elementos.
    textedit_instruments_saved_signal = QtCore.pyqtSignal(str)
    ui_signal1 = QtCore.pyqtSignal(dict)  # ['object_signal': , 'action_signal': , 'info': ]
    ui_signal2 = QtCore.pyqtSignal(str)
    ui_signal3 = QtCore.pyqtSignal(dict)

    def __init__(self):
        QtCore.QObject.__init__(self)


sinal = Sinais()  # Instância da Classe Sinais.

with open('api-key_hedge.txt', 'r') as api_secret_saved_file1:
    api_secret_saved_file_read1 = str(api_secret_saved_file1.read())

with open('secret-key_hedge.txt', 'r') as secret_key_saved_file1:
    secret_key_saved_file_read1 = str(secret_key_saved_file1.read())

client_ID = api_secret_saved_file_read1
client_secret = secret_key_saved_file_read1

clientId = client_ID
clientSecret = client_secret

with open('testnet_true_or_false_hedge.txt', 'r') as testnet_saved_tru_or_false1_file:
    testnet_saved_tru_or_false1_file_read = str(testnet_saved_tru_or_false1_file.read())
    testnet_saved_tru_or_false1 = testnet_saved_tru_or_false1_file_read

if 'False' in testnet_saved_tru_or_false1:
    testnet_true_or_false = False
    user_client_url = 'wss://deribit.com/ws/api/v2'
else:
    testnet_true_or_false = True
    user_client_url = 'wss://test.deribit.com/ws/api/v2'

WSS_url = user_client_url


class CredentialsSaved:
    def __init__(self):
        self.self = self

    @staticmethod
    def api_secret_saved():
        from lists import list_monitor_log
        with open('api-key_hedge.txt', 'r') as api_secret_saved_file:
            api_secret_saved_file_read = str(api_secret_saved_file.read())
        list_monitor_log.append('*** API key: ' + str(api_secret_saved_file_read) + ' ***')
        return api_secret_saved_file_read

    @staticmethod
    def secret_key_saved():
        from lists import list_monitor_log
        with open('secret-key_hedge.txt', 'r') as secret_key_saved_file:
            secret_key_saved_file_read = str(secret_key_saved_file.read())
        list_monitor_log.append('*** SECRET key: ' + str(secret_key_saved_file_read) + ' ***')
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
            return False
        else:
            list_monitor_log.append('***** ERROR in testnet_saved_tru_or_false *****')

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
    def __init__(self, test=None, only_public=False, client_ID=False, client_secret=False):
        if test is True:
            if client_ID or client_secret: only_public = False
            if only_public:
                self.logwriter(msg='WARNING! Only public methods available!')
                return
            self._auth(client_ID, client_secret, WSS_url)
        else:
            pass
        if test is False:
            if client_ID or client_secret: only_public = False
            if only_public:
                self.logwriter(msg='WARNING! Only public methods available!')
                return
            self.WSS_url = 'wss://www.test.deribit.com/ws/api/v2' if test else 'wss://www.deribit.com/ws/api/v2'
            self._auth(client_ID, client_secret, self.WSS_url)
        else:
            pass

    def logwriter(self, msg):
        from lists import list_monitor_log
        out = datetime.now().strftime("\n[%Y%m%d,%H:%M:%S] ") + str(msg)
        list_monitor_log.append(str(out))
        try:
            with open('log_hedge.log', 'a') as log_file:
                log_file.write(out)
        except Exception as er:
            log_file.write(str(er))
            log_file.close()
            pass
        finally:
            log_file.close()
            pass

    def _auth(self, client_ID, client_secret, WSS_url):
        from lists import list_monitor_log

        timestamp = round(datetime.now().timestamp() * 1000)
        nonce = "abcd"
        data = ""
        signature = hmac.new(
            bytes(clientSecret, "latin-1"),
            msg=bytes('{}\n{}\n{}'.format(timestamp, nonce, data), "latin-1"),
            digestmod=hashlib.sha256
        ).hexdigest().lower()

        if testnet_true_or_false is True:
            try:
                self._WSS = create_connection(WSS_url)
                msg = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "public/auth",
                    "params": {
                        "grant_type": "client_signature",
                        "client_id": clientId,
                        "timestamp": timestamp,
                        "signature": signature,
                        "nonce": nonce,
                        "data": data
                    }
                }
                self.logwriter('Auth OK\n############')
                list_monitor_log.append('Auth OK\n############')
                list_monitor_log.append('identified')
                # print('identified')
                return self._sender(msg)
            except Exception as er:
                self.logwriter('auth error:' + str(er))
        else:
            pass
        if testnet_true_or_false is False:
            try:
                self._WSS = create_connection(WSS_url)
                msg = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "public/auth",
                    "params": {
                        "grant_type": "client_signature",
                        "client_id": clientId,
                        "timestamp": timestamp,
                        "signature": signature,
                        "nonce": nonce,
                        "data": data
                    }
                }
                self.logwriter('Auth OK\n############')
                list_monitor_log.append('Auth OK\n############')
                list_monitor_log.append('identified')
                # print('identified')
                return self._sender(msg)
            except Exception as er:
                self.logwriter('auth error:' + str(er))
        else:
            pass

    def _sender(self, msg):
        from lists import list_monitor_log
        try:
            self.logwriter(msg['method'])
            self._WSS.send(json.dumps(msg))
            out = json.loads(self._WSS.recv())
            # logwriter(msg=out['result'])
            # print(out)
            return out['result']
        except Exception as er:
            self.logwriter('_sender error: ' + str(er))
            list_monitor_log.append('_sender error: ' + str(er))

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


class ConfigAndInstrumentsSaved:
    def __init__(self):
        self.self = self
        self.instrument_number = None

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
                time.sleep(0.3)
                return 'instrument available'
            else:
                list_instrument_name.clear()
                time.sleep(0.3)
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
        ui.lineEdit_api_key_saved.setText(CredentialsSaved.api_secret_saved())

    def secret_key_saved_print():
        ui.lineEdit_api_secret_saved.setText(CredentialsSaved.secret_key_saved())

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
        with open('api-key_hedge.txt', 'w') as api_key_save_file:
            api_key_save_file.write(str(ui.lineEdit_api_key_new.text()))
        secret_key_save()
        api_key_saved_print()

    def secret_key_save():
        with open('secret-key_hedge.txt', 'w') as secret_key_save_file:
            secret_key_save_file.write(str(ui.lineEdit_api_secret_new.text()))
        secret_key_saved_print()

    def testnet_true_save():
        with open('testnet_true_or_false_hedge.txt', 'w') as testnet_true_save_file:
            testnet_true_save_file.write('True')
        testnet_true_or_false_saved_print()

    def testnet_false_save():
        with open('testnet_true_or_false_hedge.txt', 'w') as testnet_false_save_file:
            testnet_false_save_file.write('False')
        testnet_true_or_false_saved_print()

    api_key_saved_print()
    secret_key_saved_print()
    testnet_true_or_false_saved_print()
    ui.pushButton_submit_new_credintals.clicked.connect(message_box_reboot1)
    ui.radioButton_testnet_true.clicked.connect(message_box_reboot2)
    ui.radioButton_2_testnet_false.clicked.connect(message_box_reboot3)


def config(ui):
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
            if ui.lineEdit_currency_instrumet1.currentText() == 'Set BTC or ETH:':
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
                msg.setText('All fields config are required - ERROR')
                msg.setWindowTitle('***** ERROR *****')
                msg.exec_()
                pass

            else:
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
                config_saved_print()

        except Exception as er:
            list_monitor_log.append(str(er))
            config_save_file.close()

    sinal.textedit_instruments_saved_signal.connect(textedit_instruments_saved_signal)
    sinal.ui_signal3.connect(ui_signal3)
    instruments_saved_print_and_check_available()
    config_saved_print()
    ui.pushButton_submit_new_instruments.clicked.connect(instruments_save)
    ui.pushButton_submit_new_instruments_2.clicked.connect(config_save)


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
                currency = str(instrument_currency_saved())
                summary_total = connect.get_account_summary(currency=currency)

                instrument_name = str(
                    ConfigAndInstrumentsSaved().instrument_name_construction_from_file(instrument_number=1))
                position_instrument_hedge = connect.get_position(instrument_name=instrument_name)

                sinal.ui_signal1.emit({
                    'object_signal': 'textEdit_balance', 'info': summary_total, 'info2': position_instrument_hedge,
                    'info3': str(currency)})

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
                currency = str(instrument_currency_saved())
                summary_total = connect.get_account_summary(currency=currency)

                sinal.ui_signal1.emit({
                    'object_signal': 'textEdit_balance_after', 'info': summary_total})

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


def run_hedge(ui):
    from lists import list_monitor_log

    def ui_signal1(info):
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
            ui.textEdit_balance.append('Size: ' + str(round(instrument_position_hedge_size, 2)) + 'USD')
            ui.textEdit_balance.append('Size Currency: ' + str(round(instrument_position_hedge_size_currency, 8)) + str(
                currency))

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
            ui.textEdit_monitor.append(str(info['info']))
        elif object_signal == 'Hedge_Stopped':
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
        else:
            pass

    def ui_signal2(info):
        if info == 'True':
            ui.textEdit_monitor.verticalScrollBar().setValue(999999)
        else:
            ui.textEdit_monitor.verticalScrollBar()

    def led_connection():
        green_icon = "./green_led_icon.png"
        red_icon = "./red_led_icon.png"
        led1 = 'red'
        while True:
            time.sleep(1)
            if led1 == led_color():
                pass
            else:
                if led_color() == 'green':
                    ui.label_29.setPixmap(QtGui.QPixmap(green_icon))
                elif led_color() == 'red':
                    ui.label_29.setPixmap(QtGui.QPixmap(red_icon))
                else:
                    pass

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
            list_monitor_log.append('********** ERROR - Account summary print tab run **********' + str(er))
            pass
        finally:
            pass

    def btc_index_print():
        import time
        global index_greeks_print_on_off
        if instrument_currency_saved() == 'ERROR':
            message_box_instrument_syntax_error()

        else:
            index_greeks_print_on_off = 'on'
            ui.pushButton.setEnabled(False)
            ui.pushButton.setText('Chronometer\nEnabled')
            ui.pushButton_stop_arbitrage.setEnabled(False)
            ui.pushButton_start_trading.setEnabled(True)

            red_icon = "./red_led_icon.png"
            ui.label_34.setPixmap(QtGui.QPixmap(red_icon))

            while index_greeks_print_on_off == 'on':
                try:
                    from connection_hedge import connect

                    a = connect.index_price('btc_usd')
                    b = str(a['index_price'])

                    sinal.ui_signal1.emit({
                        'object_signal': 'lineEdit_24_btc_index', 'info': b})

                    account_summary_print_tab_run_hedge()  # Já tem signal na função
                    for item in range(10, -1, -1):
                        sinal.ui_signal1.emit({
                            'object_signal': 'lineEdit_58', 'info': str(item)})
                        time.sleep(1)
                except Exception as error1:
                    list_monitor_log.append('********** ERROR: BTC index print **********' + str(error1))
                    time.sleep(50)
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
                list_monitor_log.append('********** ERROR: BTC index print while started hedge **********'
                                        + str(error1))
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

    def clear_monitor():
        ui.textEdit_monitor.clear()

    def lists_monitor():
        import time
        from lists import list_monitor_log, list_monitor_print_log

        counter = 0

        len_log_a = 0
        while True:
            len_log_b = len(list_monitor_log)
            if len_log_a == len_log_b:
                time.sleep(0.001)
                pass
            elif len_log_a != len_log_b:
                list_monitor_print_log.append(list_monitor_log[len_log_a:])
                del (list_monitor_log[:len_log_a])
                for i in range(len(list_monitor_print_log)):
                    info1 = (list_monitor_print_log[i])
                    sinal.ui_signal1.emit({
                        'object_signal': 'textEdit_monitor', 'info': info1})
                    del (list_monitor_print_log[i])
                len_log_a = len(list_monitor_log)
                time.sleep(0.001)
                pass
            else:
                info1 = '********** ERROR: print Monitor **********'
                sinal.ui_signal1.emit({
                    'object_signal': 'textEdit_monitor', 'info': info1})
                pass
            counter = counter + 1
            if counter >= 100000:
                counter = 0
                ui.pushButton_2.click()
                time.sleep(0.5)
                pass
            else:
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
        global greeks_value_dict
        global hedge_on_off

        ui.pushButton_submit_new_credintals.setEnabled(False)
        ui.radioButton_testnet_true.setEnabled(False)
        ui.radioButton_2_testnet_false.setEnabled(False)
        ui.pushButton_submit_new_instruments.setEnabled(False)
        ui.pushButton_submit_new_instruments_2.setEnabled(False)
        ui.pushButton_start_trading.setEnabled(False)
        ui.pushButton_stop_arbitrage.setEnabled(True)
        ui.pushButton_start_trading.setEnabled(False)
        ui.pushButton.setText('Hedge\nStarted')

        list_monitor_log.append('*** Hedge started ***')

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

            green_icon = "./green_led_icon.png"
            ui.label_34.setPixmap(QtGui.QPixmap(green_icon))

            while hedge_on_off == 'on':
                try:
                    from connection_hedge import connect

                    btc_index_print_while_hedge()  # Já tem signal na função

                    greeks_value = greeks_value_dict
                    hedge_greeks_value = float(greeks_value[hedge_type])

                    if float(hedge_superior_limit) >= float(hedge_greeks_value) >= float(hedge_inferior_limit):
                        list_monitor_log.append('*** Values according to defined parameters ***')
                        pass
                        time.sleep(2)

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
                        time.sleep(1)
                        pass
                        # time.sleep(10)
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
                        time.sleep(1)
                        pass
                        # time.sleep(10)
                    else:
                        list_monitor_log.append('********** ERROR while running hedge - line 1415 **********')
                        time.sleep(20)
                        pass
                except Exception as error1:
                    list_monitor_log.append('********** ERROR while running hedge **********' + str(error1))
                    time.sleep(50)
                    pass
                finally:
                    pass
            list_monitor_log.append('***** Hedge Stopped *****')
            sinal.ui_signal1.emit({
                'object_signal': 'Hedge_Stopped', 'info': ''})
            pass
        else:
            list_monitor_log.append('********** ERROR while running hedge - line 1455 **********')
            pass

    sinal.ui_signal1.connect(ui_signal1)
    sinal.ui_signal2.connect(ui_signal2)
    led_thread = threading.Thread(daemon=True, target=led_connection)
    led_thread.start()
    thread_lists_monitor()
    ui.pushButton_start_print_loglog.hide()
    ui.pushButton_2.hide()
    ui.textEdit_monitor.textChanged.connect(autoscroll_monitor)
    thread_btc_index_print()
    ui.pushButton_start_trading.clicked.connect(message_box_start_hedge_confirmation)
    ui.pushButton_stop_arbitrage.clicked.connect(hedge_stop)
    ui.pushButton_2.clicked.connect(clear_monitor)


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
    sys.exit(app.exec_())
