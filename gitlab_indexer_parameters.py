from dataclasses import dataclass
from typing import Optional


@dataclass
class GitLabIndexerParameters:
    gitlab_personal_token: str
    min_stars: Optional[int] = None
    min_forks: Optional[int] = None
    max_inactivity_in_days: Optional[int] = None
