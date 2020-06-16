# Threebot authentication

## Gedis authentication

In order to access the gedis server, the user needs to send the following:

- Sign his data with his private key
- Sends his 3bot name
- This all should be encrypted by the public key of the server that he tries to connect to

The server upon recieving a request will do the following:

- Will decrypt the data using its private key, if that fails will abort
- Gets the public key of the 3bot name specified from the explorer
- Verifies the signed data with the public key if that fails will refuse the request

This follows the implementation  and flow described by [JSX_core_597](https://github.com/threefoldtech/jumpscaleX_core/pull/597) and [JSX_core_694](https://github.com/threefoldtech/jumpscaleX_core/pull/694/files)

## HTTP authentication

### Over threebot server

When a user attempts to access the gedis server from Threebot the server will redirect it to `threebot connect` and a session will be created for the user for further requests.

In that case since the user is verified by `threebot connect`, there will be no need for additional authentication and the described gedis authentication above will be skipped.

In order to ensure that this flow ensures the identity of the user there needs to be a link between the explorer server and the connect server.

### Direct HTTP

In this case gedis server will expect the same authentication model described above and it is up to the client to sign and encrypt his data before sending his request otherwise it will be refused.
