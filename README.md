[![GetBadges Game](https://fablab-ka-lasaurapp.getbadges.io/shield/company/fablab-ka-lasaurapp)](https://fablab-ka-lasaurapp.getbadges.io/?ref=shield-game)

LasaurApp (FabLab Karlsruhe)
=========
This is a fork of the official [Lasersaur](http://lasersaur.com) app.

It is tuned to run together with [Odoo](http://odoo.com) for administrative purposed, but can also be used as a standalone.
To use the app with odoo, you need an instance of Odoo 10 running, and to install the module [machine_management](TODO Link).

Work in Progress
=========
  - Add Authentification with Odoo for Laser Customers (not Laser Users, as those are already auhentificated with their ID Card)
  - Send Laser Job information to Odoo, currently only for logging.

Planed
=========
  - Send Laser Job information to Odoo for payment purposes.
  - Show estimated Laser Job duration and total job cost before starting the job.


Finished
=========
  - Add materials that can be selected and have their own cutting parameters - materials are extracted from odoo
  - Add ID Card authentification, Users are saved in odoo.
  -



Using the lasaurapp with odoo
==========
An instance of Odoo 10.0 is required.
The module machine_management has to be installed

The following models have to be created:
  - Lab->Machine: This is the LaserSaur as seen in Odoo. Most parameters should be self-explanatory.
    - 'name': "LaserSaur"
    - 'status': "running" or "out of order"
    - 'rules': "free for all" to allow anyone with an ID Card to use the Laser, "restricted" to only allow users in "users" and "owners" to use it, "no access" to disable access
    - 'users': List of allowed Users. Each User should have an ID Card assigned to him
    - 'owners': currently same as "users", they are the peaple responsible for the LaserSaur
    - 'Product Tag 1': Used to tag products that are materials to be used with the Laser
    - 'Product tag 2': Used to tag products functioning as services containing the cost per minute of the use

  - Stock->Products: There is an additional tab "machien stuff" added wich contains material parameters.
    - 'parameter 1': Cut speed (mm/min)
    - 'parameter 2': Cut intensity (0-100%)
    - 'parameter 3': Engrave speed (mm/min)
    - 'parameter 4': Engrave intensity (0-100%)

  - Lab->ID-Card: Contains information about the ID Cards, cards have to be assigned to a user (res.partner) to be used. Currently only Serial Number authentification is used
    - 'card number': Serial Number of the Card, currently used for authentification
    - 'assigned client': the user (res.partner) to whom the Card belongs.
    - 'status': only "active" cards are functional.
    - 'card type': currently only "Serial Number" is supported
  - Settings->Users:
    You have to create a new User Account wich functions as the LaserSaur machine's user. It needs be in the security group "machine_users"


