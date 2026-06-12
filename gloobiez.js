const axios = require("axios");
const fs = require("fs");

const TWEET_URL = "https://twitter.com/intent/tweet"; // ganti sama link tweet target
const TARGET_USER = "gloobiez"; // ganti sama username yang di-follow

const comments = [
  "looks interesting",
  "in",
  "this is huge",
  "lets go",
  "been waiting for this",
  "clean project",
  "aping in",
  "not missing this",
  "gotta be early",
  "this is it",
  "Looks interesting",
  "In",
  "This is huge",
  "Lets go",
  "Been waiting for this",
  "Clean project",
  "Aping in",
  "Not missing this",
  "Gotta be early",
  "This is it",
  "gLOObiez",
  "gLOObiez.",
];

const tokens = fs.readFileSync("tokens.txt", "utf8").trim().split("\n");
const wallets = fs.readFileSync("wallets.txt", "utf8").trim().split("\n");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const random = (arr) => arr[Math.floor(Math.random() * arr.length)];

async function twitterRequest(method, url, data, token) {
  const headers = {
    authorization: "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I7BeIgXBO3g%3DUcf9IbT6Xp5Bfj6RKxVF2x5JJSumjWwYPAz6rS4yxUyF2tVrqmAy2Y",
    "x-csrf-token": token.split("ct0=")[1]?.split(";")[0] || "",
    cookie: token,
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
    "x-twitter-active-user": "yes",
    "x-twitter-auth-type": "OAuth2Session",
    "x-twitter-client-language": "en",
  };
  return axios({ method, url, data, headers });
}

async function follow(token, userId) {
  return twitterRequest(
    "POST",
    "https://api.twitter.com/1.1/friendships/create.json",
    `user_id=${userId}&skip_status=true`,
    token
  );
}

async function likeTweet(token, tweetId) {
  return twitterRequest(
    "POST",
    "https://api.twitter.com/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet",
    { variables: { tweet_id: tweetId } },
    token
  );
}

async function retweet(token, tweetId) {
  return twitterRequest(
    "POST",
    "https://api.twitter.com/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet",
    { variables: { tweet_id: tweetId, dark_request: false } },
    token
  );
}

async function postComment(token, tweetId, text) {
  const res = await twitterRequest(
    "POST",
    "https://api.twitter.com/graphql/a1p9RWpkYKBjWv_I3WzS-A/CreateTweet",
    {
      variables: {
        tweet_text: text,
        reply: { in_reply_to_tweet_id: tweetId, exclude_reply_user_ids: [] },
        dark_request: false,
        media: { media_entities: [], possibly_sensitive: false },
        semantic_annotation_ids: [],
      },
      features: {
        tweetypie_unmention_optimization_enabled: true,
        responsive_web_edit_tweet_api_enabled: true,
        graphql_is_translatable_rweb_tweet_is_translatable_enabled: true,
        view_counts_everywhere_api_enabled: true,
        longform_notetweets_consumption_enabled: true,
        responsive_web_twitter_article_tweet_consumption_enabled: false,
        tweet_awards_web_tipping_enabled: false,
        longform_notetweets_rich_text_read_enabled: true,
        longform_notetweets_inline_media_enabled: true,
        responsive_web_graphql_exclude_directive_enabled: true,
        verified_phone_label_enabled: false,
        freedom_of_speech_not_reach_apply_enabled: true,
        standardized_nudges_misinfo: true,
        tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled: false,
        responsive_web_graphql_skip_user_profile_image_extensions_enabled: false,
        responsive_web_graphql_timeline_navigation_enabled: true,
        interactive_text_enabled: true,
        responsive_web_text_conversations_enabled: false,
        responsive_web_enhance_cards_enabled: false,
      },
    },
    token
  );
  const tweetResult = res.data?.data?.create_tweet?.tweet_results?.result;
  const commentId = tweetResult?.rest_id;
  const username = tweetResult?.core?.user_results?.result?.legacy?.screen_name;
  return `https://twitter.com/${username}/status/${commentId}`;
}

async function submitClaim(commentUrl, evmAddress) {
  return axios.post(
    "https://gloobiez.xyz/api/wl/claims",
    { commentUrl, evmAddress },
    { headers: { "content-type": "application/json", origin: "https://gloobiez.xyz", referer: "https://gloobiez.xyz/" } }
  );
}

async function getUserId(token, username) {
  const res = await twitterRequest(
    "GET",
    `https://api.twitter.com/1.1/users/show.json?screen_name=${username}`,
    null,
    token
  );
  return res.data.id_str;
}

async function getTweetId(tweetUrl) {
  return tweetUrl.split("/status/")[1]?.split("?")[0];
}

async function main() {
  const TWEET_TARGET_URL = "GANTI_LINK_TWEET_TARGET"; // ganti ini
  const tweetId = await getTweetId(TWEET_TARGET_URL);

  // MODE: "one" | "all" | "from"
  const MODE = "all";
  const ONE_INDEX = 1;   // kalo MODE=one, akun ke berapa (mulai dari 1)
  const FROM_INDEX = 1;  // kalo MODE=from, mulai dari akun ke berapa

  let start = 0;
  let end = tokens.length;

  if (MODE === "one") {
    start = ONE_INDEX - 1;
    end = ONE_INDEX;
  } else if (MODE === "from") {
    start = FROM_INDEX - 1;
  }

  console.log(`Mode: ${MODE} | Akun ${start + 1} - ${end} dari ${tokens.length}`);

  for (let i = start; i < end; i++) {
    const token = tokens[i].trim();
    const wallet = wallets[i]?.trim();
    if (!token || !wallet) continue;

    console.log(`\n[${i + 1}/${tokens.length}] Processing...`);

    try {
      // Follow
      const userId = await getUserId(token, TARGET_USER);
      await follow(token, userId);
      console.log("✓ Follow");
      await sleep(2000 + Math.random() * 2000);

      // Like
      await likeTweet(token, tweetId);
      console.log("✓ Like");
      await sleep(2000 + Math.random() * 2000);

      // Retweet
      await retweet(token, tweetId);
      console.log("✓ Retweet");
      await sleep(2000 + Math.random() * 2000);

      // Comment
      const commentText = random(comments);
      const commentUrl = await postComment(token, tweetId, commentText);
      console.log(`✓ Comment: "${commentText}"`);
      console.log(`  URL: ${commentUrl}`);
      await sleep(3000 + Math.random() * 3000);

      // Submit claim
      const claim = await submitClaim(commentUrl, wallet);
      console.log("✓ Claim submitted:", claim.data?.claim?.commentDone ? "success" : "check response");
      await sleep(5000 + Math.random() * 5000);
    } catch (err) {
      console.error(`✗ Error akun ${i + 1}:`, err.response?.data || err.message);
    }
  }

  console.log("\nDone!");
}

main();
