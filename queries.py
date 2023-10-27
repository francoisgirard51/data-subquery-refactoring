# pylint:disable=C0111,C0103

def get_average_purchase(db):
    # return the average amount spent per order for each customer ordered by customer ID
    request = '''
        WITH OrderValues AS (
          SELECT
            SUM(od.UnitPrice * od.Quantity) AS value,
            od.OrderID
          FROM OrderDetails od
          GROUP BY od.OrderID
        )
        SELECT
            c.CustomerID,
            ROUND(AVG(ov.value), 2) AS average
        FROM Customers c
        JOIN Orders o ON c.CustomerID = o.CustomerID
        JOIN OrderValues ov ON ov.OrderID = o.OrderID
        GROUP BY c.CustomerID
        ORDER BY c.CustomerID
    '''
    return db.execute(request).fetchall()

def get_general_avg_order(db):
    # return the average amount spent per order
    query = """
    SELECT AVG(TotalAmount) AS GeneralAverage
    FROM (
        SELECT o.OrderID, SUM(od.UnitPrice * od.Quantity) AS TotalAmount
        FROM OrderDetails od
        JOIN Orders o ON o.OrderID = od.OrderID
        GROUP BY o.OrderID
    )
    """
    result = db.execute(query)
    return result.fetchone()[0]

def best_customers(db):
    # return the customers who have an average purchase greater than the general average purchase
    request = '''
        WITH OrderValues AS (
          SELECT
            SUM(od.UnitPrice * od.Quantity) AS value,
            od.OrderID
          FROM OrderDetails od
          GROUP BY od.OrderID
        ),
        GeneralOrderValue AS (
          SELECT ROUND(AVG(ov.value), 2) AS average
          FROM OrderValues ov
        )
        SELECT
          c.CustomerID,
          ROUND(AVG(ov.value),2) AS avg_amount_per_customer
        FROM Customers c
        JOIN Orders o ON o.CustomerID = c.CustomerID
        JOIN OrderValues ov ON ov.OrderID = o.OrderID
        GROUP BY c.CustomerID
        HAVING AVG(ov.value) > (SELECT average FROM GeneralOrderValue)
        ORDER BY avg_amount_per_customer DESC
    '''
    return db.execute(request).fetchall()

def top_ordered_product_per_customer(db):
    # return the list of the top ordered product by each customer
    # based on the total ordered amount in USD
    query = """
        WITH OrderedProducts AS (
            SELECT
                CustomerID,
                ProductID, SUM(OrderDetails.Quantity * OrderDetails.UnitPrice) AS ProductValue
            FROM OrderDetails
            JOIN Orders ON OrderDetails.OrderID = Orders.OrderID
            GROUP BY Orders.CustomerID, OrderDetails.ProductID
            ORDER BY ProductValue DESC
        ),
        ranks AS (
        SELECT
            OrderedProducts.CustomerID,
            OrderedProducts.ProductID,
            OrderedProducts.ProductValue,
            RANK() OVER(PARTITION BY OrderedProducts.CustomerID ORDER BY OrderedProducts.ProductValue DESC) as order_rank
            FROM OrderedProducts
            )
        SELECT ranks.CustomerID,ranks.ProductID, ranks.ProductValue
        from ranks
        WHERE order_rank = 1
        ORDER BY ranks.ProductValue DESC
    """
    return db.execute(query).fetchall()

def average_number_of_days_between_orders(db):
    # return the average number of days between two consecutive orders of the same customer
    query = """
    WITH CustomerOrders AS (
        SELECT
            o.CustomerID,
            o.OrderDate,
            LAG(o.OrderDate) OVER (PARTITION BY o.CustomerID ORDER BY o.OrderDate) AS PrevOrderDate
        FROM Orders o
    )
    SELECT
        ROUND(AVG(JULIANDAY(OrderDate) - JULIANDAY(PrevOrderDate))) AS AverageDaysBetween
    FROM CustomerOrders
    WHERE PrevOrderDate IS NOT NULL
    """
    result = db.execute(query)
    return int(result.fetchone()[0])
