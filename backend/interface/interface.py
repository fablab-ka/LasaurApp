# Proves an interface for external databases


class ExtInterface:
    def get_info(self):
        return {
            'materials': [{
                'name': "Lasermaterial",
                'id': 1,
                'machine_parameter_1': 1500,
                'machine_parameter_2': 100,
                'machine_parameter_3': 4000,
                'machine_parameter_4': 30,
                'price': 0,
            }],
            'usage': [{
                'name': "Mitglied",
                'id': 33,
                'price': 0.50,
            }]
        }

    def set_info(self, job):
        print(job)
        # with open("laserjobs.csv", "a+") as file:
        #     line = job['user']
        #     line += ", " + job['']