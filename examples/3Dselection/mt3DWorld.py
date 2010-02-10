from pymt import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
# Change the following import to your own mt3DObject implementation
# IF you are declaring the __main__ here
from reactive3DObject import *

class MT3DWorld(MTWidget):
    def __init__(self, **kwargs):
    	super(MT3DWorld, self).__init__(**kwargs)
    	self.on_selection   = False
    	self._pick_size     = 2
    	self._pick_buffer   = glSelectBuffer(64)
        
        self.touch_position = {}
        self.rotation_matrix = None
        self.reset_rotation()
        self.touch1, self.touch2 = None, None
        self.zoom = 3.0
    	
    	# OBJ management
    	self.models = {}
    	self.count = 0
    
    def reset_rotation(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        self.rotation_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()
    
    def rotate_scene(self, x,y,z):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRotatef(z, 0,0,1)
        glRotatef(x, 0,1,0)
        glRotatef(y, 1,0,0)
        glMultMatrixf(self.rotation_matrix)
        self.rotation_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()
    
    def on_touch_down(self, touch):
    	self.do_pick(touch.x, touch.y)
        
        self.touch_position[touch.id] = (touch.x, touch.y)
        if len(self.touch_position) == 1:
            self.touch1 = touch.id
        elif len(self.touch_position) == 2:
            self.touch1, self.touch2 = self.touch_position.keys()
            v1 = Vector(*self.touch_position[self.touch1])
            v2 = Vector(*self.touch_position[self.touch2])
            self.scale_dist = v1.distance(v2)
    
    def on_touch_move(self, touch):
        self.selection_pos = touch.pos
        
        dx, dy, angle = 0,0,0
        #two touches:  scale and rotate around Z
        if  self.touch_position.has_key(self.touch1) and self.touch_position.has_key(self.touch2):
            v1 = Vector(*self.touch_position[self.touch1])
            v2 = Vector(*self.touch_position[self.touch2])
            
            #compute scale factor
            new_dist = v1.distance(v2)
            zoomfactor = new_dist/self.scale_dist
            self.zoom *= zoomfactor
            self.scale_dist = new_dist
            
            # compute rotation angle
            old_line = v1 - v2
            new_line = Vector(touch.x, touch.y) - v2
            if self.touch1 != touch.id: new_line = v1 - Vector(touch.x, touch.y)
            angle = -1.0 * old_line.angle(new_line)
        
        else: #only one touch:  rotate using trackball method
            dx = 200.0*(touch.x-self.touch_position[touch.id][0])/float(self.width)
            dy = 200.0*(touch.y-self.touch_position[touch.id][1])/float(self.height)
        
        #apply the transformations we just computed
        self.rotate_scene(dx,-dy, angle)
        self.touch_position[touch.id] = (touch.x, touch.y)
    
    def on_touch_up(self, touch):
        del self.touch_position[touch.id]
    
    def do_pick(self, x, y):
    	self.on_selection = True
    	self.pick_start(x, y)
    	self.draw()
    	self.pick_stop()
    	self.on_selection = False
    
    def pick_start(self, x, y):
        viewport = glGetIntegerv(GL_VIEWPORT)
        width, height = getWindow().size
        
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPickMatrix(x, y, self._pick_size, self._pick_size, viewport)
        # left, right, bottom, top, NEAR, FAR
        glFrustum(-width / 2, width / 2, -height / 2, height / 2, .1, 1000)
        glTranslatef(-x, -y, 0.)
        glScalef(5000, 5000, 1)
        glTranslatef(-width / 2, -height / 2, -500)
        glMatrixMode(GL_MODELVIEW)
    
    def pick_stop(self):
    	hits = glRenderMode(GL_RENDER)
    	self.process_hits(hits, self._pick_buffer)
    	
    	glMatrixMode(GL_PROJECTION)
    	glPopMatrix()
    	glMatrixMode(GL_MODELVIEW)
	
    def draw(self):
      
        glPushMatrix()
    	glMultMatrixf(self.rotation_matrix)
        # Centering and rotating the world
        glTranslate(self.width/2, self.height/2, 10)
        glScalef(15, 15, 15)
        glRotate(90.0, self.width/2, self.height/2, 0)
    	
        glScalef(self.zoom, self.zoom, self.zoom)
        # then we draw every object in all the registered scenes
    	for model_key in self.models.keys():
            for obj in self.models[model_key]:
                if self.on_selection:
                    glLoadName(obj.get_number())
                obj.draw()
        glPopMatrix()

    def register_objects(self, group, object_list):
    	self.models[group] = object_list
    
    def number(self):
    	current_count = self.count
    	self.count+=1
    	return current_count
    
    def process_hits(self, hits, buffer):
    	# nothing to process
    	if len(hits) == 0:
    		return
    	# get the nearest object number
    	latest = None
    	last_near = -1
    	
    	for hit in hits:
            if last_near == -1 or (hit.near < last_near):
                last_near = hit.near
                latest = hit.names[0]
    	
    	obj = self.detect_object(latest)
    	obj.touched()
    	# uncomment below to debug
    	#print 'HIT', obj.get_number(), 'near', last_near, 'was', latest
    
    def detect_object(self, number):
        # seek the object who owns 'number' as number on stack
        for key in self.models.keys():
            # get the last object added to the dictionary of models
            if self.models[key][-1].get_number() == number:
                return self.models[key][-1]
            elif self.models[key][-1].get_number() > number:
                # current key has the list where the object we are seeking lives
                for obj in self.models[key]:
                    if obj.get_number() == number:
                        return obj
			

# The following constitutes an example
if __name__ == '__main__':
    world = MT3DWorld(size=(800, 600))
    objects = OBJ("test_scene.obj").get_objects()
    list = []
    
    for index, obj in enumerate(objects):
        # Subclassing instance of an mt3DOBject.
        # Always remember to pass the world object this particular
        # scene object will be registered in as it'll be crucial for object identification by openGL
        
        # example: generating a color for each object
        rgb_color = (index*.3, index*.5, index*.1)

        threeDobj = Reactive3DObject(obj, world.number(), rgb=rgb_color)
        list.append(threeDobj)
        
    # register scene with a name and list of objects
    world.register_objects("monkey", list)
    runTouchApp(world)
