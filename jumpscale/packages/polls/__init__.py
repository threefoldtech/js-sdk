"""Polls Package

## Installation

- Configure a wallet using stellar client named "polls_receive" and update the trustlines see: [Quick Start](https://github.com/threefoldtech/js-sdk/blob/9411bf6a359c88994475d4f90c412c1112d3487d/docs/wiki/quick_start.md#L77)

- Note: if you want to deploy test instance make sure the wallet's network is "TEST", for production use "STD"
- Note: Make sure to activate the wallet and update trust lines

- and its name tp polls.py
  ```python
  WALLET_NAME = "polls_receive"
  ```

- Start 3Bot server and add the package

- polls now available at http://localhost/polls/chats/<poll_name>


## Create new poll

- check one of the examples

  - Default questions will be added in self.QUESTIONS variable
  - custom vote allows you to add your custom questions just update the dicts and return of it

"""
