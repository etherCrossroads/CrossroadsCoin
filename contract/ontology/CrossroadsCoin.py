from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import Notify, CheckWitness
from ontology.interop.System.Action import RegisterAction
from ontology.interop.Ontology.Runtime import AddressToBase58, Base58ToAddress
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash
from ontology.interop.Ontology.Native import Invoke
from ontology.builtins import *

"""
https://github.com/tonyclarking/python-template/blob/master/libs/Utils.py
"""
def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)

"""
https://github.com/tonyclarking/python-template/blob/master/libs/SafeCheck.py
"""
def Require(condition):
    """
	If condition is not satisfied, return false
	:param condition: required condition
	:return: True or false
	"""
    if not condition:
        Revert()
    return True

def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True

"""
SafeMath 
"""

def Add(a, b):
	"""
	Adds two numbers, throws on overflow.
	"""
	c = a + b
	Require(c >= a)
	return c

def Sub(a, b):
	"""
	Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
	"""
	Require(a>=b)
	return a-b

def ASub(a, b):
    if a > b:
        return a - b
    if a < b:
        return b - a
    else:
        return 0

def Mul(a, b):
	"""
	Multiplies two numbers, throws on overflow.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
	"""
	if a == 0:
		return 0
	c = a * b
	Require(c / a == b)
	return c

def Div(a, b):
	"""
	Integer division of two numbers, truncating the quotient.
	"""
	Require(b > 0)
	c = a / b
	return c

def Pwr(a, b):
    """
    a to the power of b
    :param a the base
    :param b the power value
    :return a^b
    """
    c = 0
    if a == 0:
        c = 0
    elif b == 0:
        c = 1
    else:
        i = 0
        c = 1
        while i < b:
            c = Mul(c, a)
            i = i + 1
    return c

def Sqrt(a):
    """
    Return sqrt of a
    :param a:
    :return: sqrt(a)
    """
    c = Div(Add(a, 1), 2)
    b = a
    while(c < b):
        b = c
        c = Div(Add(Div(a, c), c), 2)
    return c

######################### Global info ########################
TransferEvent = RegisterAction("transfer", "from", "to", "amount")
ApprovalEvent = RegisterAction("approval", "owner", "spender", "amount")
ExchangeEvent = RegisterAction("exchange", "address", "amount", "crcAmount")
RedeemEvent = RegisterAction("redeem", "address", "amount")

NAME = 'CrossRoadCoin'
SYMBOL = 'CRC'
DECIMALS = 0
BALANCE_PREFIX = b'\x01'
APPROVE_PREFIX = b'\x02'
SUPPLY_KEY = 'TotalSupply'
DEST_ONG = 1000000000000000
INIT_RATE = 20000000000000
MIN_RATE = 4000000000000

k = Div(DEST_ONG, Sub(INIT_RATE, MIN_RATE))

ctx = GetContext()
ONGAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')
contractAddress = GetExecutingScriptHash()

def Main(operation, args):
    """
    :param operation:
    :param args:
    :return:
    """
    if operation == 'name':
        return name()
    if operation == 'symbol':
        return symbol()
    if operation == 'decimals':
        return decimals()
    if operation == 'totalSupply':
        return totalSupply()
    if operation == 'balanceOf':
        if len(args) != 1:
            return False
        acct = args[0]
        return balanceOf(acct)
    if operation == 'transfer':
        if len(args) != 3:
            return False
        else:
            from_acct = args[0]
            to_acct = args[1]
            amount = args[2]
            return transfer(from_acct,to_acct,amount)
    if operation == 'transferMulti':
        return transferMulti(args)
    if operation == 'transferFrom':
        if len(args) != 4:
            return False
        spender = args[0]
        from_acct = args[1]
        to_acct = args[2]
        amount = args[3]
        return transferFrom(spender,from_acct,to_acct,amount)
    if operation == 'approve':
        if len(args) != 3:
            return False
        owner  = args[0]
        spender = args[1]
        amount = args[2]
        return approve(owner,spender,amount)
    if operation == 'allowance':
        if len(args) != 2:
            return False
        owner = args[0]
        spender = args[1]
        return allowance(owner,spender)
    if operation == "exchange":
        if len(args) != 2:
            return False
        owner = args[0]
        amount = args[1]
    if operation == "redeem":
        if len(args) != 2:
            return False
        owner = args[0]
        amount = args[1]
    return False

def name():
    """
    :return: name of the token
    """
    return NAME


def symbol():
    """
    :return: symbol of the token
    """
    return SYMBOL


def decimals():
    """
    :return: the decimals of the token
    """
    return DECIMALS


def totalSupply():
    """
    :return: the total supply of the token
    """
    return Get(ctx, SUPPLY_KEY)


def balanceOf(account):
    """
    :param account:
    :return: the token balance of account
    """
    if len(account) != 20:
        raise Exception("address length error")
    return Get(ctx,concat(BALANCE_PREFIX,account))


def transfer(from_acct, to_acct, amount):
    """
    Transfer amount of tokens from from_acct to to_acct
    :param from_acct: the account from which the amount of tokens will be transferred
    :param to_acct: the account to which the amount of tokens will be transferred
    :param amount: the amount of the tokens to be transferred, >= 0
    :return: True means success, False or raising exception means failure.
    """
    if len(to_acct) != 20 or len(from_acct) != 20:
        raise Exception("address length error")
    if CheckWitness(from_acct) == False or amount < 0:
        return False

    fromKey = concat(BALANCE_PREFIX, from_acct)
    fromBalance = Get(ctx,fromKey)
    if amount > fromBalance:
        return False
    if amount == fromBalance:
        Delete(ctx,fromKey)
    else:
        Put(ctx,fromKey,Sub(fromBalance, amount))

    toKey = concat(BALANCE_PREFIX, to_acct)
    toBalance = Get(ctx, toKey)
    Put(ctx,toKey,Add(toBalance, amount))

    TransferEvent(from_acct, to_acct, amount)

    return True


def transferMulti(args):
    """
    :param args: the parameter is an array, containing element like [from, to, amount]
    :return: True means success, False or raising exception means failure.
    """
    for p in args:
        if len(p) != 3:
            # return False is wrong
            raise Exception("transferMulti params error.")
        if transfer(p[0], p[1], p[2]) == False:
            # return False is wrong since the previous transaction will be successful
            raise Exception("transferMulti failed.")
    return True


def approve(owner, spender, amount):
    """
    owner allow spender to spend amount of token from owner account
    Note here, the amount should be less than the balance of owner right now.
    :param owner:
    :param spender:
    :param amount: amount>=0
    :return: True means success, False or raising exception means failure.
    """
    if len(spender) != 20 or len(owner) != 20:
        raise Exception("address length error")
    if CheckWitness(owner) == False:
        return False
    if amount > balanceOf(owner) or amount < 0:
        return False

    key = concat(concat(APPROVE_PREFIX,owner),spender)
    Put(ctx, key, amount)

    ApprovalEvent(owner, spender, amount)

    return True


def transferFrom(spender, from_acct, to_acct, amount):
    """
    spender spends amount of tokens on the behalf of from_acct, spender makes a transaction of amount of tokens
    from from_acct to to_acct
    :param spender:
    :param from_acct:
    :param to_acct:
    :param amount:
    :return:
    """
    if len(spender) != 20 or len(from_acct) != 20 or len(to_acct) != 20:
        raise Exception("address length error")
    if CheckWitness(spender) == False:
        return False

    fromKey = concat(BALANCE_PREFIX, from_acct)
    fromBalance = Get(ctx, fromKey)
    if amount > fromBalance or amount < 0:
        return False

    approveKey = concat(concat(APPROVE_PREFIX,from_acct),spender)
    approvedAmount = Get(ctx,approveKey)
    toKey = concat(BALANCE_PREFIX,to_acct)

    if amount > approvedAmount:
        return False
    elif amount == approvedAmount:
        Delete(ctx,approveKey)
        Put(ctx, fromKey, Sub(fromBalance, amount))
    else:
        Put(ctx,approveKey, Sub(approvedAmount, amount))
        Put(ctx, fromKey, Sub(fromBalance, amount))

    toBalance = Get(ctx, toKey)
    Put(ctx, toKey, Add(toBalance, amount))

    TransferEvent(from_acct, to_acct, amount)

    return True


def allowance(owner, spender):
    """
    check how many token the spender is allowed to spend from owner account
    :param owner: token owner
    :param spender:  token spender
    :return: the allowed amount of tokens
    """
    key = concat(concat(APPROVE_PREFIX, owner), spender)
    return Get(ctx, key)


"""
use ong exchange CRC
"""
def exchange(address, amount):
    balance = ongBalance(contractAddress)
    if (balance + amount) > DEST_ONG:
        Notify(["exchange","DEST_ONG is reached"])
        return False
    res = transferOng(address, contractAddress, amount)
    Require(res)
    newSupply = callSupply(balance)
    totalSupply = getTotalSupply()
    returnCRCNum = Sub(newSupply, totalSupply)
    Put(ctx, SUPPLY_KEY, newSupply)
    key = concat(BALANCE_PREFIX, address)
    oldBalance = Get(ctx, key)
    Put(ctx, key, Add(oldBalance, returnCRCNum))
    ExchangeEvent(address, amount, returnCRCNum)
    

"""
use CRC redeem ong
"""
def redeem(address, amount):
    totalSupply = getTotalSupply()
    newSupply = Sub(totalSupply, amount)
    newOngNum = calOngNumBySupply(newSupply)
    balance = ongBalance(contractAddress)
    redeemOngNum = Sub(balance, newOngNum)
    res = transferOng(contractAddress, address, redeemOngNum)
    Require(res)
    RedeemEvent(address, amount)
    TransferEvent(contractAddress, address, redeemOngNum)
    

"""
x represent address(this).balance
totalSupply = initialRate * x - x^2/(2*k)
"""
def callSupply(x):
    opt1 = Mul(INIT_RATE, x)
    opt2 = Div(Mul(x, x), Mul(2, k))
    return Sub(opt1, opt2)


"""
because totalSupply = initialRate * x - x^2/(2*k), x represent address(this).balance
so, x = initialRate * k - sqrt((initialRate * k)^2 - 2 * k * totalSupply)
"""
def calOngNumBySupply(y):
    opt1 = Mul(INIT_RATE, k)
    sqrtOpt1 = Mul(opt1, opt1)
    sqrtOpt2 = Mul(2, Mul(k, y))
    sqrtRes = Sqrt(Sub(sqrtOpt1, sqrtOpt2))
    return Sub(Mul(INIT_RATE, k), sqrtRes)
    
    
def transferOng(fromAcct, toAcct, ongAmount):
    """
    transfer ONT
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    RequireWitness(fromAcct)
    param = state(fromAcct, toAcct, ongAmount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False
        
        
def ongBalance(address):
    ongBalance = Invoke(0, ONGAddress, 'balanceOf', state(address))
    return ongBalance
    
    
def getTotalSupply():
    return Get(ctx, SUPPLY_KEY)
