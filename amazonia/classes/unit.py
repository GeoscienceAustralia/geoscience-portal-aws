# pylint: disable=too-many-arguments, line-too-long

from amazonia.classes.elb import Elb
from amazonia.classes.asg import Asg
from amazonia.classes.database import Database


class Unit(object):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(object, self).__init__()

        elb = Elb()
        asg = Asg()


        # TODO UNIT Unit Tests:
        # TODO Sys Tests:

        if kwargs.get(database):
            database(**kwargs)


