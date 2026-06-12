import time
import random
import requests
import json

# ── Config ───────────────────────────────────────────────────────────────────
TWEET_TARGET_URL = "https://x.com/i/status/2064724007094489549"  # ganti ini
TARGET_USER = "gloobiez_eth"  # ganti sama username yang di-follow

# MODE: "one" | "all" | "from"
MODE = "all"
ONE_INDEX = 1    # kalo MODE=one, akun ke berapa (mulai dari 1)
FROM_INDEX = 1   # kalo MODE=from, mulai dari akun ke berapa
# ─────────────────────────────────────────────────────────────────────────────

COMMENTS = [
    "looks interesting", "in", "this is huge", "lets go",
    "been waiting for this", "clean project", "aping in",
    "not missing this", "gotta be early", "this is it",
    "Looks interesting", "In", "This is huge", "Lets go",
    "Been waiting for this", "Clean project", "Aping in",
    "Not missing this", "Gotta be early", "This is it",
    "gLOObiez", "gLOObiez.",
]

BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
CREATE_TWEET_URL = "https://x.com/i/api/graphql/SoVnbfCycZ7fERGCwpZkYA/CreateTweet"

def load_file(path):
    with open(path, "r") as f:
        return [l.strip() for l in f.readlines() if l.strip()]

def get_session(auth_token, ct0):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {BEARER}",
        "X-Csrf-Token": ct0,
        "Content-Type": "application/json",
        "Origin": "https://x.com",
        "Referer": "https://x.com/home",
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "en",
    })
    s.cookies.set("auth_token", auth_token, domain=".x.com")
    s.cookies.set("ct0", ct0, domain=".x.com")
    return s

def get_user_id(session, username):
    r = session.get(
        "https://x.com/i/api/graphql/G3KGOASz96M-Qu0nwmGXNg/UserByScreenName",
        params={
            "variables": '{"screen_name":"' + username + '","withSafetyModeUserFields":true}',
            "features": '{"hidden_profile_likes_enabled":true,"hidden_profile_subscriptions_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_is_identity_verified_enabled":true,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"responsive_web_twitter_article_notes_tab_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}'
        }
    )
    return r.json()["data"]["user"]["result"]["rest_id"]

def follow(session, user_id):
    r = session.post(
        "https://api.twitter.com/1.1/friendships/create.json",
        data=f"user_id={user_id}&skip_status=true",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return r.status_code == 200

def like(session, tweet_id):
    r = session.post(
        "https://x.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet",
        json={"variables": {"tweet_id": tweet_id}, "queryId": "lI07N6Otwv1PhnEgXILM7A"}
    )
    return r.status_code == 200

def retweet(session, tweet_id):
    r = session.post(
        "https://x.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet",
        json={"variables": {"tweet_id": tweet_id, "dark_request": False}, "queryId": "ojPdsZsimiJrUGLR1sjUtA"}
    )
    return r.status_code == 200

def comment(session, tweet_id, text):
    payload = {
        "variables": {
            "tweet_text": text,
            "reply": {"in_reply_to_tweet_id": tweet_id, "exclude_reply_user_ids": []},
            "dark_request": False,
            "media": {"media_entities": [], "possibly_sensitive": False},
            "semantic_annotation_ids": []
        },
        "features": {
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": False,
            "tweet_awards_web_tipping_enabled": False,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "interactive_text_enabled": True,
            "responsive_web_text_conversations_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        },
        "queryId": "SoVnbfCycZ7fERGCwpZkYA"
    }
    r = session.post(CREATE_TWEET_URL, json=payload)
    if r.status_code != 200:
        raise Exception(f"Comment failed: {r.status_code} - {r.text[:200]}")
    result = r.json()["data"]["create_tweet"]["tweet_results"]["result"]
    comment_id = result["rest_id"]
    username = result["core"]["user_results"]["result"]["legacy"]["screen_name"]
    return f"https://twitter.com/{username}/status/{comment_id}"

def submit_claim(comment_url, evm_address):
    r = requests.post(
        "https://gloobiez.xyz/api/wl/claims",
        json={"commentUrl": comment_url, "evmAddress": evm_address},
        headers={"Content-Type": "application/json", "Origin": "https://gloobiez.xyz", "Referer": "https://gloobiez.xyz/"}
    )
    return r.json()

def get_tweet_id(url):
    return url.split("/status/")[1].split("?")[0]

def parse_token(line):
    auth_token = line.split("auth_token=")[1].split(";")[0].strip()
    ct0 = line.split("ct0=")[1].split(";")[0].strip()
    return auth_token, ct0

def main():
    tokens = load_file("tokens.txt")
    wallets = load_file("wallets.txt")
    tweet_id = get_tweet_id(TWEET_TARGET_URL)

    start, end = 0, len(tokens)
    if MODE == "one":
        start, end = ONE_INDEX - 1, ONE_INDEX
    elif MODE == "from":
        start = FROM_INDEX - 1

    print(f"Mode: {MODE} | Akun {start+1} - {end} dari {len(tokens)}")

    for i in range(start, end):
        token_line = tokens[i]
        wallet = wallets[i] if i < len(wallets) else None
        if not wallet:
            print(f"[{i+1}] Skip - wallet tidak ada")
            continue

        print(f"\n[{i+1}/{len(tokens)}] Processing...")

        try:
            auth_token, ct0 = parse_token(token_line)
            session = get_session(auth_token, ct0)

            # Follow
            user_id = get_user_id(session, TARGET_USER)
            follow(session, user_id)
            print("✓ Follow")
            time.sleep(random.uniform(2, 4))

            # Like
            like(session, tweet_id)
            print("✓ Like")
            time.sleep(random.uniform(2, 4))

            # Retweet
            retweet(session, tweet_id)
            print("✓ Retweet")
            time.sleep(random.uniform(2, 4))

            # Comment
            text = random.choice(COMMENTS)
            comment_url = comment(session, tweet_id, text)
            print(f"✓ Comment: \"{text}\"")
            print(f"  URL: {comment_url}")
            time.sleep(random.uniform(3, 6))

            # Submit claim
            claim = submit_claim(comment_url, wallet)
            done = claim.get("claim", {}).get("commentDone", False)
            print(f"✓ Claim: {'success' if done else json.dumps(claim)}")
            time.sleep(random.uniform(5, 10))

        except Exception as e:
            print(f"✗ Error akun {i+1}: {e}")

    print("\nDone!")

if __name__ == "__main__":
    main()
