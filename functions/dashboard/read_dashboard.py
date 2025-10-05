from infrastructure.database.collections.dashboard_collection import DashboardCollection

class DashboardDetails:
    def __init__(self, id_user, history_id):
        self.id_user = id_user
        self.history_id = history_id
      
    def execute(self):
      print(f"DashboardDetails.execute() - uid: {self.id_user}, history_id: {self.history_id}")
      
      if self.history_id:
        print("Searching for specific dashboard with history_id")
        dashboard =  DashboardCollection().get_one(
          filter_by={"id_user": self.id_user, "_id":self.history_id}, hidden_fields=[], force_show_fields=[])
        print(f"Single dashboard result: {dashboard}")
        if not dashboard:
          raise Exception(f"Dashboard not found for user {self.id_user} with history_id {self.history_id}")
        return [dashboard]
      else:
        print("Searching for all dashboards for user")
        dashboard =  DashboardCollection().list(
          filter_by={"id_user": self.id_user}, hidden_fields=["calendar"], force_show_fields=[])
        print(f"Dashboard list result: {dashboard}")
        return dashboard


