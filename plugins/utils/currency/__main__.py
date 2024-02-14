""" convert currency """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from argparse import ArgumentError, ArgumentParser
from typing import Optional

import aiohttp
from emoji import get_emoji_regexp
from userge import Message, userge

CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


class FallableArgumentParser(ArgumentParser):
    def exit(self, status: int = 0, message: Optional[str] = None):
        raise ArgumentError(None, message or "")

    def error(self, message: str):
        self.exit(2, message)


parser = FallableArgumentParser(
    ".cr",
    usage="%(prog)s FROM TO [AMOUNT]",
    description="Convert currency & get exchange rates.",
    add_help=False,
)

CURRENCIES = {}


@userge.on_start
async def init() -> None:
    try:
        if len(CURRENCIES) == 0:
            async with aiohttp.ClientSession() as session, session.get(
                "https://www.mastercard.us/settlement/currencyrate/settlement-currencies"
            ) as response:
                if response.status != 200:
                    raise Exception(f"API response isn't 200: {await response.text()}")

                res = await response.json()
                data = res["data"]["currencies"]
                for currency in data:
                    CURRENCIES[currency["alphaCd"]] = currency["currNam"]
    except Exception as e:
        LOG.info(f"Unexpected error occurred while fetching currencies: {e}")

    parser.add_argument(
        "from_currency",
        metavar="FROM",
        choices=CURRENCIES.keys() if len(CURRENCIES) > 0 else None,
        help="Input/Source Currency",
    )
    parser.add_argument(
        "to_currency",
        metavar="TO",
        choices=CURRENCIES.keys() if len(CURRENCIES) > 0 else None,
        help="Desired Currency",
    )
    parser.add_argument(
        "amount",
        type=float,
        metavar="AMOUNT",
        default=1,
        nargs="?",
        help="Amount for input currency (default: %(default)s)",
    )
    parser.add_argument(
        "-d",
        "--date",
        action="append",
        default=["0000-00-00"],
        help="Date to use while fetching rates,\nMultiple args are supported by repeating -d DATE",
    )


@userge.on_cmd(
    "cr",
    about={
        "header": "use this to convert currency & get exchange rate",
        "description": "Convert currency & get exchange rates.",
        "examples": "{tr}cr BTC USD 1",
    },
)
async def currency_conversion(message: Message):
    """
    this function can get exchange rate results
    """

    filterinput = get_emoji_regexp().sub("", message.input_str)
    await message.edit("`Processing...`")

    args = filterinput.split()
    try:
        parsed_args = parser.parse_args(args)
    except ArgumentError as e:
        await message.err(f"`{parser.format_help()}\n{str(e)}`", del_in=5)
        return

    # fxDate	           YYYY-MM-DD	        The date of the transaction
    # transCurr	           ISO Currency Code	3-digit ISO Currency Code of the transaction
    # crdhldBillCurr	   ISO Currency Code	3-digit ISO Currency Code of the cardholder
    #                                            billing currency
    # transAmount	       Number	            Amount in transaction currency
    # bankFee	           Number	            Percentage bank fee imposed by the issuer.
    #                                            Accommodates 4 decimal points to the right
    urls = (
        (
            "https://www.mastercard.us/settlement/currencyrate/conversion-rate?"
            "bankFee=0"
            f"&fxDate={date}"
            f"&transCurr={parsed_args.from_currency}"
            f"&crdhldBillCurr={parsed_args.to_currency}"
            f"&transAmt={parsed_args.amount}",
            date,
        )
        for date in parsed_args.date
    )

    msg = "--**Currency Exchange Rates**--\n\n"

    try:
        async with aiohttp.ClientSession() as session:
            for url, date in urls:
                async with session.get(url) as response:
                    if response.status != 200:
                        await message.err(
                            f"`Failed to retrieve data, status code: {response.status_code}`",
                            del_in=5,
                        )
                        LOG.info(f".cr API Response: {await response.text()}")
                        return

                    res = await response.json()
                    data = res["data"]
                    if res.get("type") == "error":
                        await message.err(
                            f"`{data.get('errorMessage')}, status code: {data.get('errorCode')}`",
                            del_in=5,
                        )
                        return

                    msg += "__{}__:\n  {} **{}** = {} **{}**\n\n".format(
                        date,
                        *map(
                            data.get, ["transAmt", "transCurr", "crdhldBillAmt", "crdhldBillCurr"]
                        ),
                    )

                await asyncio.sleep(1)
    except Exception as e:
        await message.err(f"`Unexpected Error Occured: {e}`")

    await message.edit(msg)
