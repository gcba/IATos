#!/usr/bin/env python3

from dotenv import load_dotenv
load_dotenv()

import connexion

def main():
    app = connexion.App(__name__, specification_dir='./')
    app.add_api('swagger.yaml', base_path="/v1", arguments={'title': 'Tos.IA API'}, pythonic_params=True)
    app.run(port=8080)


if __name__ == '__main__':
    main()
