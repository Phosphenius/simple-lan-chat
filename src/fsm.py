# -*- coding: utf-8 -*-

"""
This module contains the base classes needed to build a finite state machine.
"""


from abc import ABCMeta, abstractmethod


class FiniteStateMachine(object):

    """
    Simple, abstract base class for a finite state machine.
    """

    __metaclass__ = ABCMeta

    def __init__(self, init_state=None):
        self.curr_state = init_state
        if init_state is not None and hasattr(self.curr_state, 'enter'):
            self.curr_state.enter()


    def change_state(self, new_state):
        if (self.curr_state is not None and
        hasattr(self.curr_state, 'leave')):
            self.curr_state.leave(fsm)

        old_state = self.curr_state
        self.curr_state = new_state
        if hasattr(self.curr_state, 'enter'):
            self.curr_state.enter(self, old_state)
