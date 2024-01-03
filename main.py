from utils_common import *
from eth_abi import encode
from requests import *
from fake_useragent import UserAgent

ZKF = Web3.to_checksum_address('0x1cD3E2A23C45A690a18Ed93FD1412543f464158F')

def transfer_token(web3, srcChain, privatekey, amount_to_transfer, to_address, token_address_contract, ERC20_ABI, retry=0):
    try:
        function_name = inspect.stack()[0][3]
        cprint(f'>>> start {function_name}:')

        token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address_contract), abi=ERC20_ABI)
        account = web3.eth.account.from_key(privatekey)
        my_address = account.address

        symbol = token_contract.functions.symbol().call()

        gas_price = MAX_GAS_PRICE

        tx_data = {
                "chainId": web3.eth.chain_id,
                "from": my_address,
                "nonce": web3.eth.get_transaction_count(my_address),
                'gasPrice': gas_price,
        }

        txn = token_contract.functions.transfer(
                Web3.to_checksum_address(to_address),
                amount_to_transfer).build_transaction(tx_data)

        gas = web3.eth.estimate_gas(txn)
        txn['gas'] = gas

        tx_signed = web3.eth.account.sign_transaction(txn, privatekey)
        tx_hash = web3.eth.send_raw_transaction(tx_signed.rawTransaction)
        result = pritnt_status_tx(function_name, srcChain, tx_hash, privatekey)

    except Exception as error:
        cprint(f'>>> Exception {function_name}: {error}', 'red')
        result = -1
        sleeping(15, 15)
        if (retry > 0):
            retry = retry - 1
            result = transfer_token(web3, srcChain, privatekey, amount_to_transfer, to_address, token_address_contract, ERC20_ABI, retry)
        return result

def transfer_eth(web3, srcChain, privatekey, amount_to_transfer, to_address, retry=0, i=0):
    function_name = inspect.stack()[0][3]
    cprint(f'>>> {i}. start {function_name}:')

    try:
        account = web3.eth.account.from_key(privatekey)
        address = account.address
        nonce = web3.eth.get_transaction_count(address)

        amount = intToDecimal(amount_to_transfer, 18) 
        gas_price = MAX_GAS_PRICE
        
        contract_txn = {
                'chainId': web3.eth.chain_id,
                'nonce': nonce,
                'gasPrice': gas_price,
                'to': Web3.to_checksum_address(to_address),
                'value': int(amount),
        }

        gas = web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = gas

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
    
def transfer_to_wallets(web3, key):
    for wallet in WALLET_LIST:
            amount = round(random.uniform(MIN_AMOUNT, MAX_AMOUNT), random.randint(6,9))
            transfer_eth(web3,'ZKF', key, amount, wallet)
            sleeping(2,4)

def collect(web3, key, address):
    if not WALLET_COLLECT:
        logger.warning(f'WALLET_COLLECT пустой. Введите кошелек в настройках.')
        return

    if (web3.eth.get_balance(address) > 0):
        balance_zkf = check_token_balance(key, check_rpc('ZKF')['rpc'], ZKF)
        if (balance_zkf > 0):
            transfer_token(web3,'ZKF', key, balance_zkf, WALLET_COLLECT, ZKF, ERC20_ABI)
            sleeping(5,5)
        else:
            logger.warning(f'collect ZKF | Нет на аккаунте ZKF. Пропускаем')

        amount_left = round(random.uniform(AMOUNT_MIN_LEFT_USDC, AMOUNT_MAX_LEFT_USDC), 6)
        amount_to_transfer = web3.eth.get_balance(address) - Web3.to_wei(amount_left, 'ether')
        if (amount_to_transfer > 0):
            collect_usdc = Web3.from_wei(web3.eth.get_balance(address) - Web3.to_wei(amount_left, 'ether'), 'ether')
            cprint(f'collect_usdc = {collect_usdc}')
            transfer_eth(web3,'ZKF', key, collect_usdc, WALLET_COLLECT)
            sleeping(5,5)
        else:
            logger.warning(f'collect USDC | USDC баланс < AMOUNT_LEFT_USDC ({amount_left}). Пропускаем')

    else:
        logger.warning(f'collect USDC | Нет на аккаунте USDC. Пропускаем')

def sell_inscription(w3, key, inscription_type, amount, price_per_item, retry=0):
    try:
        function_name = inspect.stack()[0][3]
        logger.success(f'>>> start {function_name}:')

        account = w3.eth.account.from_key(key)
        address = account.address

        gas_price = MAX_GAS_PRICE

        total_price = amount * price_per_item
        total_price_wei = Web3.to_wei(total_price, 'ether')
        print(f'total_price_wei = {total_price_wei}')
        if (inscription_type == 'FAIR'):
            inscription_id = 46308022477577007958419261438376410389232929614289639333622731840533339045888
        if (inscription_type == 'ZKFI'):
            inscription_id = 55371926972011559193134457160916859761174888589200348274761753835659314855936
        
        data = encode(["uint256","uint256","uint256","uint256","uint256"], [96, amount, total_price_wei, 4, inscription_id]) 
        total_data = "0x912f3095" + Web3.to_hex(data)[2:]

        tx = {
                'from': address,
                'to': Web3.to_checksum_address('0x63c6ee2597bb7ea1840d27a8b3b14efe9eafcbf5'),
                'value': 0,
                'nonce': w3.eth.get_transaction_count(address),
                'data': total_data,
                'chainId': w3.eth.chain_id,
                'gasPrice': gas_price
            }
            
        gas = w3.eth.estimate_gas(tx)
        tx['gas'] = gas
        signed_txn = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        result = pritnt_status_tx(function_name, 'ZKF', tx_hash, key)

    except Exception as error:
        cprint(f'>>> Exception {function_name}: {error}', 'red')
        result = -1
        sleeping(10, 10)
        if (retry > 0):
            retry = retry - 1
            result = sell_inscription(w3, key, inscription_type, amount, price_per_item, retry)
        return result

def get_inscription_amount(address, insctiption_ticker):
    url = f'https://api.zkfair.io/ins/mint/address?tick={insctiption_ticker.lower()}&address={address}'

    headers ={
                'User-Agent':UserAgent().random,
                'Referer':f'https://fairinscription.org/',
                'Origin':f'https://fairinscription.org/',
                'method':f'GET',
            }

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        try:
            text = json.loads(resp.text)
            total_amount = text['result'][insctiption_ticker.lower()]['amt']
            market_amount = text['result'][insctiption_ticker.lower()]['market']
            # amt_available_for_sale = total_amount - market_amount
            cprint(f'market_amount = {market_amount}')
            cprint(f'total_amount = {total_amount}')
            return total_amount
        except:
            logger.debug(f'Something going wrong')
            return 0

def get_inscription_floor(insctiption_ticker):
    url = f'https://api.zkfair.io/ins/mint/market-info-tick?tick={insctiption_ticker.lower()}'

    headers ={
                'User-Agent':UserAgent().random,
                'Referer':f'https://fairinscription.org/',
                'Origin':f'https://fairinscription.org/',
                'method':'GET',
                'authority':'api.zkfair.io',
            }

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        text = json.loads(resp.text)
        total_price = int(text['result']['floor']['price']) / 1_000_000_000_000_000_000
        total_amt = int(text['result']['floor']['amt']) 
        floor = total_price / total_amt
        cprint(f'floor = {floor}')
        return floor
    
def inscription(web3, key, address):
    floor = get_inscription_floor(INSCRIPTION_TICKER)
    amount = get_inscription_amount(address, INSCRIPTION_TICKER)
    price = FIX_PRICE
    if (SELL_BY_FLOOR):
                price = floor
    if (amount > 0):
        sell_inscription(web3, key, INSCRIPTION_TICKER, amount, price, 3)
        sleeping(10,10)
    else:
        cprint('Skip selling. No inscriptions', 'red')

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
            i = i + 1
            logger.debug(f'{i} wallet: https://scan.zkfair.io/address/{address} ')

            
            if (MODE == 'TRANSFER'):
                transfer_to_wallets(web3, key)

            if (MODE == 'COLLECT'):
                collect(web3, key, address)
            
            if (MODE == 'INSCRIPTION'):
                inscription(web3, key, address)
            

    main()

