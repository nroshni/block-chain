from hash_utils import hash_block, hash_string_sha256


class Verification:
    def valid_proof(self, transactions, previous_hash, proof):
        """
        Function to check if the proof satisfies the hashing condition

        Parameters
        ----------
            transactions (list): List of open transactions
            previous_hash (string): Hash of the previous block
            proof (integer): proof of work

        Returns
        -------
            True: If the proof satisfies the mentioned condition
            False: If the proof doesn't satisfy the mentioned condition
        """
        ordered_tx = [tx.to_ordered_dict() for tx in transactions]
        guess = (str(ordered_tx) + str(previous_hash) + str(proof)).encode()
        guessed_hash = hash_string_sha256(guess)

        print(f'Guessed hash : {guessed_hash}')
        return guessed_hash[0:2] == '00'

    def verify_chain(self, block_chain):
        """
        Function to verify if the current blockchain is valid.
        Returns
        -------
            True (Boolean): If blockchain is valid
            False (Boolean): If blockchain is invalid
        """
        for index, block in enumerate(block_chain):
            if index == 0:
                # No need to validate as the 1st block is always the genesis block
                continue
            if block.previous_hash != hash_block(block_chain[index - 1]):
                return False
            # Eliminate the reward transaction when checking if the proof is a valid
            # proof that would satisfy the given hash condition
            if not self.valid_proof(block.transactions[:-1],
                                    block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False

        return True

    def verify_transaction(self, transaction, get_balances):
        """
        Function that validates if a given transaction is valid based on
        the amount of funds the sender of the transaction has

        Parameters
        ----------
            transaction (dict): A transaction containing the sender,
                                recipient and the transaction amount

        Returns
        -------
            True (Boolean): If the transaction is valid
            False (Boolean): If the transaction is invalid
        """
        sender_balance = get_balances(transaction.sender)
        if transaction.amount > sender_balance:
            return False
        return True

    def verify_transactions(self, open_transactions, get_balances):
        """ Function to verify if all the open transactions are valid """
        return all([
            self.verify_transaction(tx, get_balances)
            for tx in open_transactions
        ])
