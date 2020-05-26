def main():
    import os
    from jumpscale.god import j

    with open("test_index.db", "w"):
        pass

    print(os.system("redis-cli --scan  --pattern 'test.indexer.quote.id://*' | xargs redis-cli del"))
    print(os.system("redis-cli --scan  --pattern 'test.quote://*' | xargs redis-cli del"))
    print(os.system("redis-cli --scan  --pattern 'test.quote.las*' | xargs redis-cli del"))
    print(os.system("redis-cli --scan  --pattern 'test.indexer.employee.id://*' | xargs redis-cli del"))
    print(os.system("redis-cli --scan  --pattern 'test.employee://*' | xargs redis-cli del"))
    print(os.system("redis-cli --scan  --pattern 'test.employee.las*' | xargs redis-cli del"))
    print(os.system("redis-cli --scan  --pattern 'test.indexer.db.id://*' | xargs redis-cli del"))
    print(os.system("redis-cli --scan  --pattern 'test.db://*' | xargs redis-cli del"))
    print(os.system("redis-cli --scan  --pattern 'test.db.las*' | xargs redis-cli del"))
    j.clients.sonic.get("test").flush_collection("test")


if __name__ == "__main__":
    main()
