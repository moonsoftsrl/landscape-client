
class StateError(Exception):
    """
    An exception that is raised when there is an error relating to the current
    state.
    """

class ConfigurationState(object):
    """
    Abstract base class for states used in the L{ConfigurationModel}.
    """
    
    def load_data(self):
        raise NotImplementedError

    def test(self, test_method):
        raise NotImplementedError
    
    def modify(self):
        raise NotImplementedError


class ModifiableHelper(object):
    """
    Allow a L{ConfigurationState}s to be modified.
    """

    def modify(self):
        return ModifiedState()

class UnloadableHelper(object):
    
    def load_data(self):
        raise StateError, "A ConfiguratiomModel in a " + \
            self.__class__.__name__ + " cannot be transitioned via load_data()"


class UnmodifiableHelper(object):
    """
    Disallow modification of a L{ConfigurationState}.
    """

    def modify(self):
        raise StateError, "A ConfigurationModel in " + \
            self.__class__.__name__ + " cannot transition via modify()"


class UntestableHelper(object):
    """
    Disallow testing of a L{ConfigurationState}.
    """

    def test(self, test_method):
        raise StateError, "A ConfigurationModel in " + \
            self.__class__.__name__ + " cannot transition via test()"


class ModifiedState(ConfigurationState):
    
    helper = ModifiableHelper()
    
    def modify(self):
        return self.helper.modify()


class TestedState(ConfigurationState):

    untestable_helper = UntestableHelper()
    unloadable_helper = UnloadableHelper()
    modifiable_helper = ModifiableHelper()
    
    def test(self, test_method):
        return self.untestable_helper.test(test_method)

    def load_data(self):
        return self.unloadable_helper.load_data()

    def modify(self):
        return self.modifiable_helper.modify()


class TestedBadState(TestedState):
    pass
    

class TestedGoodState(TestedState):
    pass


class InitialisedState(ConfigurationState):
    """
    The state of the L{ConfigurationModel} as initially presented to the
    user. Baseline data should have been loaded from the real configuration
    data, any persisted user data should be loaded into blank values and
    finally defaults should be applied where necessary.
    """

    helper = ModifiableHelper()
    
    def load_data(self):
        return self

    def test(self, test_method):
        if test_method():
            return TestedGoodState()
        else:
            return TestedBadState()

    def modify(self):
        return self.helper.modify()


class VirginState(ConfigurationState):
    """
    The state of the L{ConfigurationModel} before any actions have been taken
    upon it.
    """
    
    untestable_helper = UntestableHelper()
    unmodifiable_helper = UnmodifiableHelper()
    
    def load_data(self):
        return InitialisedState()

    def test(self, test_method):
        return self.untestable_helper.test(test_method)

    def modify(self):
        return self.unmodifiable_helper.modify()


class ConfigurationModel(object):
    
    def __init__(self, test_method=None):
        self._current_state = VirginState()
        if test_method:
            self._test_method = test_method
        else:
            self._test_method = self._test

    def _test(self):
        # TODO, dump this and use something real
        return True
    
    def get_state(self):
        return self._current_state

    def load_data(self):
        self._current_state = self._current_state.load_data()
        
    def test(self):
        self._current_state = self._current_state.test(self._test_method)

    def modify(self):
        self._current_state = self._current_state.modify()
