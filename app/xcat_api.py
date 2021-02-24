from flask import Flask
from flask import g

from app.xcat_view import get_nodes_view, update_node_view, get_nodes_log_view
import base
from base.database import create_tables

app = Flask(__name__)
app.config.from_object(__name__)


@app.before_request
def before_request():
    g.db = base.database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route("/v1/xcat/nodes", methods=["GET"])
def get_nodes():
    return get_nodes_view()


@app.route("/v1/xcat/nodes/<nodeId>", methods=["PUT"])
def update_node(nodeId):
    return update_node_view(node_id=nodeId)


@app.route("/v1/xcat/nodes/log", methods=["GET"])
def get_node_log():
    return get_nodes_log_view()
