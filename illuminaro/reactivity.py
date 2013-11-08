import inspect
import re
import argparse


class ReactiveValue(object):
    def __init__(self, parent_set, name, value):
        self.parent_set = parent_set
        self.name = name
        self._value = value
        self.dirty = False
        self.dependants = set()

    def value(self):
        stack = inspect.stack()

        # half-assed attempt to retrieve left hand side of the assignment
        if self.parent_set._debug:
            print 'ReactiveValue.value (%s): stack: %s' % (self.name, str(stack))
        if len(stack) > 2 and len(stack[2]) > 4 and stack[2][4] is not None and len(stack[2][4])>0:
            assignment = stack[2][4][0]
            lhs = assignment.split('=')[0].split('.')[1].strip()
            m = re.match(r'^[a-zA-Z0-9][a-zA-Z0-9]*$', lhs)
            if m:
                self.dependants.add(lhs)

        if self.dirty:
            # recalculate value
            res = None
            v = self.parent_set
            res = eval(self.expression)
            self._value = res
            self.dirty = False

        return self._value

    def notify(self):
        for dependant in self.dependants:
            self.parent_set._values[dependant].notify()
        self.dirty = True

    def set_value(self, value):
        stack = inspect.stack()
        if len(stack) > 2 and len(stack[2]) > 4 and stack[2][4] is not None and len(stack[2][4])>0:
            expression = stack[2][4][0]
            self.expression = '='.join(expression.split('=')[1:])
            for dependant in self.dependants:
                self.parent_set._values[dependant].notify()
                
        self._value = value


class ReactiveSet(object):
    def __init__(self, **kwargs):
        # to avoid recursion
        object.__setattr__(self, '_values', dict())
        object.__setattr__(self, '_debug', False)
        for k, v in kwargs.iteritems():
            if k == '_debug':
                object.__setattr__(self, '_debug', v)
            else:
                self._values[k] = ReactiveValue(self, k, v)

    def __getattr__(self, key):
        if key == '_debug':
            return object.__getattr__(self, '_debug')
        else:
            return self._values[key].value()

    def __setattr__(self, key, value):
        self._values[key].set_value(value)


def reactive(expression):
    pass


def reactive_test():
    v = ReactiveSet(a=2, b=3, c=7, d=10)
    v.c = v.a + v.b
    v.d = v.c * 10
    print v.c, v.d
    v.a = 8
    print v.c, v.d


def namespace_test():
    ns = argparse.Namespace(a=1, b=2)
    ns.__setattr__('c', 23)
    ns.d = 12
    print ns.a, ns.b, ns.c, ns.d


if __name__ == "__main__":
    namespace_test()