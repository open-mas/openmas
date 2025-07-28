"""
OpenMAS Agent Interfaces

This module provides the core interfaces for implementing Body-Brain separation
in OpenMAS agents, enabling reasoning agnosticism and protocol independence.
"""

from .communicator import ICommunicator
from .reasoning import IReasoningEngine

__all__ = ["ICommunicator", "IReasoningEngine"]
