import json

class route:
    def __init__(self):
        #上海
        self.from_station_name=None
        #衡阳
        self.to_station_name=None
        #SHH
        self.from_station_code=None
        #HYQ
        self.to_station_code=None
        #depart date
        self.depart_date=None
        # Ticket release data
        self.release_date=None
        #For example: G318, K511
        self.trainIds=[]
        pass
    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)

    def to_dict(self):
        return self.__dict__

if __name__ == "__main__":
    my_route = route()
    my_route.from_station_name = "上海"
    my_route.to_station_name = "衡阳"
    my_route.from_station_code = "SHH"
    my_route.to_station_code = "HYQ"
    my_route.depart_date = "2026-01-20"
    my_route.release_date = "2026-01-05"
    my_route.trainIds = ["G318", "K511"]

    print(my_route)