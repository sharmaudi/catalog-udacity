# Udacity Catalog App

This code base implements the Udacity catalog app project.

## Notes
* Python 3.6+ is required to run this project
* Uses blueprints and flask app factory pattern to register extentions 
and middleware
* UI uses bootstrap and Jquery
* Tested on SQLite and Postgresql databases


## Cloning the code base

    # Clone the code repository 
    git clone https://github.com/sharmaudi/catalog-udacity.git
    cd catalog-udacity

    # Create the virtual environment. The codebase uses f-strings and is therefore dependent on python 3.6.
    #You can use the following commands in a mac to create and activate a virtualenv. Please check the documentation for other environments.
    python3.6 -m venv .venv
    source activate .venv
    
    # Install required Python packages
    pip install -r requirements.txt
    
    
## Configuring the app

Before we can use this application, we will have to configure the database URL and OAuth provider settings.

Common settings are found in `config/settings.py`. This file is checked into the vcs and secrets and envrionment specific settings should not be stored in this file.

Environment specific settings are stored in `instance/settings.py` that is NOT stored in the code repository.
The example `instance/settings.py.example` can be used as a starting point::

    cd catalog-udacity
    cp instance/settings.py.example instance/settings.py

Configure `instance/settings.py`.

## Configuring the Database server

Edit instance/settings.py.

Make sure to configure the SQLALCHEMY_DATABASE_URI setting correctly.

## Configuring Social Providers

Edit instance/settings.py.

Make sure to configure the OAUTH_CONFIG setting correctly. The instance/settings.py.example file can be used for reference.

### Setup google as OAuth Provider
- Open the Credentials page in the API Console.
  https://console.developers.google.com/apis/credentials
- Click Create credentials > OAuth client ID.
- Complete the form. Set the application type to Web application.
- Set the redirect uri as **http&#58;//localhost:8000/login/google/authorized**
- You will be presented with a client id and client secret. Set them in instance/settings.py. e.g
    ```
        OAUTH_CONFIG = {
            "GOOGLE": {
                "client_id": "444922280xxx-0lo6xxxxxxxxr07gjqsmlxxxxx.apps.googleusercontent.com",
                "client_secret": "KefaskxxhwhoBdKxxxxxxxxxx"
            }
        }
    ```

Please visit https://developers.google.com/identity/protocols/OAuth2WebServer for more details.   
    
### Setup facebook as OAuth Provider
- Follow facebooks documentation to setup a client id and secret.
- Set the redirect uri as **http&#58;//localhost:8000/login/facebook/authorized**
- Add the client-id and secret in instance/setting.py like so
    ```
        OAUTH_CONFIG = {
            "FACEBOOK": {
                "client_id": "xxxxxxxxxxxxxxxxxxx",
                "client_secret": "xxxxxxxxxxxxxxxx"
            }
        }
    ```



### Setup Github as OAuth Provider
- Follow github documentation to setup a client id and secret.
- Set the redirect uri as **http&#58;//localhost:8000/login/github/authorized**
- Add the client-id and secret in instance/setting.py like so
    ```
        OAUTH_CONFIG = {
            "GITHUB": {
                "client_id": "xxxxxxxxxxxxxxxxxxx",
                "client_secret": "xxxxxxxxxxxxxxxx"
            }
        }
    ```




## Initializing the Database

    # Create DB tables and populate the catalog tables
    python cli.py init --with-data

## Running the app

    # Start the Flask development web server
    python run.py

Point your web browser to http://localhost:8000/


## Routes
    # The following routes are exposed by the app
        | Route                                                      | Endpoint                 | HTTP Methods             |
        | /api/v1/catalog                                            | catalog.catalog_as_json  | GET/ HEAD/ OPTIONS       |
        | /catalog/<string:category>/items                           | catalog.home             | GET/ HEAD/ OPTIONS/ POST |
        | /catalog/<string:category>/items/<int:page>                | catalog.home             | GET/ HEAD/ OPTIONS/ POST |
        | /catalog/<string:category>/items/<string:item>             | catalog.item_in_category | GET/ HEAD/ OPTIONS       |
        | /catalog/<string:category>/items/<string:item>/delete      | catalog.delete_item      | GET/ HEAD/ OPTIONS       |
        | /catalog/<string:category>/items/<string:item>/edit        | catalog.edit_item        | GET/ HEAD/ OPTIONS/ POST |
        | /catalog/<string:category>/items/<string:item>/edit/upload | catalog.upload_image     | GET/ HEAD/ OPTIONS/ POST |
        | /catalog/items                                             | catalog.home             | GET/ HEAD/ OPTIONS       |
        | /catalog/items/<int:page>                                  | catalog.home             | GET/ HEAD/ OPTIONS       |
        | /catalog/items/add                                         | catalog.add_item         | GET/ HEAD/ OPTIONS/ POST |
        | /login                                                     | user.login               | GET/ HEAD/ OPTIONS       |
        | /login/facebook                                            | facebook.login           | GET/ HEAD/ OPTIONS       |
        | /login/facebook/authorized                                 | facebook.authorized      | GET/ HEAD/ OPTIONS       |
        | /login/github                                              | github.login             | GET/ HEAD/ OPTIONS       |
        | /login/github/authorized                                   | github.authorized        | GET/ HEAD/ OPTIONS       |
        | /login/google                                              | google.login             | GET/ HEAD/ OPTIONS       |
        | /login/google/authorized                                   | google.authorized        | GET/ HEAD/ OPTIONS       |
        | /logout                                                    | user.logout              | GET/ HEAD/ OPTIONS       |
        | /static/<path:filename>                                    | static                   | GET/ HEAD/ OPTIONS       |
        | /uploads/<filename>                                        | catalog.uploaded_file    | GET/ HEAD/ OPTIONS       | 
