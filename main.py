from utils_common import *

def transfer_eth(web3, srcChain, privatekey, amount_to_transfer, to_address, retry=0, i=0):
    function_name = inspect.stack()[0][3]
    cprint(f'>>> {i}. start {function_name}:')

    try:
        data = check_rpc(srcChain)
        chain_id = data['chain_id']

        account = web3.eth.account.from_key(privatekey)
        address = account.address
        nonce = web3.eth.get_transaction_count(address)

        amount = intToDecimal(amount_to_transfer, 18) 
        gas_price = MAX_GAS_PRICE
        gas = MAX_GAS_LIMIT
        
        contract_txn = {
                'chainId': chain_id,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': gas,
                'to': Web3.to_checksum_address(to_address),
                'value': int(amount),
        }

        tx_signed = web3.eth.account.sign_transaction(contract_txn, privatekey)
        tx_hash = web3.eth.send_raw_transaction(tx_signed.rawTransaction)
        result = pritnt_status_tx(function_name, srcChain, tx_hash, privatekey)
        if (result != 1 and retry > 0):
            retry = retry - 1
            transfer_eth(srcChain, privatekey, amount_to_transfer, to_address, retry, i=0)
        return result

    except Exception as error:
        cprint(f'>>> transfer : {privatekey} | {error}', 'red')
        result = -1
        if (retry > 0):
            retry = retry - 1
            result = transfer_eth(srcChain, privatekey, amount_to_transfer, to_address, retry, i=0)
        return result

scan = 'https://scan.zkfair.io'

if __name__ == "__main__":
    with open(scriptPath+"keys.txt", "r") as f:
        KEYS_LIST = [row.strip() for row in f]  

    with open(scriptPath+"wallet.txt", "r") as f:
        WALLET_LIST = [row.strip() for row in f]

    def main():
        i = 0

        while KEYS_LIST:
            key = KEYS_LIST.pop(0)
            web3 = Web3(Web3.HTTPProvider(check_rpc('ZKF')['rpc']))
            address = web3.eth.account.from_key(key).address
            logger.debug(f'{i} wallet: https://scan.zkfair.io/address/{address} ', 'magenta')

            for wallet in WALLET_LIST:
                amount = round(random.uniform(MIN_AMOUNT, MAX_AMOUNT), random.randint(6,9))
                transfer_eth(web3,'ZKF', key, amount, wallet)
                sleeping(2,4)

    main()

