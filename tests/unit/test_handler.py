import json

import pytest

from hello_world import app


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""
    return {"body":"{\"extra\":\"10000.00\",\"strategy\":\"snowball\",\"debts\":[{\"name\":\"auto_loan\",\"min_payment\":\"62370.00\",\"balance\":\"2900000.00\",\"interest\":\"16.99\",\"next_pay_date\":\"2024-09-07\"},{\"name\":\"mortgage\",\"min_payment\":\"10000.00\",\"balance\":\"595000.00\",\"interest\":\"11.25\",\"next_pay_date\":\"2024-09-10\"}]}"}


def test_lambda_handler(apigw_event):

    response = app.lambda_handler(apigw_event, "")
    data = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert "data" in response["body"]
    assert "status" in response["body"]
    assert data["status"] == "ok"
