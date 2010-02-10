from mt3DObject import *

class Reactive3DObject(MT3DObject):
    
    def __init__(self, mesh, number, **kwargs):
        MT3DObject.__init__(self,mesh, number, **kwargs)
        self.active = kwargs.get('active')
        kwargs.setdefault('active', False)
        kwargs.setdefault('rgb', (1.0, 1.0, 1.0))
        # Can set a color for this object 
        self.rgb = kwargs.get('rgb')

    def draw(self):
        if self.active:
            prev_color = glGetFloatv(GL_CURRENT_COLOR)
            glColor(self.rgb[0], self.rgb[1], self.rgb[2])
        MT3DObject.draw(self)
        if self.active:
            glColor(prev_color[0], prev_color[1], prev_color[2], prev_color[3])
    # Define here what to do when your object is touched        
    def touched(self):
        self.active = not self.active
