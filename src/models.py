from dataclasses import dataclass

@dataclass
class Connection:
    connection_type: str
    size: str
    offset: float

@dataclass
class CutRequest:
    connection_a: Connection
    connection_b: Connection
    center_to_center: float

    def __str__(self):
        return (
            f"Connection A: Type={self.connection_a.connection_type}, "
            f"Size={self.connection_a.size}, Offset={self.connection_a.offset}\n"
            f"Connection B: Type={self.connection_b.connection_type}, "
            f"Size={self.connection_b.size}, Offset={self.connection_b.offset}\n"
            f"Center-to-Center: {self.center_to_center}"
        )
