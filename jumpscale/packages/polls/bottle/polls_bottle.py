from bottle import Bottle

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import admin_only, login_required
from jumpscale.packages.polls.chats.threefold import VOTES
from jumpscale.sals.chatflows.polls import all_users

app = Bottle()


def _map_vote_results(user_votes, votes_questions):
    votes_data = {}
    for question_name, answers in user_votes.items():
        for question in votes_questions.values():
            if question["title"] == question_name:
                answer = answers.index(1)
                votes_data[question_name] = question["options"][answer]
    return votes_data


@app.route("/api/results")
@login_required
@admin_only
def results():
    votes_data = {}
    for voter_name in all_users.list_all():
        voter = all_users.get(voter_name)
        votes_data[j.data.text.removeprefix(voter_name, "threefold_")] = _map_vote_results(voter.vote_data, VOTES)

    votes_data["-Number of voters"] = all_users.count
    return votes_data


@app.route("/api/names")
@login_required
@admin_only
def names():
    data = {"names": []}
    for voter_name in all_users.list_all():
        voter = all_users.get(voter_name)
        tname = j.data.text.removeprefix(voter_name, "threefold_")
        data["names"].append(voter.extra_data.get("full_name", tname))
    data["-Number of voters"] = all_users.count
    return data
