import os

import redis

redis_client = None


def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=int(os.environ["REDIS_PORT"]),
            password=os.environ["REDIS_PASSWORD"],
            decode_responses=True,
        )
    return redis_client


def save_user_question(user_id, question, platform):
    client = get_redis_client()
    client.set(f"user:{platform}:{user_id}:question", question)


def get_user_question(user_id, platform):
    client = get_redis_client()
    return client.get(f"user:{platform}:{user_id}:question")


def increase_user_score(user_id, platform):
    client = get_redis_client()
    return client.incr(f"user:{platform}:{user_id}:score")


def get_user_score(user_id, platform):
    client = get_redis_client()
    score = client.get(f"user:{platform}:{user_id}:score")
    return int(score) if score else 0
