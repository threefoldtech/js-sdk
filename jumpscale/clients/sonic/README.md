# Sonic server client
Sonic is a fast, lightweight and schema-less search backend. It ingests search texts and identifier tuples that can then be queried against in a microsecond's time.
read the docs [here](https://github.com/valeriansaliou/sonic)
## usage example:
first make sure that you have sonic server running
to populate data:
```python
    data = { 
         'post:1': "this is some test text hello", 
         'post:2': 'this is a hello world post', 
         'post:3': "hello how is it going?", 
         'post:4': "for the love of god?", 
         'post:5': "for the love lorde?", 
     } 
     client = j.clients.sonic.get('main') 
     for articleid, content in data.items(): 
         client.push("forum", "posts", articleid, content) 
```
to query or getting suggestions:
```python
    print(client.query("forum", "posts", "love")) 

    # ['post:5', 'post:4']

    print(client.suggest("forum", "posts", "lo"))                                
    # ['lorde', 'love']
```