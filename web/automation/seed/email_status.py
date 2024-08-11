from web.database.model import EmailStatus, EmailStatusId

email_status_seeds = [
    EmailStatus(id=EmailStatusId.QUEUED, name="Queued", order=100),
    EmailStatus(id=EmailStatusId.SENT, name="Sent", order=200),
    EmailStatus(id=EmailStatusId.FAILED, name="Failed", order=300),
]
