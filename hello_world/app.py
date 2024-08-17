import datetime

import ujson

from schemas import DebtsInSchema
from simulate import proceed
from datetime import datetime, date
# import requests


def create_response_message(status_code: int, message: str) -> dict:
    return {
        "statusCode": status_code,
        "body": ujson.dumps(
                {
                    "status": "error",
                    "data": message
                }
        )
    }


def lambda_handler(event, context):
    try:
        body = ujson.loads(event["body"])
        if not DebtsInSchema.validate(body):
            return create_response_message(422, "Unprocessable entry")
        debts_schema_in = DebtsInSchema.model_validate(body)
        if not debts_schema_in.debts:
            return create_response_message(400, "Need to have a least one debt added")
        input_json = {debt.name: {"min_payment": debt.min_payment, "balance": debt.balance, "interest": debt.interest}
                      for debt in debts_schema_in.debts}

        output_schema = proceed(input_json, debts_schema_in.extra, datetime.date(datetime.now()))
        if not output_schema:
            create_response_message(400, "Something went wrong")
        return {
                "statusCode": 200,
                "body": ujson.dumps(
                        {
                            "status": "ok",
                            "data": {
                                "Interest saved:": output_schema.interest_saved,
                                "Months saved:": output_schema.months_saved,
                                "Debt free date:": output_schema.debt_free_date,
                            }
                        }
                )
            }
    except KeyError:
        return create_response_message(400, "Bad request")


