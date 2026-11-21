from collections import defaultdict
from dataclasses import dataclass
import itertools

from hlogedu.search.problem import Problem
from hlogedu.search.common import ClassParameter


# Problem
##############################################################################


def _compute_balance(payments) -> dict[str, int]:
    balance = defaultdict(int) # default is 0
    for name, _, amount, participants in payments:
        k = len(participants)
        share = amount // k
        balance[name] += amount
        for participant in participants:
            balance[participant] -= share
        balance[name] -= amount - share * k # payer absorbs rounding
    assert sum(balance.values()) == 0
    return balance



class DebtSettlement(Problem):
    NAME = "debt-settlement"

    PARAMS = [
        ClassParameter(
            "file_",
            type=str,
            default=None,
            help="File with the payments CSV.",
        )
    ]

    def __init__(self, file_: str):
        super().__init__()

        self.participants = set()
        payments = []
        with open(file_) as fh:
            lines = iter(fh)
            # skip header
            next(lines)
            # Process each CSV line
            for line in lines:
                name, description, amount, participants = line.strip().split(";")
                amount = int(round(float(amount) * 100)) # convert to cents
                participants = participants.split(",")
                payments.append((name, description, amount, participants))
                self.participants.update(participants)
                self.participants.add(name)
        self.initial_balance = _compute_balance(payments)
    
    def initials(self):
        initials = []
        participants = sorted(self.participants)
        for i in participants:
            initials.append(self.initial_balance[i])
        return [tuple(initials)]
    
    def is_goal(self, state):
        for balance in state:
            if balance != 0:
                return False
        return True

    def actions(self, state):
        ret = []
        debtors = [] #deutors
        creditors = [] #cobradors
        for i in range(len(state)):
            balance = state[i]
            if balance < 0:
                debtors.append((i, balance))
            elif balance > 0:
                creditors.append((i, balance))
        for num, debt in debtors:
            for num2, pay in creditors:
                ret.append((num, num2, min(-debt, pay)))
        return ret

    def result(self, state, action):
        debtor, creditor, amount = action
        new_state = list(state)
        new_state[debtor] += amount
        new_state[creditor] -= amount
        return tuple(new_state)

    def cost(self, s, a):
        return 1
