def get_page(session, page, model, url, query=None):
    if not query:
        query = {}
    query["page"] = page
    resp = session.get(url, params=query)
    output = []
    for data in resp.json():
        obj = model.from_dict(data)
        output.append(obj)
    pages = int(resp.headers.get("Pages", 0))
    return output, pages


def get_all(session, model, url, query=None):
    iter, pages = get_page(session, 1, model, url, query)
    yield from iter
    for i in range(2, pages + 1):
        obj, _ = get_page(session, i, model, url, query)
        yield from obj
