def convert_url_to_class_name(url):
    urlparts = url.split(".")
    return "".join(x.capitalize() for x in urlparts)
