# Proves an interface for external databases

def get_material():
    return [
    {
        "virtual_available": -18.0,
        "name": "Acrylglas 3mm",
        "id": 15,
        "cut_speed": "1600",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 0.0,
    }, {
        "virtual_available": -5.0,
        "name": "Acrylglas 5mm",
        "image": False,
        "id": 16,
        "cut_speed": "900",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 0.0,
        "description": False
    }, {
        "virtual_available": 0.0,
        "name": "Acrylglas 8mm",
        "image": False,
        "id": 17,
        "cut_speed": "550",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 0.0,
        "description": False
    }, {
        "virtual_available": -9.0,
        "name": "Anderes Lasermaterial",
        "image": False,
        "id": 18,
        "cut_speed": "1500",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 0.0,
        "description": False
    }, {
        "virtual_available": -41.0,
        "name": "Buche 4mm",
        "image": False,
        "id": 19,
        "cut_speed": "1500",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 8.5,
        "description": False
    }, {
        "virtual_available": -17.0,
        "name": "Buche 5mm",
        "image": False,
        "id": 20,
        "cut_speed": "1100",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 10.0,
        "description": False
    }, {
        "virtual_available": -21.0,
        "name": "Buche 8mm",
        "image": False,
        "id": 21,
        "cut_speed": "700",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 14.0,
        "description": False
    }, {
        "virtual_available": -3.0,
        "name": "Gabun 10mm",
        "image": False,
        "id": 22,
        "cut_speed": "800",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 11.0,
        "description": False
    }, {
        "virtual_available": -2.0,
        "name": "Gabun 8mm",
        "image": False,
        "id": 23,
        "cut_speed": "900",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 10.0,
        "description": False
    }, {
        "virtual_available": -60.0,
        "name": "HDF 3mm",
        "image": False,
        "id": 24,
        "cut_speed": "1800",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 4.0,
        "description": False
    }, {
        "virtual_available": -26.0,
        "name": "HDF 4mm",
        "image": False,
        "id": 25,
        "cut_speed": "1200",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 4.5,
        "description": False
    }, {
        "virtual_available": -14.5,
        "name": "Pappel 3mm",
        "image": False,
        "id": 27,
        "cut_speed": "3000",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 6.5,
        "description": False
    }, {
        "virtual_available": -10.0,
        "name": "Pappel 5mm",
        "image": False,
        "id": 28,
        "cut_speed": "2300",
        "engrave_speed": "4000",
        "cut_intensity": "100",
        "engrave_intensity": "30",
        "price": 7.5,
        "description": False
    }
]

def get_services():
    return [
    {
        "virtual_available": 0.0,
        "name": "Laserminute kommerziell",
        "image": False,
        "id": 33,
        "price": 1.0,
        "description": False
    }, {
        "virtual_available": 0.0,
        "name": "Laserminute Labintern",
        "image": False,
        "id": 34,
        "price": 0.0,
        "description": False
    }, {
        "virtual_available": 0.0,
        "name": "Laserminute Mitglied",
        "image": False,
        "id": 35,
        "price": 0.5,
        "description": False
    }, {
        "virtual_available": 0.0,
        "name": "Laserminute Nichtmitglied",
        "image": False,
        "id": 36,
        "price": 1.0,
        "description": False
    }]


def authenticate(user, password):
    return {
        'email': 'otto@otto.de',
        'name': 'Otto O.'
    }
