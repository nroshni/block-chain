from blockchain import BlockChain
from verification import Verification


class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'Roshni'
        self.block_chain = BlockChain(self.id)

    def get_transaction_values(self):
        """ Returns the input of the user transaction amount as a float """
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Enter your transaction amount: '))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        user_input = input('Your choice:')
        return user_input

    def print_blockchain_elements(self):
        for block in self.block_chain.get_chain():
            print(f'Block Value : {block}')

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print(f'#' * 20)
            print('Please choose:')
            print(f'1: Add a new transaction value')
            print(f'2: Output the blockchain blocks')
            print(f'3: Mine a new block')
            print(f'4: Check transaction validity')
            print(f'q: Quit')
            user_choice = self.get_user_choice()

            if user_choice == '1':
                tx_value = self.get_transaction_values()
                tx_recipient, tx_amount = tx_value
                if self.block_chain.add_transaction(tx_recipient,
                                                    self.id,
                                                    amount=tx_amount):
                    print("Added Transaction")
                else:
                    print("Transaction Failed")
                print('Open transactions : {}'.format(
                    self.block_chain.get_open_transactions()))
            elif user_choice == '2':
                self.print_blockchain_elements()
            elif user_choice == '3':
                self.block_chain.mine_block()
            elif user_choice == '4':
                if Verification.verify_transactions(
                        self.block_chain.get_open_transactions(),
                        self.block_chain.get_balances):
                    print('All transactions are valid')
                else:
                    print('There exists invalid transactions')
            elif user_choice == 'q' or user_choice == 'Q':
                waiting_for_input = False
            else:
                print('Invalid input, please pick an option from the list!')

            if not Verification.verify_chain(self.block_chain.get_chain()):
                print("Block chain - INVALIDATED")
                break

            print('Balance of {}: {:.2f}'.format(
                self.id, self.block_chain.get_balances()))
        else:
            print('** User exited **')
        print(f'Final Blockchain : {self.block_chain.get_chain()}')


node = Node()
node.listen_for_input()
