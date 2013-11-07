
class Cell:
    def __init__(self, *args, **kwargs):
        self.observers = set()
        self._function = None
        self._args = None
        self._kwargs = None
        if args:
            value = args[0]
            newargs = args[1:]
            self.set(value, *newargs, **kwargs)
        else:
            self.set(None)

    def add_observer(self, other):
        self.observers.add(other)

    def observe(self, pred_cell):
        pred_cell.add_observer(self)

    def set(self, value, *args, **kwargs):
        if hasattr(value, '__call__'):
            self._function = value
            self._args = args
            self._kwargs = kwargs
            for arg in args:
                if isinstance(arg, Cell):
                    self.observe(arg)
            self._value = self._function(*self._args, **self._kwargs)
        else:
            self._function = None
            self._value = value
            self._args = None
            self._kwargs = None

        for ob in self.observers:
            ob.notify(self)

    def notify(self, pred_cell):
        if self._function is not None:
            self._value = self._function(*self._args, **self._kwargs)


    def get(self):
        return self._value



if __name__ == "__main__":
    a = Cell(3)
    b = Cell(4)
    c = Cell(lambda x, y: x.get()+y.get(), a, b)
    print c.get()
    b.set(8)
    print c.get()
