from abc import ABCMeta, abstractmethod, abstractproperty
import argparse

class SubCommand(object):
    '''
    Abstract class defining interface of subcommands
    '''
    __metaclass__ = ABCMeta

    def __init__(self, subparser):
        '''
        Adds this subcommand to the subparsers object of the main command
        '''
        parser = subparser.add_parser(self.name, help=self.description, epilog=self.epilog)
        self.add_arguments_to_parser(parser)

    @abstractmethod
    def add_arguments_to_parser(self, parser):
        '''
        Adds all of the arguments and their defaults to a parser object
        '''
        pass

    @abstractmethod
    def run_from_args(self, args):
        '''
        Runs the subcommand from the args objects
        '''
        pass

    @classmethod
    def name(cls):
        '''
        Returns the name of the subcommand
        For convenience this is just the name of the class in lowercase
        Override if this isn't the behavior you want
        '''
        return cls.__name__.lower()

    @abstractproperty
    def description(self):
        '''
        Returns the description of the subcommand
        '''
        pass

    @property
    def epilog(self):
        '''
        Returns the epilog of the subcommand's help text
        '''
        return None
