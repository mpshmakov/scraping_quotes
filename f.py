# import argparse
# from dbt import rate


# # parser = argparse.ArgumentParser()
# # parser.add_argument('--product_id', dest='product_id', type=str, help='Add product_id')
# # args = parser.parse_args()

# # print (args.product_id)

# rate()

from sqlalchemy import select
from database.operations import executeOrmStatement
from database.schema import Authors, Quotes, Users

q = Quotes("111111111111111111111111111111111111", "text", "ddd")
# print(type(q))

res = executeOrmStatement(select(Authors))
user = executeOrmStatement(select(Users).filter(Users.username == "user1")).first()
# quote = res.first()

# print((quote))
# print(quote.Authors.author)
print(res.all())
print(user)

# for r in res.all():
    # print(r.Authors.author)