import ujson

from .schemas import DebtsInSchema


# import requests


def lambda_handler(event, context):

    body = ujson.loads(event["body"])

    if not DebtsInSchema.validate(body):
        return {
            "statusCode": 422,
            "body": ujson.dumps(
                    {
                        "message": "Unprocessable entry"
                    }
            )
        }


