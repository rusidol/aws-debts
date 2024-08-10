from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DebtInSchema(BaseSchema):
    name: str


class DebtsInSchema(BaseSchema):
    debts: list[DebtInSchema]


class BaseReportSchema(BaseSchema):
    months: int
    principal_paid: float
    interest_paid: float
    total: float
    balance_history: list | None = None
    payment_history: list | None = None
    payments_remaining_history: list | None = None


class LoanReportSchema(BaseReportSchema):
    pass


class SummaryReportSchema(BaseReportSchema):
    payoff_strategy: str
    payoff_order: list[str]


class SummaryReportOutSchema(BaseSchema):
    loan_reports: list[LoanReportSchema]
    summary_report: SummaryReportSchema
    interest_saved: float | None = None
    months_saved: int | None = None
    debt_free_date: str | None = None

