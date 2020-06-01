from planet_health import PlanetHealth
from flask import Flask


application = Flask(__name__)


@application.route('/')
@application.route("/<cidade>")
def say_hello(cidade = "SÂO PAULO"):
    return PlanetHealth().processar(cidade)

if __name__ == "__main__":
    application.debug = True
    application.run()