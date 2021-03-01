import time
from datetime import datetime
from typing import List
import threading
import subprocess as sp

from peewee import *

from app.utils import parse_output, wait_install
from base.database import NodeInfo, db, NodeLog

# 　设置一下远程登录, 部署在远程 则不需要 ssh
# ssh = "ssh root@10.10.100.90"
ssh1 = "ssh root@10.10.100.91"

ssh = ""



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
        try:
            with db.atomic():
                item = NodeInfo.select().where(
                    NodeInfo.node == name,
                ).get()
        except DoesNotExist:
            continue

        if item:
            node["id"] = item.id
            node["manage_ip"] = item.manage_ip
            node["os"] = item.os
            node["nvidia"] = item.nvidia
            node["script"] = item.script
            node["cal_ip"] = item.cal_ip
            node["created_at"] = item.created_at
            node["operator"] = item.operator
            node["result"] = item.result
            node["bmc"] = item.bmc
            node["finish_at"] = item.finish_at

    return result


def update_node_info(*, bmc: str, os: str, nvd: str, manage_ip: str, cal_ip: str, script: str, node: str):
    now = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    # manage_ip = "10.10.100.92"
    # 操作 NodeInfo
    with db.atomic():
        # 获得或者创建
        info, created = NodeInfo.get_or_create(
            node=node,
            defaults={
                "os": os,
                "nvidia": nvd,
                "bmc": bmc,
                "manage_ip": manage_ip,
                "cal_ip": cal_ip,
                "script": script,
                "operator": "admin",
                "created_at": now,
                "finish_at": "",
                "result": "",
            }
        )
        # 若存在, 则进行更新
        if not created:
            info.os = os
            info.nvidia = nvd
            info.bmc = bmc
            info.manage_ip = manage_ip
            info.cal_ip = cal_ip
            info.script = script
            info.created_at = now
            info.finish_at = ""
            info.result = ""
            info.save()

    with db.atomic():
        # 创建日志记录
        log = NodeLog.create(
            node=node,
            os=os,
            nvidia=nvd,
            bmc=bmc,
            manage_ip=manage_ip,
            cal_ip=cal_ip,
            finish_at="",
            created_at=now,
            result="",
            operator="admin",
            script=script
        )

    # 从命令行更新
    # 1. 修改属性
    process1 = sp.Popen(f"{ssh} chdef -t node {node} ip={manage_ip}", stdout=sp.PIPE, shell=True)
    out, err = process1.communicate()
    if err:
        return err

    # 2. 配置操作系统和GPU驱动 nodeset 节点名 osimage=操作系统版本-x86_64-install-compute-cuda版本号
    osimage = f"{os}-x86_64-install-compute-{nvd}"
    cmd = f"{ssh1} nodeset {node} osimage={osimage}"
    process2 = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
    out, err = process2.communicate()
    if err:
        return err

    # 此时可以开一个线程去监听是否安装成功
    thread = threading.Thread(target=wait_install, daemon=True, args=(node, manage_ip, now))
    thread.start()

    # 3. 执行安装 `rsetboot 节点名 net`  `rpower 节点名 reset`
    shell1 = f"{ssh1} rsetboot {node} net"
    shell2 = f"{ssh1} rpower {node} reset"
    process3 = sp.Popen(shell1, stdout=sp.PIPE, shell=True)
    out, err = process3.communicate()
    if err:
        return err

    process4 = sp.Popen(shell2, stdout=sp.PIPE, shell=True)
    out, err = process4.communicate()
    if err:
        return err

    return None


def get_nodes_log():
    result = []
    for log in NodeLog.select():
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
    return result
