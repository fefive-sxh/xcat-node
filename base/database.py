from peewee import *

DATABASE = "xcat-nodes.db"
DEBUG = True

db = SqliteDatabase(DATABASE)


def create_tables():
    with db:
        db.create_tables([NodeInfo])


class BaseModel(Model):
    class Meta:
        database = db


class NodeInfo(BaseModel):
    id = PrimaryKeyField()
    node = CharField(unique=True)       # 节点名称
    os = CharField()                    # 操作系统版本
    nvidia = CharField()                # NVIDIA驱动版本
    bmc = CharField()                   # BMC IP
    manage_ip = CharField()             # 管理 IP
    cal_ip = CharField()                # 计算 IP
    finish_at = DateTimeField()         # 安装完成时间
    result = CharField()                # 安装结果
    operator = CharField()              # 操作人员
    script = TextField()                # 自定义脚本
    created_at = DateTimeField()        # 创建时间
    # mac = CharField()                   # mac 地址

