from simulate import proceed
from schemas import DebtsInSchema
from datetime import datetime, date

body = {
  "extra": "10000.00",
  "strategy": "snowball",
  "debts": [
    {
      "name": "auto_loan",
      "min_payment": "62370.00",
      "balance": "2900000.00",
      "interest": "16.99",
      "next_pay_date": "2024-09-07"
    },
    {
      "name": "mortgage",
      "min_payment": "10000.00",
      "balance": "595000.00",
      "interest": "11.25",
      "next_pay_date": "2024-09-10"
    }
  ]
}


def main():
    if not DebtsInSchema.validate(body):
        return "Unprocessable entry"
    debts_schema_in = DebtsInSchema.model_validate(body)
    if not debts_schema_in.debts:
        return "Need to have a least one debt added"
    input_json = {debt.name: {"min_payment": debt.min_payment, "balance": debt.balance, "interest": debt.interest}
                  for debt in debts_schema_in.debts}

    output_schema = proceed(input_json, debts_schema_in.extra, datetime.date(datetime.now()))
    print(f"Interest saved: {output_schema.interest_saved}")
    print(f"Months saved: {output_schema.months_saved}")
    print(f"Debt free date: {output_schema.debt_free_date}")

main()