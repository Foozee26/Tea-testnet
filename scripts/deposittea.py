import os
import sys
import asyncio
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

init(autoreset=True)
BORDER_WIDTH = 80

NETWORK_URLS = ["https://tea-sepolia.g.alchemy.com/public"]
CHAIN_ID = 10218
EXPLORER_URL = "https://sepolia.tea.xyz/tx/0x"
CONTRACT_ADDRESS = "0xD0501e868AEC9973E118B975E00E1d078c88D263"
DTEA_ADDRESS = "0x8b12642f591E6e4226Ade511f2c831a9258fE903"
STEA_ADDRESS = "0x09bA156Aaf3505d07b6F82872b35D75b7A7d5032"

DTEA_ABI = [
    {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
]

STEA_ABI = [
    {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
]

DEPOSIT_ABI = [
    {"inputs": [], "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "", "type": "address"}], "name": "balances", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
]

LANG = {
    'vi': {
        'title': 'DEPOSIT TEA - TEA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'enter_amount': 'Nhập số lượng TEA để deposit: ',
        'enter_count': 'Nhập số lần deposit (mặc định 1): ',
        'processing_wallet': 'XỬ LÝ VÍ',
        'sending_tx': 'Đang gửi giao dịch...',
        'success': 'Deposit thành công',
        'failure': 'Thất bại',
        'address': 'Địa chỉ',
        'amount': 'Số lượng',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'contract_balance': 'Số dư trong hợp đồng',
        'error': 'Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ',
        'insufficient_balance': 'Số dư không đủ',
        'connect_success': 'Thành công: Đã kết nối mạng Tea Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG'
    },
    'en': {
        'title': 'DEPOSIT TEA - TEA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'enter_amount': 'Enter TEA amount to deposit: ',
        'enter_count': 'Enter number of deposits (default 1): ',
        'processing_wallet': 'PROCESSING WALLET',
        'sending_tx': 'Sending transaction...',
        'success': 'Deposit successful',
        'failure': 'Failed',
        'address': 'Address',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'contract_balance': 'Contract balance',
        'error': 'Error',
        'invalid_number': 'Please enter a valid number',
        'insufficient_balance': 'Insufficient balance',
        'connect_success': 'Success: Connected to Tea Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL'
    }
}

def print_border(text: str, color=Fore.CYAN):
    text = text.strip()
    if len(text) > BORDER_WIDTH - 4:
        text = text[:BORDER_WIDTH - 7] + "..."
    padded_text = f" {text} ".center(BORDER_WIDTH - 2)
    print(f"{color}┌{'─' * (BORDER_WIDTH - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (BORDER_WIDTH - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm private keys vào đây, mỗi key trên một dòng\n# Ví dụ: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
            sys.exit(1)
        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append((i, key))
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ Đọc pvkey.txt thất bại: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def connect_web3(language: str = 'en'):
    # Thử kết nối với các RPC mặc định
    for url in NETWORK_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} | Chain ID: {w3.eth.chain_id} | RPC: {url}{Style.RESET_ALL}")
                return w3
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']} | RPC: {url}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)} | RPC: {url}{Style.RESET_ALL}")

    # Nếu không kết nối được, yêu cầu người dùng nhập RPC
    print(f"{Fore.RED}  ✖ Không thể kết nối tới RPC mặc định{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  ℹ {'Vui lòng lấy RPC từ https://alchemy.com và nhập vào dưới đây' if language == 'vi' else 'Please obtain an RPC from https://alchemy.com and enter it below'}{Style.RESET_ALL}")
    custom_rpc = input(f"{Fore.YELLOW}  > {'Nhập RPC tùy chỉnh' if language == 'vi' else 'Enter custom RPC'}: {Style.RESET_ALL}").strip()

    if not custom_rpc:
        print(f"{Fore.RED}  ✖ {'Không có RPC được nhập, thoát chương trình' if language == 'vi' else 'No RPC provided, exiting program'}{Style.RESET_ALL}")
        sys.exit(1)

    # Thử kết nối với RPC tùy chỉnh
    try:
        w3 = Web3(Web3.HTTPProvider(custom_rpc))
        if w3.is_connected():
            print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} | Chain ID: {w3.eth.chain_id} | RPC: {custom_rpc}{Style.RESET_ALL}")
            return w3
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']} | RPC: {custom_rpc}{Style.RESET_ALL}")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)} | RPC: {custom_rpc}{Style.RESET_ALL}")
        sys.exit(1)

def display_balances(w3: Web3, address: str, deposit_contract, language: str = 'en'):
    balance_tea = float(w3.from_wei(w3.eth.get_balance(address), 'ether'))
    dtea_contract = w3.eth.contract(address=Web3.to_checksum_address(DTEA_ADDRESS), abi=DTEA_ABI)
    stea_contract = w3.eth.contract(address=Web3.to_checksum_address(STEA_ADDRESS), abi=STEA_ABI)
    balance_dtea = float(w3.from_wei(dtea_contract.functions.balanceOf(address).call(), 'ether'))
    balance_stea = float(w3.from_wei(stea_contract.functions.balanceOf(address).call(), 'ether'))
    contract_balance = float(w3.from_wei(deposit_contract.functions.balances(address).call(), 'ether'))
    print(f"{Fore.YELLOW}  {LANG[language]['balance']:<12}: {balance_tea:.6f} TEA | dTEA: {balance_dtea:.6f} dTEA | sTEA: {balance_stea:.6f} sTEA{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  {LANG[language]['contract_balance']:<12}: {contract_balance:.6f} TEA{Style.RESET_ALL}")

async def deposit_tea(w3: Web3, private_key: str, amount: float, tx_count: int, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address
    deposit_contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=DEPOSIT_ABI)

    amount_wei = w3.to_wei(amount, 'ether')
    total_amount_wei = amount_wei * tx_count

    balance_tea = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
    if balance_tea < amount * tx_count:
        print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance']}: Cần ít nhất {amount * tx_count:.6f} TEA{Style.RESET_ALL}")
        return 0

    successful_txs = 0
    for i in range(tx_count):
        try:
            nonce = w3.eth.get_transaction_count(sender_address)
            tx = deposit_contract.functions.deposit().build_transaction({
                'from': sender_address,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'gasPrice': w3.to_wei('0.1', 'gwei'),
                'value': amount_wei
            })
            gas_limit = deposit_contract.functions.deposit().estimate_gas({'from': sender_address, 'value': amount_wei}) * 1.2
            tx['gas'] = int(gas_limit)

            gas_cost = float(w3.from_wei(tx['gas'] * tx['gasPrice'], 'ether'))
            if balance_tea < amount + gas_cost:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance']}: Cần ít nhất {(amount + gas_cost):.6f} TEA{Style.RESET_ALL}")
                break

            print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']} ({i + 1}/{tx_count}){Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
            if receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['success']} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[language]['address']:<12}: {sender_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[language]['amount']:<12}: {amount:.6f} TEA{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[language]['gas']:<12}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[language]['block']:<12}: {receipt['blockNumber']}{Style.RESET_ALL}")
                display_balances(w3, sender_address, deposit_contract, language)
                successful_txs += 1
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
            if i < tx_count - 1:
                await asyncio.sleep(5)
        except Exception as e:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)}{Style.RESET_ALL}")
            break
    return successful_txs

async def run(language: str = 'en'):
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    w3 = connect_web3(language)
    successful_ops = 0
    total_ops = 0

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        account = Account.from_key(private_key)
        print(f"{Fore.YELLOW}  {LANG[language]['address']}: {account.address}{Style.RESET_ALL}")
        deposit_contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=DEPOSIT_ABI)
        display_balances(w3, account.address, deposit_contract, language)
        print()

        while True:
            count_input = input(f"{Fore.YELLOW}  > {LANG[language]['enter_count']}{Style.RESET_ALL}").strip()
            try:
                tx_count = int(count_input) if count_input else 1
                if tx_count > 0:
                    break
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

        while True:
            amount_input = input(f"{Fore.YELLOW}  > {LANG[language]['enter_amount']}{Style.RESET_ALL}").strip()
            try:
                amount = float(amount_input)
                if amount > 0:
                    break
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

        successful_txs = await deposit_tea(w3, private_key, amount, tx_count, language)
        successful_ops += successful_txs
        total_ops += tx_count
        if i < len(private_keys):
            await asyncio.sleep(10)
        print_separator()

    print_border(f"{LANG[language]['completed'].format(successful=successful_ops, total=total_ops)}", Fore.GREEN)

if __name__ == "__main__":
    asyncio.run(run_deposittea('vi'))
