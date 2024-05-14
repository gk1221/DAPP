from web3 import Web3  # Import Web3 library for interacting with Ethereum
from solcx import compile_standard, install_solc  # Import solcx for Solidity compilation
import json  # Import json for working with JSON files
from datetime import datetime # Import datetime for dueDate
import pandas as pd
from eth_account import Account
from scripts.setting import get_path

GANACHE_URL = get_path("GANACHE_URL")
CONTRACT_PATH = get_path("CONTRACT_PATH")
ABI_PATH = get_path("ABI_PATH")

class DeployContract:
    """
    DeployContract class deploys the Event contract to Ganache and saves the contract's ABI as JSON.
    """
    def __init__(self, account_address, name, optionNames, due):
        """
        Initializes the DeployContract object with the constructor parameters of the Event contract.
        :param account_address: Address of the account deploying the contract.
        :param name: Name of the event.
        :param optionNames: List of option names.
        :param due: Due date of the event.
        """
        self.account_address = account_address
        self.name = name
        self.optionNames = optionNames
        self.due = due
        self.web3 = Web3(Web3.HTTPProvider(GANACHE_URL))  # Connect to Ganache

    def deploy(self):
        """
        Deploys the Event contract to Ganache using the specified account and saves the ABI as JSON.
        """
        # Read contract source code
        with open(CONTRACT_PATH, "r", encoding="utf-8") as file:
            contract_source_code = file.read()

        # Compile contract
        compiled_contract = compile_standard(
            {
                "language": "Solidity",
                "sources": {"Event.sol": {"content": contract_source_code}},
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                            # output needed to interact with and deploy contract
                        }
                    }
                }
            },
            solc_version="0.8.19"
        )

        # Deploy contract
        bytecode = compiled_contract["contracts"]["Event.sol"]["Event"]["evm"]["bytecode"]["object"]
        abi = compiled_contract["contracts"]["Event.sol"]["Event"]["abi"]
        contract = self.web3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = contract.constructor(self.name, self.optionNames, self.due).transact({"from": self.account_address})
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress

        # Save ABI as JSON
        with open(ABI_PATH, "w") as abi_file:
            json.dump(abi, abi_file)

class Contract:
    """
    Contract class interacts with the deployed Event contract.
    """
    def __init__(self, contract_address, wallet_secret_key):
        """
        Initializes the Contract object with the contract address, wallet address, and wallet secret key.
        :param contract_address: Address of the deployed contract.
        :param wallet_address: Wallet address for signing transactions.
        :param wallet_secret_key: Wallet secret key for signing transactions.
        """
        self.contract_address = contract_address
        self.wallet_address = Account.from_key(wallet_secret_key).address
        self.wallet_secret_key = wallet_secret_key
        self.web3 = Web3(Web3.HTTPProvider(GANACHE_URL))  # Connect to Ganache

        # Read contract ABI from JSON
        with open(ABI_PATH, "r") as abi_file:
            self.contract_abi = json.load(abi_file)

        self.contract = self.web3.eth.contract(address = self.contract_address, abi = self.contract_abi)

    def getProfile(self):
        """
        Returns the profile of the event.
        """
        # Call dueDate function
        return self.contract.functions.getProfile().call()
    
    def getTotalPrice(self):
        """
        Returns the total price of the event.
        """
        # Call getTotalPrice function
        return self.contract.functions.getTotalPrice().call()
    
    def getWinnerCount(self, selection):
        return self.contract.functions.getWinnerCount(selection).call()
    
    def dueDate(self):
        """
        Returns the due date of the event.
        """
        # Call dueDate function
        return self.contract.functions.dueDate().call()
    
    def isAlive(self):
        """
        Returns the contract status.
        """
        return self.contract.functions.isAlive().call()
    
    def eventName(self):
        """
        Returns the name of the event.
        """
        # Call eventName function
        return self.contract.functions.eventName().call()
    
    def manager(self):
        """
        Returns the manager of the event.
        """
        # Call manager function
        return self.contract.functions.manager().call()
    
    def resultOption(self):
        return self.contract.functions.resultOption().call()

    def enter(self, selection):
        """
        Enters the event by making a payment and selecting an option.
        :param selection: Selection made by the participant.
        """
        # Build transaction
        transaction = self.contract.functions.enter(selection).build_transaction({
            'from': self.wallet_address,
            'value': self.web3.to_wei(5, 'ether'),  # Amount to be sent
            'nonce': self.web3.eth.get_transaction_count(self.wallet_address),
            'gas': 200000,
            'maxFeePerGas': 2000000000,
            'maxPriorityFeePerGas': 1000000000,
        })

        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(transaction, self.wallet_secret_key)

        # Send transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def endEvent(self, selection):
        """
        Ends the event by transferring rewards to winners.
        :param selection: Selection made by the winner.
        """
        # Build transaction
        transaction = self.contract.functions.endEvent(selection).build_transaction({
            'from': self.wallet_address,
            'nonce': self.web3.eth.get_transaction_count(self.wallet_address),
        })

        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(transaction, self.wallet_secret_key)

        # Send transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
    
    def cancel(self):
        """
        Cancels the event.
        """
        # Build transaction
        transaction = self.contract.functions.cancel().build_transaction({
            'from': self.wallet_address,
            'nonce': self.web3.eth.get_transaction_count(self.wallet_address),
        })

        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(transaction, self.wallet_secret_key)

        # Send transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt
    
class BlockInformation:

    def __init__(self, wallet_secret_key):
        """
        UI class interacts with the deployed Event contract.
        """
        self.wallet_address = Account.from_key(wallet_secret_key).address
        self.wallet_secret_key = wallet_secret_key
        self.web3 = Web3(Web3.HTTPProvider(GANACHE_URL))  # Connect to Ganache
        self.lastest_block_number = self.web3.eth.block_number
        self.wallet_balance = int(self.web3.from_wei(self.web3.eth.get_balance(self.wallet_address),
                                                     unit = "ether"))

        # Read contract ABI from JSON
        with open(ABI_PATH, "r") as abi_file:
            self.contract_abi = json.load(abi_file)

        self.contract_creation = pd.DataFrame(columns = ["timestamp", "contract_manager", "contract_address", "eventName", "dueDate", "Profile", "isAlive"]) 
        self.action_log = pd.DataFrame(columns = ["timestamp", "function_name", "selection", "from", "to", "value"])
        if self.lastest_block_number > 0:
            self.contract_creation = self.get_contract_creation()
            self.action_log = self.get_action_log()

    def get_contract_creation(self):
        
        rows = []
        # traverse all block and get block's information
        for i in range(1, self.lastest_block_number + 1):

            block = self.web3.eth.get_block(i)
            transaction = block["transactions"][0]
            tx = self.web3.eth.get_transaction(transaction.hex())
            to = tx["to"]
            
            is_contract = (to == None)

            # create contract
            if is_contract:
                row = {"timestamp": datetime.fromtimestamp(block["timestamp"]),
                        "contract_manager": tx["from"],
                        "contract_address": self.web3.eth.get_transaction_receipt(tx.hash)["contractAddress"]}
                
                rows.append(row)

        df = pd.DataFrame(rows)
        # traverse all contract_address and get contract's detail
        df["eventName"] = df["contract_address"].apply(lambda x : Contract(x, self.wallet_secret_key).eventName())
        df["dueDate"] = df["contract_address"].apply(lambda x : Contract(x, self.wallet_secret_key).dueDate())
        df["Options"] = df["contract_address"].apply(lambda x : Contract(x, self.wallet_secret_key).getProfile()[2])
        df["isAlive"] = df["contract_address"].apply(lambda x : Contract(x, self.wallet_secret_key).isAlive())
        df["resultOption"] = df["contract_address"].apply(lambda x : Contract(x, self.wallet_secret_key).resultOption()[1])
        
        return df.to_dict("records")

    def get_action_log(self):

        rows = []
        # traverse all block and get block's information
        for i in range(1, self.lastest_block_number + 1):

            block = self.web3.eth.get_block(i)
            transaction = block["transactions"][0]
            tx = self.web3.eth.get_transaction(transaction.hex())
            to = tx["to"]
            
            is_contract = (to == None)

            # create contract
            # call function
            if is_contract == False:
                contract = self.web3.eth.contract(address = to, abi = self.contract_abi)
                input_decoded = contract.decode_function_input(tx.input)
                row = {"timestamp": datetime.fromtimestamp(block["timestamp"]),
                       "function_name": input_decoded[0].fn_name,
                       "selection": input_decoded[1],
                       "from": tx["from"],
                       "to": tx["to"],
                       "value": self.web3.from_wei(tx["value"], unit="ether"),
                       }
                
                rows.append(row)
        
        if len(rows) == 0:
            return pd.DataFrame(columns = ["timestamp", "function_name", "selection", "from", "to", "value"])
        else:
            return pd.DataFrame(rows)

def private_key_to_account_address(private_key):
    return Account.from_key(private_key).address