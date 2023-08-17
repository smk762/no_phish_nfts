# No Phish NFTs

This repo serves an API to check if a domain or contract address has been identified as spam or otherwise malicious.

## Endpoints

[GET] `blocklist/contract/{network}/{address}` - Returns `true` (if contract is in block list) or `false`
[GET] `blocklist/domain/{domain}` - Returns `true` (if domain is in block list) or `false`
[GET] `blocklist/{network}/contract_list` - Returns the NFT contracts blocklist for a network
[GET] `blocklist/domain_list` - Returns domain blocklist

[POST] `blocklist/add_domain/{domain}` - Requires authentication. Adds a new domain to the domain block list.
[POST] `blocklist/add_contract/{network}/{address}` - Requires authentication. Adds a new contract to the NFT contracts block list.

## Crons

- Add block list sources to `sources.json`
- Setup a crontab entry like `0 0 * * 1 /home/user/no_phish_nfts/update_blocklists.sh` to refresh the lists every 24 hours.


