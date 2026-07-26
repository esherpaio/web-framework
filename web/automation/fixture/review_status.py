from web.database.model import ReviewStatus, ReviewStatusId

review_status_seeds = [
    ReviewStatus(id=ReviewStatusId.PENDING, name="Pending", order=100),
    ReviewStatus(id=ReviewStatusId.APPROVED, name="Approved", order=200),
    ReviewStatus(id=ReviewStatusId.REJECTED, name="Rejected", order=300),
]
