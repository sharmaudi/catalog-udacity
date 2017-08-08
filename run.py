from app import app

if __name__ == '__main__':
    flask_app = app.create_app()
    debug = flask_app.config['DEBUG']
    print(f"Debug is {debug}")
    flask_app.run(debug=debug, port=8000, host='0.0.0.0', threaded=True)
