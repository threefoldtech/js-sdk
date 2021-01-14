# Adding tokens to a stellar wallet

## Tokens available

At the time of writting, there are three types of tokens available:

- [FreeTFT](https://github.com/threefoldfoundation/tft-stellar/#freetft)
- [TFT](https://github.com/threefoldfoundation/tft-stellar/#tft)
- [TFTA](https://github.com/threefoldfoundation/tft-stellar/#tfta)


## Getting some tokens

The FreeTFT's is a special token that has been created to allow developers and interested parties to play with the grid for free using free capacity by certain farmers.

To watch a quick video with the next steps go to [Create wallet and exchange in JS-NG](https://www.youtube.com/watch?v=HGkB7bunbTw&feature=youtu.be)

To get yourself FreeTFTs and TFTs on testnet network you can follow the following steps where you create a wallet and configure it:


## From the admin dashboard

From your 3bot (local or deployed on the grid) you can go to wallet manager and create a new wallet (will be test if you are using identity against testnet) and it will add the trustlines and activate using threefold services
![admin walletmanager](../images/walletmanager.jpg)

and after creating a new wallet it will be funded with 10000 XLM
![admin walletdetails](../images/walletdetails.jpg)


- To get TFTs we can sell from the XLM tokens in the wallet in exchange for TFTs by following the next steps:
    - Access [https://testnet.interstellar.exchange/app](https://testnet.interstellar.exchange/app) and proceed with the steps until you can **Enter Account**.

        ![start](../images/interstellar_start.png)

    - Enter a password for your current session. **Please keep it saved safely**
    ![new_session](../images/interstellar_new_session.png)

    - Click on Import your wallet
    ![import_wallet_button](../images/interstellar_import_wallet_button.png)

    - Enter the wallet secret you obtained from the wallet instance you created in the jsng shell
    ![import_wallet](../images/interstellar_import_wallet.png)

    - Click on **trading** from the sidebar
    ![home](../images/interstellar_home.png)

    - Click on the last item on the right from the top bar then choose the exchange tokens to be from XLM to TFT. If it is not shown click on my assets in the pop up menu to choose TFT from the assets you have setup in the wallet
    ![trading_assets](../images/interstellar_trading_assets.png)

    - Choose the from the available the XLM you will be selling then click on the number or percentage from the amount wanted and click on **SELL XLM**
    ![sell_xlm](../images/interstellar_sell_xlm.png)

    - Enter the session secret you chose earlier and submit the sell request.
    ![sign_transaction](../images/interstellar_sign_transaction.png)

    - You should now have the TFTs you bought in your wallet.

        ```python
        JS-NG> wallet.get_balance()
        Balances
            1000.0000000 FreeTFT:GBLDUINEFYTF7XEE7YNWA3JQS4K2VD37YU7I2YAE7R5AHZDKQXSS2J6R
            429.1627121 TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3
            8999.9999650 XLM
        ```

You are now ready with a new wallet with the required TFT and FreeTFT
