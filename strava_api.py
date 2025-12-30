from stravaio import strava_oauth2, StravaIO
from notion_api import NotionInterface

# --- CONFIG ---
STRAVA_CLIENT_ID = "192679"
STRAVA_CLIENT_SECRET = "619046f4581ee532585919dc0695401d4ce756f7"

# Use your secret_... token and the 32-character ID of your parent page
NOTION_TOKEN = "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"
PARENT_PAGE_ID = "2d9d1473272f8073a14af1d70d208b7d"
# --------------

# 1. Get Strava Data
token = strava_oauth2(client_id=STRAVA_CLIENT_ID, client_secret=STRAVA_CLIENT_SECRET)
client = StravaIO(access_token=token["access_token"])
activities = client.get_logged_in_athlete_activities()

# 2. Upload to Notion
notion = NotionInterface(NOTION_TOKEN, PARENT_PAGE_ID)
db_id = notion.get_or_create_database()

for activity in activities:
    notion.add_row_to_table(db_id, activity)

print("Finished syncing activities!")
