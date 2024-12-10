""" convert currency """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from argparse import ArgumentError, ArgumentParser, RawTextHelpFormatter
from typing import Optional

import aiohttp
from emoji import get_emoji_regexp
from userge import Message, userge

CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)

# Add headers constant
HEADERS = {
    "Host": "www.mastercard.us",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Cookie": "_abck=9D818DF69CE0B2308A74B221E86E03FF~0~YAAQbG0QAuusIpyTAQAA2N2ZqA2OExSUs9WJ9eKk/P7fh7UN0+bhamGggjA/2LnMzlt0aycpIlSFr0i3VkX0tx+MjaZVam+dOJN2eseq3sgrzLcfY6Upx1NWQoEHuXugy4V1F/NRnaRkEXEPFjVr22+0L1fXAq4pt6Zyj8Qc2PZp5KF8o1wyDQc2Ncrp5qp21JzlnaRZJmvGgzAviL7b3COUGqAixK7HccjlfdqDNdJTquUSNrv7pViYbF2BX/EyogKU1UxnHd7QqndNzsJ7ECmL3YQ5G34U4roQDUeCjQ3WbouXdg9/I51ABRgoBLBM474NUbKKzOjIW0AxjglF4gVwOeTMqMSnWuqhY0otT0yM4HCBoBtNI/a0YwFViKDXcfSXm4nqDDhrteCDoVx6wT+TrV1A7B1y3/do1zoTmc9mbvRPpSbR5kB4Oxvl3/EfWKBa9rEw3hyzR1Nm4j+XSH34WZbEK2ycU2zpHk9eSEkewuIglmqjPgaJyOz2D12s2wfijpAqiL+PK+jiu5cq3AsiZkAoSEjihiO4HcoouZC7xNO5ZMluLbzTkLRWikfIpGKsv7YoYAOtQsTVXgZpOlp474YkzJTa/7ocYptXQlztb1A4RluNPuBJydIcOOe/Uob3+hH+pcHBvv1F2XRgOEWTYbfs8v+ovcL5wmRMPpQ+cW5Mqqeo8u/Tab2l+81TtKp0zOfHl9NdQvKuR0/xYZ3KCVH9dH0AlPuUt+Qj/VDHxobYOS4ySj4qjQ==~-1~-1~-1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-GPC": "1"
}

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
    formatter_class=RawTextHelpFormatter,
)

CURRENCIES = {}


@userge.on_start
async def init() -> None:
    try:
        if len(CURRENCIES) == 0:
            async with aiohttp.ClientSession() as session, session.get(
                "https://www.mastercard.us/settlement/currencyrate/settlement-currencies",
                headers=HEADERS  # Add headers here
            ) as response:
                if response.status != 200:
                    raise Exception(f"API response isn't 200: {await response.text()}")

                res = await response.json()
                data = res["data"]["currencies"]
                for currency in data:
                    CURRENCIES[currency["alphaCd"]] = currency["currNam"]
                LOG.info(f"Available Currencies: {CURRENCIES}")
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
        "examples": "{tr}cr USD GBP 1 | Use -d yyyy-mm-dd Flag to get historical rates",
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
        await message.err(f"`{parser.format_help()}\n\n{str(e)}`", del_in=5)
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
            f"&transAmt={parsed_args.amount}"
        )
        for date in parsed_args.date
    )

    msg = "--**Currency Exchange Rates**--\n\n"

    try:
        async with aiohttp.ClientSession() as session:
            for url in urls:
                async with session.get(url, headers=HEADERS) as response:
                    if response.status != 200:
                        await message.err(
                            f"`Failed to retrieve data, status code: {response.status}`",
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

                    msg += "__{}__:\n   {} **{}** = {} **{}**\n\n".format(
                        *map(
                            data.get,
                            ["fxDate", "transAmt", "transCurr", "crdhldBillAmt", "crdhldBillCurr"],
                        ),
                    )

                await asyncio.sleep(1)
    except Exception as e:
        await message.err(f"`Unexpected Error Occured: {e}`")

    await message.edit(msg)
