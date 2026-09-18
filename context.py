import uuid
from db import get_connection
import json

def get_or_create_conversation(customer_id):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Look for an existing open conversation
        query = """
            SELECT TOP 1 id
            FROM conversations
            WHERE customer_id = ?
              AND status = 'open'
            ORDER BY created_at DESC
        """
       
        cursor.execute(query, customer_id)

        row = cursor.fetchone()

        if row:
            return str(row.id)

        # No open conversation → create one
        conversation_id = uuid.uuid4()

        cursor.execute("""
            INSERT INTO conversations
                (id, customer_id, status)
            VALUES
                (?, ?, 'open')
        """,
        conversation_id,
        customer_id)

        cursor.execute("""
            INSERT INTO conversation_state
                (conversation_id, customer_id)
            VALUES
                (?, ?)
        """,
        conversation_id,
        customer_id)

        conn.commit()

        return str(conversation_id)

    finally:
        conn.close()

def get_recent_messages(conversation_id, limit=10):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TOP (?)
                role,
                content,
                created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at DESC
        """,
        limit,
        conversation_id)

        rows = cursor.fetchall()

        rows.reverse()

        return [
            {
                "role": row.role,
                "content": row.content
            }
            for row in rows
        ]

    finally:
        conn.close()


def get_conversation_state(conversation_id):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                customer_id,
                active_order_id,
                active_ticket_id,
                intent,
                issue,
                status,
                facts,
                pending_items,
                actions_taken
            FROM conversation_state
            WHERE conversation_id = ?
        """,
        conversation_id)

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "customer_id": row.customer_id,
            "active_order_id": str(row.active_order_id)
                if row.active_order_id else None,
            "active_ticket_id": str(row.active_ticket_id)
                if row.active_ticket_id else None,
            "intent": row.intent,
            "issue": row.issue,
            "status": row.status,
            "facts": json.loads(row.facts or "[]"),
            "pending_items": json.loads(
                row.pending_items or "[]"
            ),
            "actions_taken": json.loads(
                row.actions_taken or "[]"
            )
        }

    finally:
        conn.close()


def save_message(conversation_id, role, content):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages
                (conversation_id, role, content, created_at)
            VALUES
                (?, ?, ?, SYSDATETIME())
        """,
        conversation_id,
        role,
        content)

        cursor.execute("""
            UPDATE conversations
            SET updated_at = SYSDATETIME()
            WHERE id = ?
        """,
        conversation_id)

        conn.commit()

    finally:
        conn.close()

def build_context(customer_id, conversation_id):

    state = get_conversation_state(
        conversation_id
    )

    messages = get_recent_messages(
        conversation_id,
        limit=5
    )

    return {
        "customer_id": customer_id,
        "conversation_id": str(conversation_id),
        "state": state,
        "recent_messages": messages
    }



if __name__ == "__main__":
    customers= get_or_create_conversation(1)
    print(customers)