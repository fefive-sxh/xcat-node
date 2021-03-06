from flask import Flask
from flask import g

from app.xcat_view import get_nodes_view, update_node_view, get_nodes_log_view
from base.database import db

app = Flask(__name__)
app.config.from_object(__name__)


@app.before_request
def before_request():
    g.db = db
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route("/v1/xcat/nodes", methods=["GET"])
def get_nodes():
    return get_nodes_view()


@app.route("/v1/xcat/nodes/<node>", methods=["PUT"])
def update_node(node):
    return update_node_view(node=node)


@app.route("/v1/xcat/nodes/log", methods=["GET"])
def get_node_log():
    return get_nodes_log_view()
