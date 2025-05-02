# common/protocol.py
import enum

# 8. Estilos de Protocolo de Troca – R, RR e RRA com HTTP
class CommunicationMode(enum.Enum):
    """Defines the communication styles."""
    R = "R"    # Request
    RR = "RR"  # Request-Response (Confirmed)
    RRA = "RRA" # Request-Response-Async Acknowledgment

DEFAULT_MODE = CommunicationMode.RR