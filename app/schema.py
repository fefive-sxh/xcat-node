from marshmallow import fields, Schema


# 节点信息Schema
class NodeInfoSchema(Schema):
    id = fields.String()
    node = fields.String(required=True)
    os = fields.String()
    nvidia = fields.String()
    bmc = fields.String(required=True)
    manage_ip = fields.String()
    cal_ip = fields.String()
    created_at = fields.DateTime()
    script = fields.String()
    finished_at = fields.DateTime()
    operator = fields.String()
    result = fields.String()
