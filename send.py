import json #標準のjsonモジュールの読み込み
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み

CK = "51r5HQvY8V939P7VB7fuAJt7p"
CS = "gekTiCOciiD4JBuaduiKVrHQpnRoXO4frwHfRxuUK0CYyTIdlF"
AT = "2361825306-lvaatJZlw2F848Y631wgWfP0jRFA412IhUEfLDz"
ATS = "TkXLZhyhswSAQgRc9F8fm4qWLjuKUMa9ADusvxo78saTo"

twitter = OAuth1Session(CK, CS, AT, ATS)

def post_dm(text, name=972379651761782786):
    url = 'https://api.twitter.com/1.1/direct_messages/events/new.json'
    headers = {'content-type': 'application/json'}
    target_id = name #nameを処理
    payload = {"event": {"type": "message_create","message_create": {"target": {"recipient_id": target_id }, "message_data": {"text": text}}}}
    data = json.dumps(payload)
    return twitter.post(url, headers=headers, data=data)

def post_tweet(text):
    url = "https://api.twitter.com/1.1/statuses/update.json"
    params = {"status": text}
    return twitter.post(url, params = params)

def get_tl():
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    return twitter.get(url)

def get_followers(list_or_ids, count):
    url = "https://api.twitter.com/1.1/followers/{}.json".format(list_or_ids)
    params = {"count": count}
    return twitter.get(url)

def get_retweeters(tweet_id):
    url = "https://api.twitter.com/1.1/statuses/retweeters/ids.json"
    params = {"id": tweet_id}
    return twitter.get(url, params = params)

post_dm("はちじだよ")
