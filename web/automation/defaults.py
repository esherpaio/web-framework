from .automator import Automator
from .task import (
    AppSettingSeedSyncer,
    EmailCleaner,
    EmailProcessor,
    EmailStatusSeedSyncer,
    FileTypeSeedSyncer,
    OrderStatusSeedSyncer,
    ProductLinkeTypeSeedSyncer,
    ProductTypeSeedSyncer,
    ReviewStatusSeedSyncer,
    UserRoleSeedSyncer,
)

DEFAULT_SERVER_TASKS: list[type[Automator]] = [
    AppSettingSeedSyncer,
    EmailStatusSeedSyncer,
    FileTypeSeedSyncer,
    OrderStatusSeedSyncer,
    ProductLinkeTypeSeedSyncer,
    ProductTypeSeedSyncer,
    ReviewStatusSeedSyncer,
    UserRoleSeedSyncer,
]
DEFAULT_WORKER_TASKS: list[type[Automator]] = [
    EmailProcessor,
    EmailCleaner,
]


def with_default_tasks(
    tasks: list[type[Automator]],
    *,
    worker: bool,
) -> list[type[Automator]]:
    defaults = DEFAULT_WORKER_TASKS if worker else DEFAULT_SERVER_TASKS
    missing = [d for d in defaults if not any(issubclass(t, d) for t in tasks)]
    return missing + list(tasks)
