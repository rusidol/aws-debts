import ujson

from schemas import DebtsInSchema


# import requests


def lambda_handler(event, context):
    try:
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
        return {
                "statusCode": 200,
                "body": ujson.dumps(
                        {
                            "message": "It works!"
                        }
                )
            }
    except KeyError:
        return {
            "statusCode": 400,
            "body": ujson.dumps(
                    {
                        "message": "Bad request"
                    }
            )
        }


