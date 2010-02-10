from mt3DObject import *

class Reactive3DObject(MT3DObject):

	def __init__(self, mesh, number, **kwargs):
		super(Reactive3DObject, self).__init__(mesh, number, **kwargs)
		self.active = kwargs.get('active')
		kwargs.setdefault('active', False)
		
	def draw(self):
		if self.active:
			prev_color = glGetFloatv(GL_CURRENT_COLOR)
			glColor(1.0,1.0,1.0)
		super(Reactive3DObject, self).draw()
		if self.active:
			glColor(prev_color[0], prev_color[1], prev_color[2], prev_color[3])
	
	def touched(self):
		self.active = not self.active
