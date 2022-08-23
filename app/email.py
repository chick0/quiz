from dns.resolver import resolve
from dns.resolver import NoAnswer
from dns.resolver import NXDOMAIN


class EmailVerifyFail(Exception):
    def __init__(self, message: str):
        super().__init__()
        self.message: str = message


def test_email_with_dns(email: str) -> bool:
    def safe_resolve(target: str) -> bool:
        try:
            resolve(qname=target)
            return True
        except (NXDOMAIN, NoAnswer):
            return False

    user, host = email.rsplit("@", 1)

    try:
        dns = resolve(
            qname=host,
            rdtype="MX"
        )
    except (NoAnswer, NXDOMAIN) as error:
        name = error.__class__.__name__
        raise EmailVerifyFail(
            message={
                "NoAnswer": "이메일을 받을 수 없는 주소입니다.",
                "NXDOMAIN": "해당 이메일은 존재하지 않는 도메인을 사용하고 있습니다.",
            }.get(name)
        )

    count = 0
    depth = 3

    for section in dns.response.sections:
        for data in section:
            for item in data.items:
                if count < depth:
                    name = ".".join([x.decode() for x in item.exchange.labels if len(x) != 0])
                    count += 1

                    if safe_resolve(target=name):
                        return True

    raise EmailVerifyFail(
        message="해당 이메일 주소는 MX 레코드 정보가 올바르지 않아 사용하실 수 없습니다."
    )
