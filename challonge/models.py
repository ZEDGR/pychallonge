from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tournament:
    id: int
    name: str
    url: str
    tournament_type: str
    state: str
    description: str | None = None
    game_name: str | None = None
    game_id: int | None = None
    private: bool = False
    open_signup: bool = False
    hold_third_place_match: bool = False
    teams: bool = False
    signup_cap: int | None = None
    check_in_duration: int | None = None
    participants_count: int = 0
    prediction_method: int = 0
    swiss_rounds: int = 0
    starts_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    predictions_opened_at: datetime | None = None
    check_in_opened_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Participant:
    id: int
    tournament_id: int
    name: str
    seed: int
    active: bool = True
    final_rank: int | None = None
    username: str | None = None
    email: str | None = None
    group_id: int | None = None
    misc: str | None = None
    checked_in: bool = False
    checked_in_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Match:
    id: int
    tournament_id: int
    state: str
    round: int
    identifier: str
    player1_id: int | None = None
    player2_id: int | None = None
    player1_prereq_match_id: int | None = None
    player2_prereq_match_id: int | None = None
    winner_id: int | None = None
    loser_id: int | None = None
    scores_csv: str | None = None
    suggested_play_order: int | None = None
    group_id: int | None = None
    has_attachment: bool = False
    underway_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class MatchAttachment:
    id: int
    match_id: int
    url: str | None = None
    description: str | None = None
    asset_file_name: str | None = None
    asset_content_type: str | None = None
    asset_file_size: int | None = None
    asset_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
