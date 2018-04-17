import bs4
import requests
import comprobante_crawler
import getpass

DST_URL = "https://secure.dst.usb.ve/login"


def login(user, password):
    """ Authenticates the given user with the university's CAS.
        NOTE: Since the university uses a self signed SSL certificate, I had to disable ceritificate
        verification, which triggers a warning at runtime.
        Parameters:
            user: the user's username
            password: the user's password
        Returns:
            A dict holding the cookie received after authentication (empty if it failed)
            A requests.Session object with the same cookie which can be used to make requests
    """
    session = requests.Session()
    first_response = session.get(DST_URL, verify=False)
    soup = bs4.BeautifulSoup(first_response.content, 'html.parser')
    lt = soup.find("input", {"name": "lt"}).attrs["value"]
    jsessionid = first_response.cookies.get('JSESSIONID')
    params = {
        'username': user,
        'password': password,
        'lt': lt,
        '_eventId': 'submit',
        'submit': 'INICIAR SESIÓN'
    }
    second_response = session.post(
        DST_URL + ';jsessionid=' + jsessionid, data=params)
    return second_response.cookies.get_dict(), session


def main():
    user = input("User: ")
    password = getpass.getpass("Password: ")
    token, session = login(user, password)
    resp = session.get(
        DST_URL + "?service=https%3A%2F%2Fcomprobante.dii.usb.ve%2FCAS%2Flogin.do", verify=False)

    params = {
        "cedula": "1210561",
        "tipo": "1"
    }

    resp_buscador = session.post(
        "https://comprobante.dii.usb.ve/CAS/consultaCarnet.do", data=params, verify=False)

    comprobante_crawler.get_student_data(resp_buscador.text)


if __name__ == '__main__':
    main()
