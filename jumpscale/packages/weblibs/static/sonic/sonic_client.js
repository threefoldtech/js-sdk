sonic_search = query => {
    return packageGedisClient.zerobot.webinterface.actors.wiki.find({ "name": NAME, "text": query })
        .then(res => res.json())
}
