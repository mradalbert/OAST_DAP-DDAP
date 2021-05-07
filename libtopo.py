class Link:
    def __init__(self, data):
        self.start_node = int(data[0])
        self.end_node = int(data[1])
        self.modules_number = int(data[2])
        self.module_cost = float(data[3])
        self.link_module = int(data[4])

class Path:
    def __init__(self, data):
        self.links = [int(link) for link in data[1:]]

class Demand:
    def __init__(self, data):
        self.start_node = int(data[0])
        self.end_node = int(data[1])
        self.demand_volume = int(data[2])
        self.paths = []

class NetworkTopology:
    def __init__(self):
        self.links = []
        self.demands = []

class TopologyParser:

    @staticmethod
    def loadTopologyFromFile(file_path):
        print("Parsing topology file...")
        network = NetworkTopology()
        with open(file_path, 'r') as input_file:
            links_number = int(input_file.readline())

            for index in range(links_number):
                data = input_file.readline().strip().split(' ')
                link = Link(data)
                network.links.append(link)

            if input_file.readline().strip() == "-1":
                print("Parsing links success!")
            else:
                print("Parsing links failed! Expected new line! Exiting...")
                quit()

            input_file.readline()

            demands_number = int(input_file.readline())
            input_file.readline()

            for index in range(demands_number):
                data = input_file.readline().strip().split(' ')
                demand = Demand(data)
                paths_number = int(input_file.readline())

                for idx in range(paths_number):
                    data = input_file.readline().strip().split(' ')
                    path = Path(data)
                    demand.paths.append(path)

                network.demands.append(demand)

                if input_file.readline() != "\n":
                    print("Parsing demand #" + str(index) + " failed! Expected new line! Exiting...")
                    quit()

            print("Parsing demands success!")
            return network