from OpenGL.GL import *

class MT3DObject(object):

    def __init__(self, mesh, number, **kwargs):	
        kwargs.setdefault('visible', True)
        # volume
        self.wrapped_mesh = mesh
        self.visible = kwargs.get('visible')
        self.stack_number = number
    
    def draw(self):
        if self.visible:
            self.wrapped_mesh.draw()
            
    def touched(self):
        # to be implemented by YOU
        pass
    
    def set_visible(self, value):
        self.visible = value
        
    def get_number(self):
        return self.stack_number
		
        
