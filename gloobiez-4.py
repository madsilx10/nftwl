import time
import random
import requests
import json
import os

# ── Config ───────────────────────────────────────────────────────────────────
TWEET_TARGET_URL = "https://x.com/i/status/2064724007094489549"
TARGET_USER = "gloobiez_eth"
DONE_FILE = "done.txt"  # nyimpen akun yang udah selesai: index|comment_url
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

def load_file(path):
    with open(path, "r") as f:
        return [l.strip() for l in f.readlines() if l.strip()]

def load_done():
    done = {}
    if not os.path.exists(DONE_FILE):
        return done
    with open(DONE_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if "|" in line:
                idx, url = line.split("|", 1)
                done[int(idx)] = url
    return done

def save_done(idx, comment_url):
    with open(DONE_FILE, "a") as f:
        f.write(f"{idx}|{comment_url}\n")

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
            "variables": json.dumps({"screen_name": username, "withSafetyModeUserFields": True}),
            "features": json.dumps({
                "hidden_profile_likes_enabled": True,
                "hidden_profile_subscriptions_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "subscriptions_verification_info_is_identity_verified_enabled": True,
                "subscriptions_verification_info_verified_since_enabled": True,
                "highlights_tweets_tab_ui_enabled": True,
                "responsive_web_twitter_article_notes_tab_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
            })
        }
    )
    data = r.json()
    if "data" not in data or "user" not in data["data"]:
        raise Exception(f"get_user_id gagal: {json.dumps(data)[:200]}")
    return data["data"]["user"]["result"]["rest_id"]

def follow(session, user_id):
    r = session.post(
        "https://api.twitter.com/1.1/friendships/create.json",
        data=f"user_id={user_id}&skip_status=true",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if r.status_code != 200:
        raise Exception(f"Follow gagal: {r.status_code} - {r.text[:150]}")
    result = r.json()
    if "id" not in result and "id_str" not in result:
        raise Exception(f"Follow gagal: {json.dumps(result)[:150]}")

def like(session, tweet_id):
    r = session.post(
        "https://x.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet",
        json={"variables": {"tweet_id": tweet_id}, "queryId": "lI07N6Otwv1PhnEgXILM7A"}
    )
    if r.status_code != 200:
        raise Exception(f"Like gagal: {r.status_code} - {r.text[:150]}")
    data = r.json()
    if "data" not in data:
        raise Exception(f"Like gagal: {json.dumps(data)[:150]}")

def retweet(session, tweet_id):
    r = session.post(
        "https://x.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet",
        json={"variables": {"tweet_id": tweet_id, "dark_request": False}, "queryId": "ojPdsZsimiJrUGLR1sjUtA"}
    )
    if r.status_code != 200:
        raise Exception(f"RT gagal: {r.status_code} - {r.text[:150]}")
    data = r.json()
    if "data" not in data:
        raise Exception(f"RT gagal: {json.dumps(data)[:150]}")

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
    r = session.post(
        "https://x.com/i/api/graphql/SoVnbfCycZ7fERGCwpZkYA/CreateTweet",
        json=payload
    )
    if r.status_code != 200:
        raise Exception(f"Comment gagal: {r.status_code} - {r.text[:150]}")
    data = r.json()
    if "data" not in data or "create_tweet" not in data["data"]:
        raise Exception(f"Comment gagal: {json.dumps(data)[:200]}")
    result = data["data"]["create_tweet"]["tweet_results"]["result"]
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
    done = load_done()
    tweet_id = get_tweet_id(TWEET_TARGET_URL)

    print(f"\nTotal akun: {len(tokens)} | Sudah selesai: {len(done)}")
    print("Mode:")
    print("  1. 1 akun")
    print("  2. Semua akun")
    print("  3. Dari akun ke-N sampai akhir")
    mode_input = input("Pilih [1/2/3]: ").strip()

    if mode_input == "1":
        idx = int(input(f"Akun ke- (1-{len(tokens)}): ")) - 1
        start, end = idx, idx + 1
    elif mode_input == "2":
        start, end = 0, len(tokens)
    elif mode_input == "3":
        start = int(input(f"Mulai dari akun ke- (1-{len(tokens)}): ")) - 1
        end = len(tokens)
    else:
        print("Pilihan tidak valid.")
        return

    user_id_cache = {}

    for i in range(start, end):
        token_line = tokens[i]
        wallet = wallets[i] if i < len(wallets) else None
        if not wallet:
            print(f"\n[{i+1}/{len(tokens)}] Skip - wallet tidak ada")
            continue

        print(f"\n[{i+1}/{len(tokens)}] Processing...")

        try:
            auth_token, ct0 = parse_token(token_line)
            session = get_session(auth_token, ct0)

            # Cek apakah akun sudah komen sebelumnya
            if i in done:
                comment_url = done[i]
                print(f"  Skip komen - udah ada: {comment_url}")
            else:
                # Follow
                if TARGET_USER not in user_id_cache:
                    user_id_cache[TARGET_USER] = get_user_id(session, TARGET_USER)
                follow(session, user_id_cache[TARGET_USER])
                print("  ✓ Follow")
                time.sleep(random.uniform(2, 4))

                # Like
                like(session, tweet_id)
                print("  ✓ Like")
                time.sleep(random.uniform(2, 4))

                # Retweet
                retweet(session, tweet_id)
                print("  ✓ Retweet")
                time.sleep(random.uniform(2, 4))

                # Comment
                text = random.choice(COMMENTS)
                comment_url = comment(session, tweet_id, text)
                print(f"  ✓ Comment: \"{text}\"")
                print(f"  ✓ URL: {comment_url}")
                save_done(i, comment_url)
                time.sleep(random.uniform(3, 6))

            # Submit claim
            claim = submit_claim(comment_url, wallet)
            done_flag = claim.get("claim", {}).get("commentDone", False)
            if done_flag:
                print(f"  ✓ Claim: success")
            else:
                print(f"  ✗ Claim: {json.dumps(claim)}")

            time.sleep(random.uniform(5, 10))

        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\nDone!")

if __name__ == "__main__":
    main()
