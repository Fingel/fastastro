from typing import Optional


class SourceFilter:
    def __init__(
        self,
        name_contains: Optional[str] = None,
        cone_ra: Optional[float] = None,
        cone_dec: Optional[float] = None,
        cone_radius: Optional[float] = None,
    ):
        self.name_contains = name_contains
        self.cone_ra = cone_ra
        self.cone_dec = cone_dec
        self.cone_radius = cone_radius

    @property
    def cone(self) -> tuple:
        if all((self.cone_ra, self.cone_dec, self.cone_radius)):
            return (self.cone_ra, self.cone_dec, self.cone_radius)
        return ()
