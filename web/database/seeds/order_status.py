from web.database.model import OrderStatus, OrderStatusId

order_status_seeds = [
    OrderStatus(id=OrderStatusId.COMPLETED, name="Completed", order=500),
    OrderStatus(id=OrderStatusId.PAID, name="Paid", order=200),
    OrderStatus(id=OrderStatusId.PENDING, name="Pending", order=100),
    OrderStatus(id=OrderStatusId.PRODUCTION, name="Production", order=300),
    OrderStatus(id=OrderStatusId.READY, name="Ready", order=400),
]
