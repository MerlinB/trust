import pytest

from chain.chain import Network, Member, Trust, Group


@pytest.fixture()
def network():
    return Network()


class TestRisk:
    def test_profit(self, network):
        A = Member(network=network, name='A')
        B = Member(network=network, name='B')
        network.trusts += [
            Trust(A, B, 100),
        ]
        assert A.get_theft_profitability(100) == 1
        assert A.get_theft_profitability(200) == 2
        assert Group(network, [A]).get_theft_profitability(100) == 0
        assert Group(network, [A]).get_theft_profitability(200) == 1

    def test_risk_group(self, network):
        A = Member(network=network)
        B = Member(network=network)
        C = Member(network=network)
        network.trusts += [
            Trust(A, B, 100),
            Trust(B, C, 1000)
        ]
        assert A.get_risk_group(200).members == [A]
        assert A.get_risk_group(100).members == [A, B, C]
