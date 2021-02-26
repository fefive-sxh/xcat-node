import time

from flask import request, json, jsonify

from app.xcat import get_nodes_info, update_node_info


def get_nodes_view():
    """
    获得节点列表
    :return:
    """
    node_list = get_nodes_info()
    result = []
    for node in node_list:
        item = {
            "id": node.get("id", ""),
            "node": node.get("node", ""),
            "os": node.get("os", ""),
            "nvidia": node.get("nvidia", ""),
            "bmc": node.get("bmc", ""),
            "manageIp": node.get("manage_ip", ""),
            "calIp": node.get("cal_ip", ""),
            "cratedAt": node.get("created_at", ""),
            "script": node.get("script", "")
        }

        result.append(item)

    return jsonify(result), 200


def update_node_view(node: str):
    """
    更新节点
    :param node:
    :return:
    """

    params = request.json
    os = params["os"]
    nvidia = params["nvidia"]
    manage_ip = params["manageIp"]
    cal_ip = params["calIp"]
    script = params["script"]
    name = params["node"]
    bmc = params["bmc"]

    if name == node:
        err = update_node_info(os=os, nvd=nvidia, manage_ip=manage_ip, cal_ip=cal_ip, script=script, node=name, bmc=bmc)
        if not err:
            return {}, 200
    return {}, 400


def get_nodes_log_view():
    """
    获得节点日志
    :return:
    """
    log_list = get_nodes_info()
    result = []
    for log in log_list:
        item = {
            "finishAt": log.get("finish_at", ""),
            "node": log.get("node", ""),
            "os": log.get("os", ""),
            "nvidia": log.get("nvidia", ""),
            "bmc": log.get("bmc", ""),
            "manageIp": log.get("manage_ip", ""),
            "calIp": log.get("cal_ip", ""),
            "result": log.get("result", ""),
            "createdAt": log.get("created_at", ""),
            "operator": log.get("operator", ""),
        }
        result.append(item)
    return json.dumps(result), 200
