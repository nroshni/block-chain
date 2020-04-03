import os
import logging
from blockchain import BlockChain
from utils.verification import Verification

log_folder = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(log_folder, "Blockchain_LOG"),
    datefmt='%m-%d-%Y %I:%M:%S %p',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Node:
    def __init__(self):
        self.id = 'Roshni'
        self.block_chain = BlockChain(self.id)
        logging.info('Initializing Node: {}'.format(self.__dict__))

    def get_transaction_values(self):
        """ Returns the input of the user transaction amount as a float """
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Enter your transaction amount: '))
        logging.debug(
            "Received - Recipient Name: {} & Transaction Amount: {}".format(
                tx_recipient, tx_amount))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        user_input = input('Your choice:')
        logging.debug(f'User choice input: {user_input}')
        return user_input

    def print_blockchain_elements(self):
        for block in self.block_chain.get_chain():
            print(f'Block Value : {block}')

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print(f'#' * 50)
            print('Please choose:')
            print(f'1: Add a new transaction value')
            print(f'2: Output the blockchain blocks')
            print(f'3: Mine a new block')
            print(f'4: Check transaction validity')
            print(f'q: Quit')
            logging.info('#' * 50)
            user_choice = self.get_user_choice()

            if user_choice == '1':
                logging.info(f'Adding a new transaction')
                tx_value = self.get_transaction_values()
                tx_recipient, tx_amount = tx_value
                if self.block_chain.add_transaction(tx_recipient,
                                                    self.id,
                                                    amount=tx_amount):
                    logging.info("Added Transaction")
                else:
                    logging.warning("Transaction Failed - Insufficient funds")
                print('Open transactions : {}'.format(
                    self.block_chain.get_open_transactions()))
            elif user_choice == '2':
                logging.info('Printing the blockchain blocks')
                self.print_blockchain_elements()
            elif user_choice == '3':
                logging.info('Mining a new block')
                self.block_chain.mine_block()
            elif user_choice == '4':
                logging.info(f'Checking transaction validity')
                if Verification.verify_transactions(
                        self.block_chain.get_open_transactions(),
                        self.block_chain.get_balances):
                    logging.info('All transactions are valid')
                    print('All transactions are valid')
                else:
                    logging.warning('There exists invalid transactions')
                    print('There exists invalid transactions')
            elif user_choice == 'q' or user_choice == 'Q':
                logging.info(f'Quitting block chain')
                waiting_for_input = False
            else:
                logging.info('Invalid User input')
                print('Invalid input, please pick an option from the list!')

            if not Verification.verify_chain(self.block_chain.get_chain()):
                logging.error("Block chain - INVALIDATED")
                print("Block chain - INVALIDATED")
                break
            else:
                logging.info("Valid block chain")

            logging.info('Balance of {}: {:.2f}'.format(
                self.id, self.block_chain.get_balances()))
            print('Balance of {}: {:.2f}'.format(
                self.id, self.block_chain.get_balances()))


if __name__ == "__main__":
    node = Node()
    node.listen_for_input()
