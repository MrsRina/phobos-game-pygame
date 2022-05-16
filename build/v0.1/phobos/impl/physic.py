from .lib import math, pygame;
from .    import api, util, universe;

class CollideInfo:
	def __init__(self):
		self.depth = 0;
		self.normal = 0;
		self.start = 0;
		self.end = 0;

	def set_info(self, d, n, s):
		self.depth = d;
		self.normal = n;
		self.start = start;
		self.end = s.add(n.scale(d));

	def oposite(self):
		self.normal = self.normal.scale(-1);
		n = self.start;
		self.start = self.end;
		self.end = n;

class Vec2:
	def __init__(self, x, y):
		self.x = x;
		self.y = y;

	def set(self, x, y):
		self.x = x;
		self.y = y;

	def length(self):
		return math.sqrt(self.x * self.x + self.y * self.y);

	def add(self, vec):
		return Vec2(vec.x + self.x, vec.y + self.y);

	def subtract(self, vec):
		return Vec2(self.x - vec.x, self.y - vec.y);

	def scale(self, n):
		return Vec2(self.x * n, self.y * n);

	def dot(self, vec):
		return (self.x * vec.x + self.y * vec.y);

	def cross(self, vec):
		return (self.x * vec.y - self.y * vec.x);

	def rotate(self, center, angle):
		x = self.x - center.x;
		y = self.y - center.y;

		matrix_rotation = [0, 0];
		matrix_rotation[0] = x * math.cos(angle) - y * math.sin(angle);
		matrix_rotation[1] = x * math.sin(angle) + y * math.cos(angle);

		matrix_rotation[0] += center.x;
		matrix_rotation[1] += center.y;

		return Vec2(matrix_rotation[0], matrix_rotation[1]);

	def normalize(self):
		length = self.length();

		if length > 0:
			length = 1 / length;

		return self.scale(length);

	def distance(self, vec):
		x = self.x - vec.x;
		y = self.y - vec.y;

		return math.sqrt(self.x * self.x + self.y * self.y);

class RigidShape:
	def __init__(self, center):
		self.center = center;
		self.angle = 0;
		self.gravity = False;
		self.type = "empty";

	def push(self, physic_manager):
		physic_manager.add(self);

	def collidewith(self, collider):
		return 0;

	def update(self):
		pass

class Rectangle(RigidShape):
	def __init__(self, center, w, h):
		super().__init__(center);

		self.type = "rectangle";
		self.gravity = 0;
		self.spd = 0;
		self.sp = None;
		self.bound_radius = math.sqrt(w * w + h * h) / 2;

		self.w = w;
		self.h = h;

		self.vertex = [0, 0, 0, 0];
		self.face_normal = [0, 0, 0, 0];

		self.vertex[0] = Vec2(center.x - w / 2, center.y - h / 2);
		self.vertex[1] = Vec2(center.x + w / 2, center.y - h / 2);
		self.vertex[2] = Vec2(center.x + w / 2, center.y + h / 2);
		self.vertex[3] = Vec2(center.x - w / 2, center.y + h / 2);

		self.face_normal[0] = self.vertex[1].subtract(self.vertex[2]);
		self.face_normal[0] = self.face_normal[0].normalize();
		self.face_normal[1] = self.vertex[2].subtract(self.vertex[3]);
		self.face_normal[1] = self.face_normal[1].normalize();
		self.face_normal[2] = self.vertex[3].subtract(self.vertex[0]);
		self.face_normal[2] = self.face_normal[2].normalize();
		self.face_normal[3] = self.vertex[0].subtract(self.vertex[1]);
		self.face_normal[3] = self.face_normal[3].normalize();

	def move(self, vec):
		for i in range(0, 4):
			self.vertex[i] = self.vertex[i].add(vec);

		self.center.add(vec);
		return self;

	def rotate(self, angle):
		self.angle += angle;

		for i in range(0, 4):
			self.vertex[i] = self.vertex[i].rotate(self.center, angle);

		self.face_normal[0] = self.vertex[1].subtract(self.vertex[2]);
		self.face_normal[0] = self.face_normal[0].normalize();
		self.face_normal[1] = self.vertex[2].subtract(self.vertex[3]);
		self.face_normal[1] = self.face_normal[1].normalize();
		self.face_normal[2] = self.vertex[3].subtract(self.vertex[0]);
		self.face_normal[2] = self.face_normal[2].normalize();
		self.face_normal[3] = self.vertex[0].subtract(self.vertex[1]);
		self.face_normal[3] = self.face_normal[3].normalize();

		return self;

	def collidewith(self, rect, collideinfo):
		status1 = 0;
		status2 = 0;

		info1 = CollideInfo();
		info2 = CollideInfo();

		status1 = self.find_axis_least_penetration(rect, info1);

		if status1:
			status2 = rect.find_axis_least_penetration(self, info2);

			if status2:
				if (info1.depth < info2.depth):
					depth_vec = info1.normal.scale(info1.depth);
					collideinfo.set_info(info1.depth, info1.normal, info1.start.subtract(depth_vec));
				else:
					collideinfo.set_info(info2.depth, info2.normal.scale(-1), info2.start);

		return status1 and status2;


	def find_support_point(self, the_dir, ptonedge):
		toedge = 0;
		projection = 0;

		self.spd = -9999999;
		self.sp = None;

		for i in range(0, len(self.vertex)):
			toedge = self.vertex[i].subtract(ptonedge);
			projection = toedge.dot(the_dir);

			if (projection > 0) and (projection > self.spd):
				self.sp = self.vertex[i];
				self.spd = projection;

	def find_axis_least_penetration(self, rect, collideinfo):
		n = 0;
		sp = 0;
		best_dist = 999999;
		best_index = -1;
		has_sp = 1;

		i = 0;

		while (has_sp and (i < len(self.face_normal))):
			n = self.face_normal[i];
			the_dir = self.vertex[i];
			ptonedge = self.vertex[i];

			rect.find_support_point(the_dir, ptonedge);
			has_sp = (self.sp != None);

			if (has_sp and self.spd < best_dist):
				best_dist = self.spd;
				best_index = i;
				spd = self.spd;

			i += 1;

		if has_sp and best_dist != -1:
			bestVec = self.face_normal[best_index].scale(best_dist);
			collideinfo.set_info(best_dist, self.face_normal[best_index], bestVec.add(spd));

		return has_sp;

class Circle(RigidShape):
	def __init__(self, center, radius):
		super().__init__(center);

		self.type = "circle";
		self.gravity = 0;

		self.radius = radius;
		self.startpoint = Vec2(center.x, center.y - radius);

	def move(self, vec):
		self.startpoint = self.startpoint.add(vec);
		self.center = self.center.add(vec);
		return self;

	def collidewith(self, collider, collideinfo):
		diff = collider.center.subtract(self.center);
		rsum = collider.radius + self.radius;
		dist = diff.length();

		if (dist > math.sqrt(rsum * rsum)):
			return False;

		if (dist != 0):
			ndiff = diff.scale(-1).normalize();
			r2 = ndiff.scale(collider.radius);

			collideinfo.set_info(rsum - dist, diff.normalize(), collider.add(r2));
		else:
			if (self.radius > collider.radius):
				collideinfo.set_info(rsum, Vec2(0, -1), self.center.add(Vec2(0, self.radius)));
			else:
				collideinfo.set_info(rsum, Vec2(0, -1), self.center.add(Vec2(0, collider.radius)));

		return False;

	def rotate(self, angle):
		self.angle += angle;
		self.startpoint = self.startpoint.rotate(self.center, self.angle);
		return self;

class Physic:
	def __init__(self, master):
		self.gravity = 0.9;
		self.shape_list = [];
		self.master = master;
		self.offset_ticks = 0;
		self.collideinfo = CollideInfo();

	def add(self, rigidshape):
		self.shape_list.append(rigidshape);

	def apply_rect_clamp_collision(self, x, y, w, h, rect, diff):
		pass

	def update(self):
		for segment_shapes_1 in self.shape_list:
			segment_shapes_1.update();

			for segment_shapes_2 in self.shape_list:
				if segment_shapes_2 == segment_shapes_1:
					continue;

				if segment_shapes_1.collidewith(segment_shapes_2, self.collideinfo):
					print("collided");

	def render(self, partial_ticks):
		key = pygame.key.get_pressed();

		if key[pygame.K_SPACE] and self.offset_ticks > 80:
			rect = Rectangle(Vec2(self.master.player.rect.x, self.master.player.rect.y), 200, 200);
			rect.push(self);
			self.offset_ticks = 0;

		self.offset_ticks += 1;

		for shapes in self.shape_list:
			if shapes.type == "rectangle":
				api.OpenGL.fill_rectangle(shapes, self.master.camera, (255, 255, 255, 200));
			elif shapes.type == "circle":
				api.OpenGL.fill_arc(shapes, self.master.camera, (255, 255, 255, 200));

	def check(self, tile):
		return tile.get_name() != "player_spawn" and tile.get_name() != "mob_spawn" and tile.get_name() != "passive_spawn";