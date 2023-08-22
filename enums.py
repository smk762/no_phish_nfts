from enum import Enum, EnumMeta


class CaseInsensitiveKeys(EnumMeta):
    def __getitem__(cls, item):
        try:
            return super().__getitem__(item)
        except:
            for key in cls._member_map_.keys():
                if key.casefold() == item.casefold():
                    return super().__getitem__(key)

    def __str__(self) -> str:
        return str.__str__(self)


class MnemonicHqNetworkEnum(str, Enum, metaclass=CaseInsensitiveKeys):
    ethereum = "eth"
    polygon = "polygon"


class AlchemyNetworkEnum(str, Enum, metaclass=CaseInsensitiveKeys):
    ethereum = "eth"
    polygon = "polygon"


class MoralisNetworkEnum(str, Enum, metaclass=CaseInsensitiveKeys):
    avalanche = "avalanche"
    binance = "bsc"
    ethereum = "eth"
    fantom = "fantom"
    polygon = "polygon"


class NetworkEnum(str, Enum, metaclass=CaseInsensitiveKeys):
    avalanche = "avalanche"
    binance = "bsc"
    ethereum = "eth"
    fantom = "fantom"
    polygon = "polygon"
    solana = "solana"
