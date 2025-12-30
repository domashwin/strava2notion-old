from notion_client import Client
import datetime

class NotionInterface:
    def __init__(self, token, parent_page_id):
        # Your specific Token V2 and IDs
        self.token = "v03%3AeyJhbGciOiJkaXIiLCJraWQiOiJwcm9kdWN0aW9uOnRva2VuLXYzOjIwMjQtMTEtMDciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIn0..iAWvUCjP4sO7RO-ajpv7xg.8o51zPy3g_RkE_x6zRveHM7_vgkXFN712bnewrHnXr8zJZ6o21qVDm18wzeKKSx4mL6T1cxQXnuOSRdMTnSfbpBvR6OfC0ECltoR57Q9GXmYmn1oAzavYWPHJMAfoHttD2mKSDZ_WqwrunOhq0AClsHcG1-N78Lwoq0MiPoupLazt-p8scmRbPSnxv4AAVWmemApNGPlcun2Gg5k9B4CUO9BLKs76j2eB1pUWFE4gWKzMI8vEC_ZxJeKayaieYiKHAyq7FRXaj-513-xSCRgxcZX-_gQdw2QK8uA0bPBN9Nrzo-cySQongdIArfJ7lhj936mAdEQUuemoKYKj92b6R8rMmnEudnjveIqoWIt7Mo.LNVrdrsBOVS62L8zw_W2yOLVJZCQQo7bm2yAfI4Tlqk"
        self.client = Client(auth=self.token)
        self.strava_table_title = "Strava Activities Final"
        # IMPORTANT: This must be the ID of the page where you want the table
        # You can find it in the URL of your Notion page
        self.parent_page_id = "738942b0805c48b292023946654e00ad" 

    def create_activity_log_table(self):
        # Search for existing database
        search_results = self.client.search(query=self.strava_table_title).get("results", [])
        for result in search_results:
            if result["object"] == "database" and not result.get("archived"):
                print(f"Found existing database: {result['id']}")
                return result["id"]

        # Create the database if not found
        print(f"Creating fresh database: {self.strava_table_title}...")
        new_db = self.client.databases.create(
            parent={"type": "page_id", "page_id": self.parent_page_id},
            title=[{"type": "text", "text": {"content": self.strava_table_title}}],
            properties={
                "Activity Name": {"title": {}},
                "Date": {"date": {}},
                "Type": {"select": {}},
                "Distance (m)": {"number": {}},
                "Time (s)": {"number": {}},
                "Calories": {"number": {}},
                "Avg Speed (m/s)": {"number": {}}
            }
        )
        return new_db["id"]

    def add_row_to_table(self, database_id, data):
        # Standardize date format
        date_str = data.start_date_local.strftime("%Y-%m-%d")
        
        # Duplicate check
        query = self.client.databases.query(
            database_id=database_id,
            filter={
                "and": [
                    {"property": "Activity Name", "title": {"equals": str(data.name)}},
                    {"property": "Date", "date": {"equals": date_str}}
                ]
            }
        )
        if query.get("results"):
            print(f"Skipping duplicate: {data.name}")
            return

        # Map Strava data to Notion properties
        # Note: These keys MUST match the properties defined in create_activity_log_table
        properties = {
            "Activity Name": {"title": [{"text": {"content": str(data.name)}}]},
            "Date": {"date": {"start": date_str}},
            "Type": {"select": {"name": str(data.type)}},
            "Distance (m)": {"number": float(data.distance or 0)},
            "Time (s)": {"number": int(data.moving_time or 0)},
            "Calories": {"number": float(getattr(data, 'calories', 0) or 0)},
            "Avg Speed (m/s)": {"number": float(data.average_speed or 0)}
        }

        try:
            self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            print(f"Added: {data.name}")
        except Exception as e:
            print(f"Failed to add {data.name}: {e}")
