from infrastructure.database.collections.dashboard_collection import DashboardCollection

class DashboardDetails:
    def __init__(self, uid, history_id):
        self.uid = uid
        self.history_id = history_id
      
    def execute(self):
      print(f"DashboardDetails.execute() - uid: {self.uid}, history_id: {self.history_id}")
      
      # Debug: Check if any data exists in the collection
      all_data = DashboardCollection().list(filter_by={}, hidden_fields=[], force_show_fields=[])
      if self.history_id:
        print("Searching for specific dashboard with history_id")
        dashboard =  DashboardCollection().get_one(
          filter_by={"id_user": self.uid, "_id":self.history_id}, hidden_fields=[], force_show_fields=[])
        print(f"Single dashboard result: {dashboard}")
        if not dashboard:
          raise Exception(f"Dashboard not found for user {self.uid} with history_id {self.history_id}")
        return [dashboard]
      else:
        print("Searching for all dashboards for user")
        dashboard =  DashboardCollection().list(
          filter_by={"id_user": self.uid}, hidden_fields=["calendar"], force_show_fields=[])
        print(f"Dashboard list result: {dashboard}")
        return dashboard


