from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """
    Configuration, loaded entirely from .env
    """
    sphere_radius: float
    frequency: int
    opening: float
    line_width: float
    colormap: str
    background_color: str
    title_color: str
    figure_size: float
    show_title: bool
    elevation: float
    start_azimuth: float
    spin: bool
    spin_speed: float
    frame_interval: int
    frame_count: int
