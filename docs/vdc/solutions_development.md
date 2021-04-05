# Introduction
This guide should help you to develop a solution, integrate it with threefold connect service, update the helm chart to use and create pipeline to automate the process.

# steps
## preparing repo
Either create your repo or prepare a fork.

## threefold connect
To integrate threefold connect, we have two options:
- Integrate with our [Oauth Proxy Service](https://github.com/threefoldtech/oauth-proxy), this is the easy path.
following these [examples](https://github.com/threefoldtech/oauth-proxy/tree/master/examples)


- Implement the whole authentication service in your code, this is more optimized but more challenging.
    - Redirect the user to `"https://login.threefold.me` with these parameters `state,appid,scope,redirecturl,publickey`

        - `state`: Which is a random alphanumeric string, then store it in the session to be used later
        - `publickey`: Your `threebot` public key used for  authentication.
        - `scope`: Scope is a mechanism to limit an     application's access to a user's account. An    application can request one or more scopes, this   information is then presented to the user in the  consent screen.
        - `redirecturl`: URL inside your application will be used for redirection after the authentication
        - `appid`: Domain name for your application.
        example
        `https://www.domain-name.com` so the domain is  `domain-name`

        example:
        ``` python
        params = {
                "state": state,
                "appid": request.get_header("host"),
                "scope": json.dumps({"user": True, "email":     True}),
                "redirecturl": "/callback",
                "publickey": data["publickey"].encode(),
            }
            params = urlencode(params)
            redirect(f"{REDIRECT_URL}?{params}", code=302)
        ```

    - After the authentication, you will be redirected to the endpoint specified in the previous params, you will do the following steps in your callback method
        - You will get the `signAttempt` from the request parameters
        - You will get the `state` which was stored in the session
        - You will get the `username` from the request parameters
        - send request to `https://login.threefold.me/api/users/{username}` to verify the user and get the user public key
        - Use the public key to verify the `signAttemp` and get user data
            - Verify `state`
            - Verify `sei` using `openkyc`
            - Now, you have the `email` and `username` ready and verified

            full example for the method
            ```python
            def verify():

                is_json = "application/json" in request.headers         ["Content-Type"]
                if is_json:
                    request_data = request.json
                else:
                    request_data = request.params

                data = request_data.get("signedAttempt")
                # Get the state from the session
                state = "<get_state_from_session>"

                if not data:
                    return abort(400, "signedAttempt parameter is           missing")

                if not is_json:
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        return abort(400, "signedAttempt not in correct             format")

                if "signedAttempt" not in data:
                    return abort(400, "signedAttempt value is missing")

                username = data.get("doubleName")

                if not username:
                    return abort(400, "DoubleName is missing")

                res = requests.get(f"https://login.threefold.me/api/            users/{username}", {"Content-Type": "application/json"})
                if res.status_code != 200:
                    return abort(400, "Error getting user pub key")

                pub_key = nacl.signing.VerifyKey(res.json()["publicKey"]            , encoder=nacl.encoding.Base64Encoder)

                # verify data
                signedData = data["signedAttempt"]

                verifiedData = pub_key.verify(base64.b64decode          (signedData)).decode()

                data = json.loads(verifiedData)

                if "doubleName" not in data:
                    return abort(400, "Decrypted data does not contain          (doubleName)")

                if "signedState" not in data:
                    return abort(400, "Decrypted data does not contain          (state)")

                if data["doubleName"] != username:
                    return abort(400, "username mismatch!")

                # verify state
                signed_state = data.get("signedState", "")
                if state != signed_state:
                    return abort(400, "Invalid state. not matching one          in user session")

                nonce = base64.b64decode(data["data"]["nonce"])
                ciphertext = base64.b64decode(data["data"]["ciphertext"]            )

                try:
                    box = Box(PRIV_KEY.to_curve25519_private_key(),             pub_key.to_curve25519_public_key())
                    decrypted = box.decrypt(ciphertext, nonce)
                except nacl.exceptions.CryptoError:
                    return abort(400, "Error decrypting data")

                try:
                    result = json.loads(decrypted)
                except json.JSONDecodeError:
                    return abort(400, "3bot login returned faulty data")

                if "email" not in result:
                    return abort(400, "Email is not present in data")

                email = result["email"]["email"]

                sei = result["email"]["sei"]
                res = requests.post(
                    "https://openkyc.live/verification/verify-sei",
                    headers={"Content-Type": "application/json"},
                    json={"signedEmailIdentifier": sei},
                )

                if res.status_code != 200:
                    return abort(400, "Email is not verified")

                return {"email": email, "username": username}
            ```


## vdc integration (chatflow and Helm chart)
- Create a chat flow for your solution  under `jumpscale/packages/vdc_dashboard/chats/solution_name.py`

[examples](https://github.com/threefoldtech/js-sdk/blob/development/jumpscale/packages/vdc_dashboard/chats) for complete chatflows

- Add helm chart for your solution, following this [guide](https://github.com/threefoldtech/vdc-solutions-charts)


## Build image
- After you have completed your development, you have to build and push a versioned docker image.

## pipeline
- Create a pipeline to automate building and pushing your docker images upon any update to the repo .
following this [example](https://github.com/crystaluniverse/tf-owncloud/blob/master/.github/workflows/main.yml)
