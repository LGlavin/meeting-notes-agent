from langchain_core.tools import tool
from pyairtable import Api
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME


def _get_table():
    api = Api(AIRTABLE_API_KEY)
    return api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)


@tool
def save_meeting_notes(
    date: str,
    attendees: str,
    summary: str,
    action_items: str,
    decisions: str,
    follow_ups: str,
) -> str:
    """Save processed meeting notes to Airtable for tracking.

    Args:
        date: Meeting date (YYYY-MM-DD)
        attendees: Comma-separated list of attendees
        summary: Brief meeting summary
        action_items: Action items with owners, one per line
        decisions: Key decisions made, one per line
        follow_ups: Items to follow up on in the next meeting
    """
    table = _get_table()
    record = table.create({
        "Date": str(date),
        "Attendees": str(attendees),
        "Summary": str(summary),
        "Action Items": str(action_items),
        "Decisions": str(decisions),
        "Follow Ups": str(follow_ups),
    })
    return f"Meeting notes saved to Airtable (Record ID: {record['id']})"


@tool
def get_past_meeting_notes(attendee: str) -> str:
    """Look up past meeting notes for an attendee to find previous follow-ups.

    Args:
        attendee: Name of the person to look up past meetings for
    """
    table = _get_table()
    records = table.all(formula=f"FIND('{attendee}', {{Attendees}})")

    if not records:
        return f"No past meetings found with {attendee}."

    results = []
    for record in records[-3:]:  # Last 3 meetings
        fields = record["fields"]
        results.append(
            f"Date: {fields.get('Date', 'N/A')}\n"
            f"Summary: {fields.get('Summary', 'N/A')}\n"
            f"Follow Ups: {fields.get('Follow Ups', 'N/A')}\n"
            f"Action Items: {fields.get('Action Items', 'N/A')}"
        )
    return "\n\n---\n\n".join(results)


all_tools = [save_meeting_notes, get_past_meeting_notes]
