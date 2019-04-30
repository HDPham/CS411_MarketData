#taking in the stock name as input
def ohlc(stock):
    connection = db.engine.connect()
    query = 'SELECT open, high, low, close FROM Daily WHERE stock_name=\"'+stock+'\";'
    result = connection.execute(query)
    o = []
    h = []
    l = []
    c = []
    for row in result:
        o.append(row[0])
        h.append(row[1])
        l.append(row[2])
        c.append(row[3])
    return o, h, l, c # output four vectors
