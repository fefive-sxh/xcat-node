from datetime import datetime
from typing import List
import threading
import subprocess as sp

from flask import flash
from peewee import *

from app.utils import parse_output, wait_install
from base import database
from base.database import NodeInfo, db

#　设置一下远程登录
ssh = "ssh root@10.10.100.90"


def get_nodes_info() -> List[dict]:
    # 一部分存到数据库中, 一部分从命令行中获得

    # 从命令行中获得
    process = sp.Popen(f"{ssh} lsdef -t node -l", stdout=sp.PIPE, shell=True)
    out, err = process.communicate()
    # out 是一段字符串, 将其序列化
    result = parse_output(out)

    # xcat 中 manageIp os nvd 可能为空
    # 看数据库中是否存在
    for node in result:
        name = node.get("node")
        mac = node.get("mac")
        bmc = node.get("bmc")
        try:
            with db.atomic():
                item = NodeInfo.select().where(
                    NodeInfo.node == name,
                    NodeInfo.bmc == bmc,
                    NodeInfo.mac == mac
                ).get()
        except DoesNotExist:
            continue

        if item:
            node["manageIp"] = item.manage_ip
            node["os"] = item.os
            node["nvidia"] = item.nvidia
            node["script"] = item.script
            node["calIp"] = item.cal_ip
            node["createdAt"] = item.created_at

    return result


def update_node_info(*, bmc: str, os: str, nvd: str, manage_ip: str, cal_ip: str, script: str, node: str):
    # 若id存在 则是更新, 不存在则是创建
    if node:
        n = NodeInfo.select().where(NodeInfo.id == id).get()
        n.bmc = bmc
        n.os = os
        n.nvidia = nvd
        n.manage_id = manage_ip
        n.cal_ip = cal_ip
        n.script = script
        n.node = node
        n.save()
    else:
        # 同步到数据库
        try:
            with db.atomic():
                node = NodeInfo.create(
                    node=node,
                    os=os,
                    nvidia=nvd,
                    bmc=bmc,
                    manage_ip=manage_ip,
                    cal_ip=cal_ip,
                    script=script,
                    operator="admin",
                    created_at=datetime.now(),  # todo 验证是否正确
                )
        except InternalError:
            flash("the node name is already taken")

    # 从命令行更新
    # 1. 修改属性
    process1 = sp.Popen(f"chdef -t node {node} ip={manage_ip}", stdout=sp.PIPE, shell=True)
    # out, err = process.communicate()

    # 2. 配置操作系统和GPU驱动 nodeset 节点名 osimage=操作系统版本-x86_64-install-compute-cuda版本号
    osimage = f"{os}-x86_64-install-compute-{nvd}"
    cmd = f"{ssh} nodeset {node} {osimage=}"
    process2 = sp.Popen(cmd, stdout=sp.PIPE, shell=True)

    # 此时可以开一个线程去监听是否安装成功
    thread = threading.Thread(target=wait_install(node=node, bmc=bmc))
    thread.run()

    # 3. 执行安装 `rsetboot 节点名 net`  `rpower 节点名 reset`
    shell1 = f"{ssh} rsetboot {node} net"
    shell2 = f"{ssh} rpower {node} reset"
    process3 = sp.Popen(shell1, stdout=sp.PIPE, shell=True)
    process4 = sp.Popen(shell2, stdout=sp.PIPE, shell=True)
    return
