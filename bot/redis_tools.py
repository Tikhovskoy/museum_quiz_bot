import os

import redis


def get_redis_client():
    return redis.Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ["REDIS_PORT"]),
        password=os.environ["REDIS_PASSWORD"],
        decode_responses=True,
    )


def save_user_question(client, user_id, question, platform):
    client.set(f"user:{platform}:{user_id}:question", question)


def get_user_question(client, user_id, platform):
    return client.get(f"user:{platform}:{user_id}:question")


def increase_user_score(client, user_id, platform):
    return client.incr(f"user:{platform}:{user_id}:score")


def get_user_score(client, user_id, platform):
    score = client.get(f"user:{platform}:{user_id}:score")
    return int(score) if score else 0
