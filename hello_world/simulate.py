#!/usr/bin/env python3
"""Simulate loan payment methods to find the optimal way to pay of loans.

Payment Priority Methods:
 - Avalanche: Prioritize high interest loans first and continue to make
              minimum payments on all other loans. When a loan is paid
              off, apply the payment to the next remaining highest
              priority loan.
 - Snowball:  Prioritize low balance loans first and continue to make
              minimum payments on all other loans. When a loan is paid
              off, apply the payment to the next remaining highest
              priority loan.
 - Minimum:   Only pay the minimum payment fo all loans.

This script outputs a JSON report with information about the loans.

Notes
-----
The interest rate defined in the input file is taken to be the yearly
interest rate.

"""

import json
from datetime import datetime, date
from math import log10, ceil
from typing import Dict, List

from .schemas import LoanReportSchema, SummaryReportSchema, SummaryReportOutSchema

JSON_INDENT_SIZE = 4

PAYOFF_PRIORITY = {
    "snowball": lambda loan: loan.balance,  # lower balances,
    "avalanche": lambda loan: -loan.interest_rate,  # higher interests
    "minimum_only": lambda loan: 0,
}


class Loan(object):

    def __init__(self, name: str, principal: float, interest_rate: float,
                 min_payment: float):
        self.name = name
        self.balance_history = []
        self.payment_history = []
        self.remaining_history = []
        self.interest_rate = interest_rate
        self.min_payment = min_payment
        self._principal = principal
        self._interest = 0.0
        self._principal_paid = 0.0
        self._interest_paid = 0.0

    @property
    def balance(self) -> float:
        """Add the principal and interest to get the balance.

        Calculate the balance of the loan and round to two decimal
        places.

        Returns
        -------
        float
            The rounded balance left in the loan.

        """
        return round(self.interest + self.principal, 2)
    
    @property
    def balance_paid(self) -> float:
        """Add the principal and interest paid to get the balance paid.

        Calculate the balance paid of the loan and round to two decimal
        places.

        Returns
        -------
        float
            The rounded balance paid in the loan.

        """
        return round(self.interest_paid + self.principal_paid, 2)

    @property
    def principal(self) -> float:
        """The principal of the loan rounded to 2 decimal places.

        Returns
        -------
        float
            Rounded principal of the loan.

        """
        return round(self._principal, 2)
    
    @principal.setter
    def principal(self, value: float):
        self._principal = value

    @property
    def interest(self) -> float:
        """The interest of the loan rounded to 2 decimal places.

        Returns
        -------
        float
            Rounded interest of the loan.

        """
        return round(self._interest, 2)
    
    @interest.setter
    def interest(self, value: float):
        self._interest = value
        
    @property
    def interest_paid(self) -> float:
        """The interest paid of the loan rounded to 2 decimal places.

        Returns
        -------
        float
            Rounded interest paid of the loan.

        """
        return round(self._interest_paid, 2)
    
    @interest_paid.setter
    def interest_paid(self, value: float):
        self._interest_paid = value
        
    @property
    def principal_paid(self) -> float:
        """The principal paid of the loan rounded to 2 decimal places.

        Returns
        -------
        float
            Rounded principal paid of the loan.

        """
        return round(self._principal_paid, 2)
    
    @principal_paid.setter
    def principal_paid(self, value: float):
        self._principal_paid = value

    def compound(self) -> float:
        """Calculate the months interest for the loan.

        Returns
        -------
        float
            The new balance of the loan.

        """
        interest = self.balance * self.interest_rate / 12
        self.interest += interest
        return self.balance

    def make_payment(self, payment: float = None) -> float:
        """Make a payment to the loan.

        Uses the payment to pay off the loans interest and then applies
        the rest to the principal. If the payment is greater than the
        balance, the difference is returned.

        Parameters
        ----------
        payment : optional, float
            Amount to pay towards the loan balance. If set to None, make
            minimum payment (the default is None)

        Returns
        -------
        float
            Difference if payment is greater than loan balance.

        """
        if payment is None:
            payment = self.min_payment
        adjusted_payment = min((payment, self.balance))
        refund = payment - adjusted_payment

        interest_payment = min((adjusted_payment, self.interest))
        principal_payment = adjusted_payment - interest_payment
        self.interest_paid += interest_payment
        self.principal_paid += principal_payment
        self.interest -= interest_payment
        self.principal -= principal_payment

        self.balance_history.append(self.balance)
        self.payment_history.append(adjusted_payment)
        num_payments_left = self.get_num_remaining_payments(adjusted_payment)
        self.remaining_history.append(num_payments_left)

        return refund

    def get_num_remaining_payments(self, payment: float = 0) -> int:
        """Calculate the number of payments remaining in the loan.

        Parameters
        ----------
        payment : optional, float
            Payment to make. If set to 0 or None, it uses the minimum
            payment (the default is 0).

        Returns
        -------
        int
            Number of payments remaining.

        """
        if not payment:
            payment = self.min_payment

        if self.interest_rate:
            monthly_rate = self.interest_rate/12
            interest = monthly_rate * self.balance
            base = interest/payment
            num_payments = -log10(1 - base)/log10(1 + monthly_rate)
        else:
            num_payments = self.balance / payment
        return ceil(num_payments)

    def __bool__(self):
        return self.balance > 0

    def __repr__(self):
        return repr({self.name: self.__dict__})


def parse_loan_data(file: str) -> List[Loan]:
    """Reads a JSON file to get the loan data.

    Parameters
    ----------
    file : str
        Path to the file containing loan data.


    Returns
    -------
    List of loans
        List containing objects with loan data.

    """
    loan_data = json.load(open(file))
    loans = [Loan(loan_name, data["balance"], data["interest"]/100,
                  data["min_payment"])
             for loan_name, data in loan_data.items()]
    return loans


def generate_report(loan_order: List[Loan], payoff_strategy,
                    include_balance_history: bool = False,
                    include_payment_history: bool = False,
                    include_payments_left: bool = False) -> SummaryReportOutSchema:
    """Generate a report containing information about the payoff method.

    Generates a JSON report containing information such as months to
    payoff, interest paid, balance history, etc. for each loan and for
    a summary of all of them.

    Parameters
    ----------
    loan_order : list of Loan
        List containing Loan objects in the priority order.
    payoff_strategy : str
        Selected payoff strategy.
    include_balance_history : optional, bool
        Include the balance history for each loan and the summary (the
        default is False)
    include_payment_history : optional, bool
        Include the payment history for each loan (the default is False)
    include_payments_left : optional, bool
        Include the number of payments left after each payment for each
        loan (the default is False).

    Returns
    -------
    dict
        Generated report ready to be JSON dumped.

    """
    # report = {}
    loan_reports = []
    for loan in loan_order:
        loan_reports.append(_generate_loan_report(loan,
                                                  include_balance_history,
                                                  include_payment_history,
                                                  include_payments_left))
        # report[loan.name] = _generate_loan_report(loan,
        #                                           include_balance_history,
        #                                           include_payment_history,
        #                                           include_payments_left)

    summary_report = _generate_summary_report(loan_order,
                                                 payoff_strategy,
                                                 include_balance_history,
                                                 include_payment_history,
                                                 include_payments_left)
    # report["summary"] = _generate_summary_report(loan_order,
    #                                              payoff_strategy,
    #                                              include_balance_history,
    #                                              include_payment_history,
    #                                              include_payments_left)

    return SummaryReportOutSchema(
            loan_reports=loan_reports,
            summary_report=summary_report
    )


def _generate_loan_report(loan: Loan, include_balance_history: bool,
                          include_payment_history: bool,
                          include_payments_left: bool) -> LoanReportSchema:
    report = {
        "months ": len([balance for balance in loan.balance_history
                        if balance > 0]) + 1,
        "principal_paid": loan.principal_paid,
        "interest_paid": loan.interest_paid,
        "total": loan.principal_paid + loan.interest_paid
    }

    if include_balance_history:
        report["balance_history"] = loan.balance_history

    if include_payment_history:
        report["payment_history"] = loan.payment_history

    if include_payments_left:
        report["payments_remaining_history"] = loan.remaining_history

    res = LoanReportSchema(
            months=len([balance for balance in loan.balance_history
                        if balance > 0]) + 1,
            principal_paid=loan.principal_paid,
            interest_paid=loan.interest_paid,
            total=loan.principal_paid + loan.interest_paid
    )
    return res


def _generate_summary_report(loan_order: List[Loan],
                             payoff_strategy: str,
                             include_balance_history: bool,
                             include_payment_history: bool,
                             include_payments_left: bool) -> SummaryReportSchema:

    months = max([len(loan.balance_history) for loan in loan_order])
    principal_paid = sum([loan.principal_paid for loan in loan_order])
    interest_paid = sum([loan.interest_paid for loan in loan_order])
    total = sum([loan.balance_paid for loan in loan_order])

    summary = {
        "payoff_strategy": payoff_strategy,
        "payoff_order": [loan.name for loan in loan_order],
        "months": months,
        "principal_paid": round(principal_paid, 2),
        "interest_paid": round(interest_paid, 2),
        "total": round(total, 2)
    }
    res = SummaryReportSchema(
            months=max([len(loan.balance_history) for loan in loan_order]),
            principal_paid=round(principal_paid, 2),
            interest_paid=round(interest_paid, 2),
            total=round(total, 2),
            payoff_order=[loan.name for loan in loan_order],
            payoff_strategy=payoff_strategy,
    )
    
    if include_balance_history:
        balance_history = [round(sum(balances), 2) for balances in
                           zip(*[loan.balance_history for loan in loan_order])]
        summary["balance_history"] = balance_history
        
    if include_payment_history:
        payment_history = [round(sum(payments), 2) for payments in
                           zip(*[loan.payment_history for loan in loan_order])]
        summary["payment_history"] = payment_history

    if include_payments_left:
        payments_left = [round(sum(payments_left), 2) for payments_left in
                         zip(*[loan.remaining_history for loan in loan_order])]
        summary["payments_remaining_history"] = payments_left

    return res


def simulate(payoff_order: List[Loan], monthly_extra: float = 0,
             onetime_extra: float = 0):
    """Simulate the chosen payment plan for your loan.

    Parameters
    ----------
    payoff_order : list of Loan
        List of Loan objects in the order to prioritize payoff.
    monthly_extra : optional, float
        Extra payment to apply to the highest priority loan (the default
         is 0)
    onetime_extra : optional, float
        Onetime extra payment to apply to the highest priority loan (the
        default is 0)

    """
    extra = onetime_extra

    while any(payoff_order):
        remaining_loans = list(filter(bool, payoff_order))
        for loan in payoff_order:
            # first remaining loan is the highest priority
            if loan == remaining_loans[0]:
                payment = loan.min_payment + extra + monthly_extra
                extra = loan.make_payment(payment)
            else:
                extra += loan.make_payment()
            loan.compound()


def get_report(args: dict, monthly_extra: float = 0.0, one_time_extra: float = 0.0) -> SummaryReportOutSchema:
    loans = parse_loan_data(args["data"])
    payoff_order = sorted(loans, key=PAYOFF_PRIORITY[args["payoff_strategy"]])
    simulate(payoff_order, monthly_extra, one_time_extra)
    report = generate_report(payoff_order,
                             args["payoff_strategy"],
                             args["balance_history"],
                             args["payment_history"],
                             args["remaining_history"])
    return report


def add_months(current_date, months_to_add) -> date:
    new_date = date(current_date.year + (current_date.month + months_to_add - 1) // 12,
                    (current_date.month + months_to_add - 1) % 12 + 1,
                    current_date.day)
    return new_date


def main():
    args = {
        "data": "example_loan_data.json",
        "monthly_extra": 10_000,
        "onetime_extra":  0,
        "payment_history": True,
        "remaining_history": True,
        "balance_history": True,
        "payoff_strategy": "snowball",
        "output": "output_with_extra.json",
        "start_date": datetime.date(datetime.now())
    }
    report_no_extra = get_report(monthly_extra=0, args=args)
    report_with_extra = get_report(monthly_extra=args["monthly_extra"], args=args)

    diff_months = report_no_extra.summary_report.months - report_with_extra.summary_report.months
    diff_interest = report_no_extra.summary_report.interest_paid - report_with_extra.summary_report.interest_paid
    report_with_extra.months_saved = diff_months
    report_with_extra.interest_saved = diff_interest
    report_with_extra.debt_free_date = str(add_months(current_date=args["start_date"],
                                                                 months_to_add=report_with_extra.summary_report.months))

    if args["output"]:
        json.dump(report_with_extra.model_dump(), open(args["output"], 'w'), indent=JSON_INDENT_SIZE)

    else:
        print(json.dumps(report_with_extra.model_dump(), indent=JSON_INDENT_SIZE))


if __name__ == "__main__":
    main()
