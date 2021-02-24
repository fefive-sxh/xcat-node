from datetime import date

from peewee import *

db = SqliteDatabase("people.db")


class BaseModel(Model):
    class Meta:
        database = db


class Person(BaseModel):
    # script = TextField()
    name = CharField()
    # is_success = BooleanField(default=False)

    birthday = DateField()  # 具有 year month day 属性

    # 　time = TimeField()  # 具有 hour minute second 属性

    # DataTimeField() 上面都有

    class Meta:
        database = db  # 这个　model 使用 "people.db" 数据库
        # 若要显式指定模型类的表名, 可以使用 table_name 元选项
        # table_name = 'tb_person'


db.connect()
db.create_tables([Person])

# 存储数据 save() 或者 create()
# 方式1
# sb_zz = Person(name="zz", birthday=date(1989, 9, 4))
# sb_zz.save()

# 方式二
# nc = Person.create(name="gg", birthday=date(1989, 6, 4))
# # 若要更新, 可以使用save
# nc.name = "sjb"
# nc.save()

# 查询
# # 获取单条记录, 使用 Select.get() 或者 Model.get()
p = Person.select().where(Person.name == "gg").get()
# p1 = Person.get(Person.name == "zz")
print(f"{p=}")

# # 获取所有清单
for person in Person.select():
    print(f"{person.name=}")

# 删除实例
# # 比如先创建一个非智障的人, 需要删除
s = Person.create(name="xx", birthday=date(1977, 6, 6))
s.delete_instance()

# 处理完毕需要关闭数据库连接
db.close()
