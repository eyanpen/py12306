from autoticket.data.route import route
from autoticket.data.data import sys_data


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

    mydata = sys_data()
    mydata.routes.append(my_route)
    print(mydata)
    mydata.saveToFile()

    loadData=sys_data.loadFromFile()
    print(loadData)