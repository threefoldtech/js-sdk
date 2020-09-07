# Adding validator in the chatflow 

For instance we want to add validation for input from the user for valid git urls

## step 1

Go to packages/chatflows/frontend/field.js, there you will find the common validators and validators by type e.g for string, and for int.

## Step 2

in string_ask validation we add new section

```javascript
        is_git_url: (field) => {
            let str = field.val
            let regex = /(?:git|ssh|https?|git@[-\w.]+):(\/\/)?(.*?)(\.git)(\/?|\#[-\d\w._]+?)$/;
            if (!regex.test(str)) {
                return "Invalid URL. should be a valid git repository URL";
            };
            return true;
        },
```

