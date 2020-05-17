import argparse
from enum import Enum
from math import ceil, log
from typing import List, Dict, Union


class Selection(Enum):
    ANNUITY: str = "annuity"
    DIFF: str = "diff"
    INVALID: str = "invalid"


months: int
years: int
output: List[str] = []
parameters: Dict[str, Union[int, float, Selection]]
payments: Dict[int, int] = {}

parser = argparse.ArgumentParser()
parser.add_argument("--type", type=Selection, help="indicates the type of payments", default="invalid")
parser.add_argument("--payment", type=float, help="a monthly payment", default=0)
parser.add_argument("--principal", type=int, help="loan principal", default=0)
parser.add_argument("--periods", type=int, help="number of months needed to repay the credit", default=0)
parser.add_argument("--interest", type=float, help="interest of the loan", default=0)
args = parser.parse_args()

parameters = dict(args._get_kwargs())

# type is within implementation
# if parameters["type"] not in ["annuity", "diff"]:
#     print("Incorrect parameters")
# else:
#     selection = Selection(parameters["type"])

# print(parameters)

selection = parameters["type"]
payment = parameters["payment"]
principal = parameters["principal"]
periods = parameters["periods"]
interest = parameters["interest"] / (100 * 12)

if (
        selection != Selection.INVALID and
        # payment must not be specified when using diff
        not (selection == Selection.DIFF and payment) and
        # need more than 3 numerical parameters
        len([v for v in parameters.values() if isinstance(v, (int, float)) and v]) >= 3 and
        # none of the parameters should be negative
        not any((v < 0 for v in parameters.values() if isinstance(v, (int, float)))) and
        # interest always needs to be specified
        interest
):

    if selection == Selection.DIFF:
        for i in range(1, periods + 1):
            payments[i] = int(ceil(principal / periods + interest * (principal - (principal * (i - 1)) / periods)))
        output.extend(["Month {}: paid out {}".format(k, v) for k, v in payments.items()])
        output.append("\nOverpayment = {}".format(sum(payments.values()) - principal))
        print(*output, sep="\n")
    elif selection == Selection.ANNUITY:
        if not payment:
            payment = ceil(principal * (interest * (1 + interest) ** periods) / ((1 + interest) ** periods - 1))
            print("Your annuity payment = {}!".format(payment))
        elif not principal:
            principal = int(payment / ((interest * (1 + interest) ** periods) / ((1 + interest) ** periods - 1)))
            print("Your annuity payment = {}!".format(principal))
        elif not periods:
            periods = ceil(log((payment / (payment - interest * principal)), 1 + interest, ))
            years, months = divmod(periods, 12)
            output = ["You need"]
            if years:
                output.append("{} year{}{}".format(
                        years,
                        "" if years == 1 else "s",
                        " and" if months else "",
                ))
            if months:
                output.append("{} month{}".format(
                        months,
                        "" if months == 1 else "s",
                ))
            output.append("to repay this credit!")
            print(*output, sep=" ")
        print("Overpayment = {}".format(int(ceil(payment * periods - principal))))
else:
    print("Incorrect parameters")
