from abc import ABCMeta, abstractmethod, abstractproperty
import argparse

class SubCommand(object):
    '''
    Abstract class defining interface of subcommands
    '''
    __metaclass__ = ABCMeta

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

    def add_to_subparser(self, subparser):
        '''
        Adds this subcommand to the subparsers object of the command
        '''
        parser = subparser.add_parser(self.name, help=self.description, epilog=self.epilog)
        self.add_arguments_to_parser(parser)

    @abstractproperty
    def name(self):
        '''
        Returns the name of the subcommand
        '''
        pass

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

    def command_parser(self):
        parser = argparse.ArgumentParser(description=self.description, epilog=self.epilog)
        self.add_arguments_to_parser(parser)

