from mt3DObject import *
from pymt import *

class Reactive3DObject(MT3DObject):
    
    def __init__(self, mesh, number, **kwargs):
        MT3DObject.__init__(self,mesh, number, **kwargs)
        kwargs.setdefault('active', False)
        kwargs.setdefault('rgb', (1.0, 1.0, 1.0))

        self.active = kwargs.get('active')
        # Can set a color for this object 
        self.rgb = kwargs.get('rgb')

    def draw(self):
        if self.active:
            with gx_color(*self.rgb):
                MT3DObject.draw(self)
        else:
            with gx_color(1,0,0,0.5):
                MT3DObject.draw(self)
    # Define here what to do when your object is touched        
    def touched(self):
        self.active = not self.active
