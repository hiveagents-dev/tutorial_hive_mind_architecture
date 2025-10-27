"""Agent-to-Agent (A2A) communication protocol for HiveMind system."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages in A2A protocol."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MessagePriority(str, Enum):
    """Message priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class A2AMessage(BaseModel):
    """
    Agent-to-Agent message structure.

    This follows a simplified A2A protocol for inter-agent communication.

    Attributes:
        message_id: Unique message identifier.
        sender: Sender agent name.
        recipient: Recipient agent name (or "broadcast").
        message_type: Type of message.
        priority: Message priority.
        content: Message content.
        metadata: Additional metadata.
        timestamp: Message timestamp.
        parent_message_id: ID of parent message if this is a response.
    """
    message_id: str
    sender: str
    recipient: str
    message_type: MessageType
    priority: MessagePriority = MessagePriority.MEDIUM
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    parent_message_id: Optional[str] = None


class CommunicationBus:
    """
    Communication bus for agent message passing and logging.

    This class manages all inter-agent communication, providing:
    - Message routing
    - Message history
    - Communication logging
    - Message analytics
    """

    def __init__(self):
        """Initialize communication bus."""
        self.messages: List[A2AMessage] = []
        self.message_count = 0
        logger.info("CommunicationBus initialized")

    def send_message(
        self,
        sender: str,
        recipient: str,
        content: str,
        message_type: MessageType = MessageType.REQUEST,
        priority: MessagePriority = MessagePriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        parent_message_id: Optional[str] = None
    ) -> A2AMessage:
        """
        Send a message from one agent to another.

        Args:
            sender: Sender agent name.
            recipient: Recipient agent name.
            content: Message content.
            message_type: Type of message.
            priority: Message priority.
            metadata: Additional metadata.
            parent_message_id: Parent message ID if response.

        Returns:
            A2AMessage: The sent message.
        """
        self.message_count += 1
        message_id = f"msg_{self.message_count:04d}"

        message = A2AMessage(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            priority=priority,
            content=content,
            metadata=metadata or {},
            parent_message_id=parent_message_id
        )

        self.messages.append(message)

        logger.info(
            f"Message {message_id}: {sender} → {recipient} "
            f"[{message_type.value}] ({priority.value})"
        )

        return message

    def get_conversation(
        self,
        agent1: str,
        agent2: str
    ) -> List[A2AMessage]:
        """
        Get all messages between two agents.

        Args:
            agent1: First agent name.
            agent2: Second agent name.

        Returns:
            List of messages between the agents.
        """
        return [
            msg for msg in self.messages
            if (msg.sender == agent1 and msg.recipient == agent2) or
               (msg.sender == agent2 and msg.recipient == agent1)
        ]

    def get_agent_messages(
        self,
        agent_name: str,
        direction: str = "all"
    ) -> List[A2AMessage]:
        """
        Get all messages for a specific agent.

        Args:
            agent_name: Agent name.
            direction: "sent", "received", or "all".

        Returns:
            List of relevant messages.
        """
        if direction == "sent":
            return [msg for msg in self.messages if msg.sender == agent_name]
        elif direction == "received":
            return [msg for msg in self.messages if msg.recipient == agent_name]
        else:  # all
            return [
                msg for msg in self.messages
                if msg.sender == agent_name or msg.recipient == agent_name
            ]

    def get_message_thread(
        self,
        message_id: str
    ) -> List[A2AMessage]:
        """
        Get a message and all its responses (thread).

        Args:
            message_id: Root message ID.

        Returns:
            List of messages in the thread.
        """
        thread = []

        # Find root message
        root = next((msg for msg in self.messages if msg.message_id == message_id), None)
        if root:
            thread.append(root)

            # Find all responses
            responses = [
                msg for msg in self.messages
                if msg.parent_message_id == message_id
            ]
            thread.extend(responses)

            # Recursively get sub-threads
            for response in responses:
                sub_thread = self.get_message_thread(response.message_id)
                thread.extend(sub_thread[1:])  # Skip root as it's already included

        return thread

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get communication statistics.

        Returns:
            dict: Statistics about communication activity.
        """
        if not self.messages:
            return {
                "total_messages": 0,
                "agents": [],
                "message_types": {},
                "priority_distribution": {}
            }

        agents = set()
        for msg in self.messages:
            agents.add(msg.sender)
            agents.add(msg.recipient)

        message_types = {}
        for msg_type in MessageType:
            count = sum(1 for msg in self.messages if msg.message_type == msg_type)
            message_types[msg_type.value] = count

        priority_dist = {}
        for priority in MessagePriority:
            count = sum(1 for msg in self.messages if msg.priority == priority)
            priority_dist[priority.value] = count

        return {
            "total_messages": len(self.messages),
            "agents": list(agents),
            "agent_count": len(agents),
            "message_types": message_types,
            "priority_distribution": priority_dist,
            "first_message": self.messages[0].timestamp if self.messages else None,
            "last_message": self.messages[-1].timestamp if self.messages else None
        }

    def get_communication_flow(self) -> List[Dict[str, str]]:
        """
        Get simplified communication flow for visualization.

        Returns:
            List of message flow entries.
        """
        return [
            {
                "id": msg.message_id,
                "from": msg.sender,
                "to": msg.recipient,
                "type": msg.message_type.value,
                "timestamp": msg.timestamp
            }
            for msg in self.messages
        ]

    def export_log(self) -> str:
        """
        Export complete communication log.

        Returns:
            str: Formatted communication log.
        """
        if not self.messages:
            return "No messages in communication log."

        log_lines = ["=" * 80, "COMMUNICATION LOG", "=" * 80, ""]

        for msg in self.messages:
            log_lines.append(f"[{msg.timestamp}] {msg.message_id}")
            log_lines.append(f"  {msg.sender} → {msg.recipient}")
            log_lines.append(f"  Type: {msg.message_type.value} | Priority: {msg.priority.value}")

            if msg.parent_message_id:
                log_lines.append(f"  In response to: {msg.parent_message_id}")

            # Truncate content if too long
            content_preview = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            log_lines.append(f"  Content: {content_preview}")

            if msg.metadata:
                log_lines.append(f"  Metadata: {msg.metadata}")

            log_lines.append("")

        log_lines.extend(["=" * 80, "END OF LOG", "=" * 80])

        return "\n".join(log_lines)

    def clear(self) -> None:
        """Clear all messages from the bus."""
        self.messages = []
        self.message_count = 0
        logger.info("CommunicationBus cleared")

    def __repr__(self) -> str:
        """String representation."""
        return f"CommunicationBus(messages={len(self.messages)})"
