import sys
import json
import typing
import logging
import requests

# which component listens on which port
SERVICE_NAME: typing.Final[dict[int,str]] = {
    8000: "front.js",
#    8001: "front.rb",
    8002: "parser.js",
#    8003: "parser.rb",
    8004: "codegen",
    8006: "kbgen",
    8007: "query.engine"
}

# this is just a wrapper around SERVICE_NAME
# the order is the same as in the README
def component_name_listenning_on(port: int) -> str:
    if port in SERVICE_NAME:
        return SERVICE_NAME[port]
    
    logging.error(f'health check on uninitialized port {port}')
    return ""

def health_check_all_components() -> None:

    for port in SERVICE_NAME.keys():
        try:
            url = f'http://127.0.0.1:{port}/healthcheck'
            component = component_name_listenning_on(port)
            response = requests.get(url)
            if response.status_code == 200:
                json_response = json.loads(response.text)
                if 'healthy' in json_response and json_response['healthy']:
                    logging.info(f'{component} ---> healthy 😃 ')
                continue
        except requests.exceptions.RequestException:
            pass # fall through to the last error log message
        
        logging.error(f'{component} ---> unhealthy 😖 ')

def configure_logger() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s]: %(message)s",
        datefmt="%d/%m/%Y ( %H:%M:%S )",
        stream=sys.stdout
    )

def main():

    configure_logger()
    health_check_all_components()

if __name__ == "__main__":
    main()

