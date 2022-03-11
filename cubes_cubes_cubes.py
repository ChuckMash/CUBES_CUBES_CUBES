import cv2
import numpy as np
import time
import random



class cube:
  def __init__(self):
    self.verts = [[-1,-1,-1,1],[1,-1,-1,1],[-1,1,-1,1],[1,1,-1,1],[-1,-1,1,1],[1,-1,1,1],[-1,1,1,1],[1,1,1,1]]
    self.lines = []
    self.lines.extend([[0,2],[1,3],[4,6],[5,7]]) # sides
    self.lines.extend([[0,1],[0,4],[1,5],[4,5]]) # bottoms
    self.lines.extend([[2,3],[2,6],[3,7],[6,7]]) # tops





class renderer:
  def __init__(self, shape, rotation=[0,0,0], delta=[0,0,0], color=(255,255,255), zoom=0.1, thickness=2):
    self.width = 640
    self.height = 480

    self.Gx = 0
    self.Gy = 0
    self.Gz = 0

    self.Cx = 0
    self.Cy = 0
    self.Cz = 5

    self.skew = 0

    self.shape     = shape
    self.rotation  = rotation[:]
    self.delta     = delta[:]
    self.color     = color
    self.zoom      = zoom
    self.thickness = thickness
    self.offsetX   = self.width / 2
    self.offsetY   = self.height / 2
    self.Px        = self.width / 10000
    self.Py        = self.height / 10000

    if self.color == "random":
      self.color = self.random_color()



  def random_color(self,r=[0,255], g=[0,255], b=[0,255]):
    r=random.randint(r[0],r[1])
    g=random.randint(g[0],g[1])
    b=random.randint(b[0],b[1])
    return [r,g,b]



  def blank_image(self):
    return 0 * np.ones((self.height, self.width, 3), dtype='uint8')



  def apply_rotation(self):
    self.rotation[0] += self.delta[0]
    self.rotation[1] += self.delta[1]
    self.rotation[2] += self.delta[2]



  def get(self):
    # I do not have the faintest idea of how this functions
    offset = np.array([[1, 0, 0, self.offsetX], [0, -1, 0, self.offsetY], [0, 0, 1, 0], [0, 0, 0, 1]])
    P = np.array([[(self.zoom * self.width) / (2 * self.Px), self.skew, 0, 0], [0, (self.zoom * self.height) / (2 * self.Py), 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
    C = np.array([[1, 0, 0, -self.Cx], [0, 1, 0, -self.Cy], [0, 0, 1, -self.Cz], [0, 0, 0, 1]])
    Rx = np.array([[1, 0, 0, 0], [0, np.cos(self.rotation[0]), - np.sin(self.rotation[0]), 0], [0, np.sin(self.rotation[0]), np.cos(self.rotation[0]), 0],[0, 0, 0, 1]])
    Ry = np.array([[np.cos(self.rotation[1]), 0, np.sin(self.rotation[1]), 0], [0, 1, 0, 0], [- np.sin(self.rotation[1]), 0, np.cos(self.rotation[1]), 0], [0, 0, 0, 1]])
    Rz = np.array([[np.cos(self.rotation[2]), - np.sin(self.rotation[2]), 0, 0],[np.sin(self.rotation[2]), np.cos(self.rotation[2]), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    G = np.array([[1, 0, 0, -self.Gx], [0, 1, 0, -self.Gy], [0, 0, 1, -self.Gz], [0, 0, 0, 1]])
    pov = [0] * len(self.shape.verts)

    for i in range(len(self.shape.verts)):
        pov[i] = np.matmul(G,  np.array(self.shape.verts[i]))
        pov[i] = np.matmul(Rz, pov[i])
        pov[i] = np.matmul(Ry, pov[i])
        pov[i] = np.matmul(Rx, pov[i])
        pov[i] = np.matmul(C,  pov[i])
        pov[i] = np.matmul(P,  pov[i])
        N = np.array([[1 / pov[i][2], 0, 0, 0], [0, 1 / pov[i][2], 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        pov[i] = np.matmul(N, pov[i])
        pov[i] = np.matmul(offset, pov[i])

    image = self.blank_image()

    for line in self.shape.lines:
        cv2.line(image, (int(pov[line[0]][0]), int(pov[line[0]][1])), (int(pov[line[1]][0]), int(pov[line[1]][1])), color=self.color, thickness=self.thickness)

    self.apply_rotation()

    return image





if __name__ == "__main__":
  domains=[]

  for i in range(1,6):
    zoom = i/40
    dx = random.uniform(-0.01, 0.01)
    dy = random.uniform(-0.01, 0.01)
    domains.append(renderer(shape=cube(), delta=[dx, dy, 0], color="random", zoom=zoom))

  while True:
    image = domains[0].get()
    for domain in domains[1:]:
      image = cv2.add(image, domain.get())

    cv2.imshow('CUBES CUBES CUBES', image)

    if cv2.waitKey(1) == 27: # esc
      break

  cv2.destroyAllWindows()
