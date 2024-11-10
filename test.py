# print('hello world')

# list = [1, 2, 3, 4, 5, 6]
# for i in list:
#     print(i)

# def summ(a, b):
#     if b % 2 == 0:
#         return a + b
#     return a

# acc = 0
# for i in list:
#     acc = summ(acc, i)
# print(acc)

pairs = {
    "XXRPZUSD": {
        "altname": "XRPUSD",
        "wsname": "XRP/USD",
        "aclass_base": "currency",
        "base": "XXRP",
    },
    "XXBTZUSD": {
        "altname": "XBTUSD",
        "wsname": "XBT/USD",
        "aclass_base": "currency",
        "base": "XXBT",
    },
    "ADAUSDT": {
        "altname": "XRPUSD",
        "wsname": "XRP/USD",
        "aclass_base": "currency",
        "base": "ADA",
    },
    "ADAEUR": {
        "altname": "ADAUER",
        "wsname": "ADA/EUR",
        "aclass_base": "currency",
        "base": "ADA",
    },
}
# filtered_pairs = {k: v for k, v in pairs.items() if k.endswith('USD')}
filtered_pairs = {}
for key, value in pairs.items():
    if key.endswith("USD"):
        filtered_pairs[key] = value

lst = []
for i in pairs.keys():
    symbol = pairs[i]["base"]
    if symbol.startswith("X"):
        symbol = symbol[1:]
    lst.append(symbol)

a = [{"label": data["base"], "value": key} for key, data in pairs.items()]
print(a)
