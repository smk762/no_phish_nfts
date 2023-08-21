from enum import Enum

class MnemonicHqNetworkEnum(str, Enum):
    ethereum = "ethereum"
    polygon = "polygon"
    
    def __str__(self) -> str:
        return str.__str__(self)


class AlchemyNetworkEnum(str, Enum):
    ethereum = "eth"
    polygon = "polygon"
    
    def __str__(self) -> str:
        return str.__str__(self)


class NetworkEnum(str, Enum):
    # If adding more, match to Moralis API chains
    avalanche = "avalanche"
    binance = "bsc"
    ethereum = "ethereum"
    fantom = "fantom"
    polygon = "polygon"
    solana = "solana"
    def __str__(self) -> str:
        return str.__str__(self)