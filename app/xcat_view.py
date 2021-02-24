from flask import request
from marshmallow import fields, Schema

from app.schema import NodeInfoSchema
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
            "id": node.id,
            "node": node.node,
            "os": node.os,
            "nvidia": node.nvidia,
            "bmc": node.bmc,
            "manageIp": node.manage_ip,
            "calIp": node.cal_ip,
            "cratedAt": node.created_at,
        }
        result.append(item)
    return NodeInfoSchema(many=True).dump(result).data, 200


def update_node_view(node_id: str):
    """
    更新节点
    :param node_id:
    :return:
    """
    params, _ = NodeInfoSchema().load(request.get_json())
    os = params["os"]
    nvidia = params["nvidia"]
    manage_ip = params["manageIp"]
    cal_ip = params["calIp"]
    script = params["script"]
    node = params["node"]

    update_node_info(id=node_id, os=os, nvd=nvidia, manage_ip=manage_ip, cal_ip=cal_ip, script=script, node=node)

    #
    return [], 200


def get_nodes_log_view():
    """
    获得节点日志
    :return:
    """
    log_list = get_nodes_info()
    result = []
    for log in log_list:
        item = {
            "finishAt": log.finish_at,
            "node": log.node,
            "os": log.os,
            "nvidia": log.nvidia,
            "bmc": log.bmc,
            "manageIp": log.manage_ip,
            "calIp": log.cal_ip,
            "result": log.result,
            "createdAt": log.created_at,
            "operator": log.operator,
        }
        result.append(item)
    return NodeInfoSchema(many=True).dump(result).data, 200
