import subprocess as sp
import time

from base.database import NodeInfo


def parse_output(text: str) -> list:
    # 1. 去除 \n 和 空格
    text = text.decode("utf-8").replace(" ", "").replace("\n", " ")
    """
    处理之后为:
    'Objectname:dce-gpu-64 arch=x86_64 bmc=192.168.126.64 currchain=boot currstate=installcentos7-x86_64-compute groups=test,all,gpu ip=192.168.111.64 mac=ac:1f:6b:a5:00:c2 mgt=ipmi netboot=pxe os=centos7 postbootscripts=otherpkgs postscripts=syslog,remoteshell,syncfiles profile=compute provmethod=centos7-x86_64-install-compute-cuda10.1 Objectname:dce-gpu-65 arch=x86_64 bmc=192.168.126.65 groups=test,all,gpu ip=192.168.111.65 mac=ac:1f:6b:a5:00:c3 mgt=ipmi netboot=pxe os=centos7.8 postbootscripts=otherpkgs postscripts=syslog,remoteshell,syncfiles '
    """
    # 2. 将 多个节点信息分割开为单个节点
    string_list: list = text.split("Objectname:")[1:]
    """
    处理之后
        [
        'dce-gpu-64 arch=x86_64 bmc=192.168.126.64 currchain=boot currstate=installcentos7-x86_64-compute groups=test,all,gpu ip=192.168.111.64 mac=ac:1f:6b:a5:00:c2 mgt=ipmi netboot=pxe os=centos7 postbootscripts=otherpkgs postscripts=syslog,remoteshell,syncfiles profile=compute provmethod=centos7-x86_64-install-compute-cuda10.1 ',
        'dce-gpu-65 arch=x86_64 bmc=192.168.126.65 groups=test,all,gpu ip=192.168.111.65 mac=ac:1f:6b:a5:00:c3 mgt=ipmi netboot=pxe os=centos7.8 postbootscripts=otherpkgs postscripts=syslog,remoteshell,syncfiles '
        ]
    """
    result = []
    for string in string_list:
        item = str_to_map(string)
        result.append(item)
    return result


def str_to_map(string: str):
    s_list = string.split(" ")
    result = {
        "node": s_list[0],
    }
    for s in s_list:
        if "bmc=" in s:
            result["bmc"] = s.replace("bmc=", "")
        if "ip=" in s:
            result["manageIp"] = s.replace("ip=", "")
        if "provmethod=" in s:
            tmp = s.replace("provmethod=", "")
            tmp = tmp.split("-")
            result["os"] = tmp[0]
            result["nvidia"] = tmp[-1]
        if "mac=" in s:
            result["mac"] = s.replace("mac=", "")

    return result


# 测试是否安装成功
def check_install(manage_ip):
    process = sp.Popen(f"ping -c 1 {manage_ip}", stdout=sp.PIPE, shell=True)
    out, err = process.communicate()

    return err is None


def wait_install(node, manage_ip, created_at):
    # 首先等待50分钟
    time.sleep(50*60)
    ok = check_install(manage_ip=manage_ip)
    if not ok:
        # 若没有安装成功 再等待一个5分钟
        time.sleep(60*5)
        ok = check_install(manage_ip)

    now = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    # 将结果同步到数据库中
    n = NodeInfo.update(
        result="success" if ok else "unsuccess",
        finish_at=now
    ).where(NodeInfo.node == node & NodeInfo.created_at == created_at)

    n.execute()
