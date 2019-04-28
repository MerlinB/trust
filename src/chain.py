from typing import List, Dict, Iterator


class Network:
    trusts: List['Trust'] = []

    @property
    def total(self) -> int:
        return sum([trust.amount for trust in self.trusts])

    @property
    def members(self) -> List['Member']:
        return list(dict.fromkeys([trust.donor for trust in self.trusts]
                    + [trust.trustee for trust in self.trusts]))

    def get_theft_profitabilities(self, amount) -> Dict['Member', float]:
        return {member: member.get_theft_profitability(amount)
                for member in self.members}

    def __str__(self) -> str:
        return f'{self.trusts}'

    __repr__ = __str__


class Member:
    def __init__(self, network: 'Network', name=None) -> None:
        self.name = name
        self.network = network

    @property
    def trusts_out(self) -> List['Trust']:
        return [trust for trust in self.network.trusts if trust.donor == self]

    @property
    def trusts_in(self) -> List['Trust']:
        return [trust for trust in self.network.trusts
                if trust.trustee == self]

    @property
    def trustees(self):
        return [trust.trustee for trust in self.trusts_out]

    @property
    def groups_possible(self) -> List['Group']:

        def find_groups(group):
            if self in group.members:
                yield group

            for next_group in group.extended_groups:
                for g in find_groups(next_group):
                    yield g

        groups: List['Group'] = []
        for member in self.network.members:
            groups += list(find_groups(Group(self.network, [member])))
        return groups

    def get_risk_group(self, amount) -> 'Group':
        return sorted(self.groups_possible, key=lambda group:
                      group.get_theft_profitability(amount))[-1]

    def get_theft_profitability(self, amount) -> float:
        return self.get_risk_group(amount).get_theft_profitability(amount)

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__


class Trust:
    def __init__(self, donor: 'Member', trustee: 'Member', amount: int):
        self.donor = donor
        self.trustee = trustee
        self.amount = amount

    def __str__(self) -> str:
        return f'{self.donor}->{self.amount}->{self.trustee}'

    __repr__ = __str__


class Group:
    def __init__(self, network: 'Network', members: List['Member']):
        self.members = members
        self.network = network

    @property
    def trustees(self) -> Iterator['Member']:
        for trust in self.network.trusts:
            if trust.donor in self.members:
                yield trust.trustee

    @property
    def investment(self) -> int:
        investment: int = 0
        for trust in self.network.trusts:
            if trust.donor in self.members or trust.trustee in self.members:
                investment += trust.amount
        return investment

    @property
    def collateral(self) -> int:
        costs: int = 0
        for trust in self.network.trusts:
            if trust.donor in self.members and \
                    trust.trustee not in self.members or \
                    trust.donor not in self.members and \
                    trust.trustee in self.members:
                costs += trust.amount
        return costs

    @property
    def extended_groups(self) -> Iterator['Group']:
        for trustee in self.trustees:
            if trustee not in self.members:
                yield Group(self.network, self.members + [trustee])

    def get_theft_profitability(self, amount) -> float:
        return (amount - self.collateral) / self.investment

    def __str__(self) -> str:
        return f'{self.members}'

    __repr__ = __str__
