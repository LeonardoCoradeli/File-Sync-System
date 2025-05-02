import enum

class CommunicationMode(enum.Enum):
    R = "R"
    RR = "RR"
    RRA = "RRA"

DEFAULT_MODE = CommunicationMode.RR