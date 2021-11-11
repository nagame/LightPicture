class FancyVertex(type):
    def __new__(cls, what, bases=None, dict=None):
        print(dict)
        if 'get_blog' in dict:
            print('Great you have get_blog')
        else:
            raise Exception('get_blog missing')

        new_dict = {}
        for key, val in dict.items():
            new_dict[key] = val
        new_dict['meta_say'] = lambda s: print('metasay')

        return type.__new__(cls, what, bases, new_dict)


class MyVertex(metaclass=FancyVertex):
    def get_blog(self):
        print('get_blog is there.')
    pass

v2 = MyVertex()
v2.get_blog()
v2.meta_say()



def f(self, key=None):
    print('I am f')

MyVertes = type('MyVertex',
             (),
             {'__init__': Coordinate.__init__,
             'f': f}
            )

v2.get_blog()
v2.meta_say()