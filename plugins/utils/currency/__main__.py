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
    'Host': 'www.mastercard.us',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cookie': '_abck=D6C3C89210EAB2BD97B4F6A52424EFF8~0~YAAQbG0QAtFhYDuVAQAAZvvnPw03CoNjVUmJp8fdRlhBg0DiwRVnVuZgWNk6YJzeVWQpYtF3Eg/rB3ptqLCNzp+qrgyJ37v2ypGWgChJUV1iuPYpxx+e/IrqVxbO+IozC61xHOwH+nZEZj4cS6nRTzlP9wXw5tRMXBOYCjut2NGRcK1M4kzHor9DFPQeCOrnF/L0A9DVB/mw4LyIdGaT5vYGf6WwFShPM06O9OqwP1OPdZLYD76j35A0UH+/o9KJqEfPMS49S4N4SHuYMYuxU8dcPC6QmUXRSKic4i9QVDw/gbEs+LcV/vT0AYvepFhTCIPS4CFahjEqbd+h7dLVN6EwlBwSfQ9MjQwQc+97Vx/j/+xyN6t7G1DYlNK/t1Gkl5MB1fe1rZTPYGHESZUKYwDthZNJCTCKp+SweUJq2RJQ6CI5NcvNi2JfQrQs4GXkpll0smOPi/9O/xiV7xv4+rPn7Wb7LVynRa4aucaaEq+7U1wvvpYoFFBWor0kfvzfRy0iTOpSjK9s4l2oOmxh3O8DjS5mNnyDp0XRQ7TvjTxNxcFmmCVv/XSx0eTdSU9sD5DhNhx9Rz1YampSQWcWRzqKpRjNYNVZFsX8pVXnaa5h9bF4NOrnhUaKC+4pSt0iq1O6of3upZ0jF7aYxhOK7U52HE4Ig0TzOAeS17KS3q3c14iZYQVUV0DQyKXmE1eO6iKmc+lhytWfXkDIH/BS0GQyn8YnFDgUr9hZg3nnwmVJtC4QTSd6eMa5I3qz/4VrhM8G3ZfqHu0LEyFG3WZ7ILxY820i5NwlYUJaJ0PDg+1LCppq+uK4d+dz7bR86mJx~-1~-1~-1; ak_bmsc=394A716C8870A124600369360574442E~000000000000000000000000000000~YAAQbG0QAllfYDuVAQAATHvmPxpkrQYOrN2UgsGhi4Rc7xr0iWKMFDW7h4Zo280uJH63bE/5UY0dk21gxN8kogc1jl9AVFAA6d8s93msG8GNfnklK4TfMIxP9sbGmmWM7FPiCMPXta8dy/OJ1X+zx87h17peAhuzj2eRj4Umw8A2jg+Cja65eM6N/8wdaRAreal5aoTMCunBJcj1HI0AQS+09j71GeF9bfTOR0EGY9Q7yppzTp95xt4cUe/iEy+pGvb4dux6bqBTReQj0BropGHsR8WqUYc15CjLkIVgaycFK0j0KSPVuna20nhRaJOQL57pkJYSERv4aNqpt6GOV23JMb9PNzskc22F0nBFtNfvN5nh6mtUbsDM0nvOIw71fwfm4bvQ4foKEpxLnlI=; bm_sz=13F766DCC57AFABF987F0BE80E6F8819~YAAQbG0QAtNhYDuVAQAAZvvnPxrCjTpyma+ohVliatEV3ibv/MUuqYcjxIjlNTswZY0w70c4rLsGda28xALrzHcQMxG1MEW1e/pfYVDsKC/hrldMsadWf1KWPhbIHnti55QH2TdaDaFy9IcTPa4RTgo2XzbEcL1zu1E6K1sgnKwQ6m+mbwGAcfD449D+Y0ODDzzmYSr7jldrusUC+S2KJw+j9QoDXnINBcd2EFkFr07g79jTw6O0bG0dihUwrpM1pgw3w5SP5Yb468UNiE7NtduUR5T8j9l2oqzwjxvqwZ8FI1o/1mu1ymLG2xNIpMPOwijhWK4BcdoYuHpnoJTNZBKIjtvOiS2vXNws7rYHzVKQB3vlpjsKQpjANx0VWkoUTdJhTPiQ934kYukZhvwHt9ga65C0xw6WoYnswEUwyCOdbLIH7g==~3490613~3749954; BIGipServerwww.dm.mc.global-https-pool=!OF1JfZMfHkAGJ+y6oJ35j37UF/50ILn05SYqipnxjDwjNNDMZmbICPmrM7GGmhhNmfc2iTFZcih4Fk4=; TS013559a7=019243af6fc6d6211a994384e7c6f0c9a6580019395a238d70b9611c523bfe00b772e347c7a3757325f6b5628ee89a50d0f3bce9dd; bm_sv=D7BCE826D598445EE315D0ED999493B1~YAAQbG0QAtJhYDuVAQAAZvvnPxpfoqs+5NsOqTkMX1TOlVObWHOnhTM74cT22o2SPIg2I5PsL2omwzrD5KbCKX+kl2yi9Nsks5v5TKo8ZLmqVnUmc/NWWffTS4d9vg8n8cXLKxQDAc09M6ozx72t12GUFDiibJxLWWlcV9CST2DT0MHie9BHDbsWNoMg00jBtgAy5FApGbiTR/URexuWw0Xqjo2sn8bKvVLk9rJSkkGl3bAmb6ET3oo4AjLJZyQhpdb6~1',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-GPC': '1'
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
