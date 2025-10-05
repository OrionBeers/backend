from infrastructure.database.collections.dashboard_collection import DashboardCollection

class DashboardDetails:
    def __init__(self, uid, history_id):
        self.uid = uid
        self.history_id = history_id
      
    def execute(self):
      if self.history_id:
        dashboard =  DashboardCollection().get_one(
          filter_by={"id_user": self.uid, "_id":self.history_id}, hidden_fields=[], force_show_fields=[])
        if not dashboard:
          raise Exception("Dashboard not found")

      else:
        dashboard =  DashboardCollection().list(
          filter_by={"id_user": self.uid}, hidden_fields=["historic_data"], force_show_fields=[])
        if not dashboard:
          raise Exception("Dashboard not found")


