import sys, math, pygame, time
from operator import itemgetter
from Cube import *
from copy import copy, deepcopy # Cần sao chép trạng thái khối cho khối 3D

class GUI():

    def __init__(self, cube, width=800, height=600, threeD=True):
        self.cube = cube
        self.color_bank = [(255, 0, 0), (0, 255, 0), (255, 255, 255), (0, 0, 255), (255, 255, 0), (255, 165, 0)] #Màu sắc của mỗi khối: đỏ, vàng, xanh dương, trắng, xanh lá cây, cam
        self.background_color = (0,35,0)

        self.state_list = None # Lưu trữ danh sách đường dẫn AI đã lấy
        self.info_box_text = [[('Buoc di cua AI: ', (0,0,0))] , [('Phim tat: ', (0,0,0))]] # Mảng chứa văn bản được hiển thị ở cuối màn hình
        self.info_box_text[1].append(('A - Xoay tu dong, M - Xoay thu cong', (0,0,0)))

        pygame.init() # bắt đầu pygame
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        pygame.display.set_caption('CubeAI')

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

        self.frame_rate = 50 # Tốc độ khung hình của trò chơi
        pygame.time.Clock().tick(self.frame_rate) # Giới hạn tốc độ khung hình

        # 3D cài đặt
        self.autoRotate = False # Khối lập phương có nên tự động xoay không
        self.threeD = threeD # 3D or 2D
        self.threeDCube = ThreeD_Cube()
        self.mouse_center = None
        self.speed = 140 # Hạn chế ảnh hưởng của chuột đối với chuyển động của khối (cao hơn là chậm hơn)
        self.autorotate_speed = 0.8 # tốc độ mà khối sẽ tự động xoay (cao hơn là nhanh hơn)
        self.theta = (0,0)

    # Cập nhật và hiển thị GUI bằng đầu vào của người dùng, phải được gọi liên tục
    def update(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

            # Bàn phím điều khiển
            keys = pygame.key.get_pressed()
            if event.type == pygame.KEYDOWN:
                # điều khiển 3D
                # xoay tự động
                if keys[pygame.K_a]:
                    if self.threeD != None:
                        self.autoRotate = True
                # Xoay thủ công bằng chuột
                if keys[pygame.K_m]:
                    if self.threeD != None:
                        self.autoRotate = False
                # Chuyển chế độ xem giữa 2d và 3d
                if keys[pygame.K_v]:
                    if self.threeD:
                        self.threeD = False
                    else:
                        self.threeD = True

                # Phím mũi tên
                if keys[pygame.K_RIGHT]:
                    if self.state_list != None and self.state_num < len(self.state_list)-1:
                        self.state_num += 1
                        self.cube.state = self.state_list[self.state_num][1]
                        # Thay đổi văn bản thông tin cho trạng thái nếu đó là một nước đi hợp lệ
                        del self.info_box_text[0][1:]
                        path_str = ''
                        for i in range(1,self.state_num):
                            path_str += str(Cube.translateMove(self.state_list[i][0])) + ', '
                        self.info_box_text[0].append((path_str, (0,0,0)))
                        self.info_box_text[0].append((str(Cube.translateMove(self.state_list[self.state_num][0])), (0,0,255)))
                        path_str = ', '
                        for i in range(self.state_num+1,len(self.state_list)):
                            path_str += str(Cube.translateMove(self.state_list[i][0])) + ', '
                        self.info_box_text[0].append((path_str[:-2], (0,0,0)))
                if keys[pygame.K_LEFT]:
                    if self.state_list != None and self.state_num > 0:
                        self.state_num -= 1
                        self.cube.state = self.state_list[self.state_num][1]
                        # Thay đổi văn bản thông tin cho trạng thái nếu đó là một nước đi hợp lệ
                        del self.info_box_text[0][1:]
                        path_str = ''
                        for i in range(1,self.state_num):
                            path_str += str(Cube.translateMove(self.state_list[i][0])) + ', '
                        self.info_box_text[0].append((path_str, (0,0,0)))
                        path_str = ''
                        if self.state_num > 0:
                            self.info_box_text[0].append((str(Cube.translateMove(self.state_list[self.state_num][0])), (0,0,255)))
                            path_str = ', '
                        for i in range(self.state_num+1,len(self.state_list)):
                            path_str += str(Cube.translateMove(self.state_list[i][0])) + ', '
                        self.info_box_text[0].append((path_str[:-2], (0,0,0)))

                # Xuất sắc               

        # Kiểm tra xem có nhấp chuột để xoay khối 3D không
        if pygame.mouse.get_pressed()[0] and not self.autoRotate:
                if self.mouse_center == None:
                    self.mouse_center = pygame.mouse.get_pos()
                self.theta = (self.theta[0] + (pygame.mouse.get_pos()[0]-self.mouse_center[0])/(self.speed), self.theta[1] + (pygame.mouse.get_pos()[1]-self.mouse_center[1])/(self.speed))

        self.screen.fill(self.background_color) # rõ ràng màn hình
        # Kết xuất 3D
        if self.threeD:
            self.threeDCube.update(self.cube.state, self.color_bank)
            self.draw3DCube(self.threeDCube.vertices, self.threeDCube.faces, self.threeDCube.colors)
            self.renderText()
            pygame.display.update()
        # Kết xuất 2D
        else:
            self.draw2DCube()
            self.renderText()
            pygame.display.update()

        pygame.time.Clock().tick(self.frame_rate) # Giới hạn tốc độ khung hình

    # Vẽ khối lập phương 2D lên màn hình
    def draw2DCube(self):
        cube = self.cube.state
        #print(khối lập phương)
        # Thông số kích thước khối
        color_bank = [(255, 0, 0), (0, 255, 0), (255, 255, 255), (0, 0, 255), (255, 255, 0), (255, 165, 0)] #Màu sắc của mỗi khối: đỏ, vàng, xanh dương, trắng, xanh lá cây, cam
        offset = (200, 25)
        cubeletSize = 30
        gap = 2
        size = int(math.log(len(cube[0]), 2)) #Những gì demention được sử dụng
        faces = [(size*(cubeletSize+gap)+gap, size*(cubeletSize+gap)+gap),
                 (size*(cubeletSize+gap)+gap, 0),
                 (2*(size*(cubeletSize+gap)+gap), size*(cubeletSize+gap)+gap),
                 (size*(cubeletSize+gap)+gap, 2*(size*(cubeletSize+gap)+gap)),
                 (0, size*(cubeletSize+gap)+gap),
                 (size*(cubeletSize+gap)+gap, 3*(size*(cubeletSize+gap)+gap))] #[Color, offset] cho từng mặt; lập chỉ mục là [trước, lên, phải, xuống, trái, sau]

        for c in range(len(cube)):
            count = 0
            for i in range(1, size+1):
                for j in range(1, size+1):
                    f = faces[c]
                    pygame.draw.rect(self.screen, color_bank[cube[c][count]], [offset[0]+f[0]+j*(cubeletSize+gap), offset[1]+f[1]+i*(cubeletSize+gap), cubeletSize, cubeletSize])
                    count += 1

    # Vẽ khối 3D lên màn hình
    # đỉnh = đỉnh là kết quả của ThreeD_Cube
    # khuôn mặt = khuôn mặt là kết quả của ThreeD_Cube
    # colors = màu có được từ ThreeD_Cube
    def draw3DCube(self, vertices, faces, colors):
        # Nó sẽ giữ các đỉnh đã biến đổi.
        t = []

        for v in vertices:
            # Xoay điểm quanh trục X, sau đó quanh trục Y và cuối cùng quanh trục Z.
            #r = v.rotateX(self.angle).rotateY(self.angle).rotateZ(self.angle)
            r = v.rotateX(self.theta[1]).rotateY(self.theta[0])
            # Chuyển đổi điểm từ 3D sang 2D
            p = r.project(self.screen.get_width(), self.screen.get_height(), 256, 4)
           # Đưa điểm vào danh sách đỉnh đã biến đổi
            t.append(p)

       # Tính giá trị Z trung bình của mỗi mặt.
        avg_z = []
        i = 0
        for f in faces:
            z = (t[f[0]].z + t[f[1]].z + t[f[2]].z + t[f[3]].z) / 4.0
            avg_z.append([i,z])
            i = i + 1

       # Vẽ các mặt bằng thuật toán Painter:
        # Những khuôn mặt ở xa được vẽ trước những khuôn mặt ở gần hơn.
        for tmp in sorted(avg_z,key=itemgetter(1),reverse=True):
            face_index = tmp[0]
            f = faces[face_index]
            pointlist = [(t[f[0]].x, t[f[0]].y), (t[f[1]].x, t[f[1]].y),
                         (t[f[1]].x, t[f[1]].y), (t[f[2]].x, t[f[2]].y),
                         (t[f[2]].x, t[f[2]].y), (t[f[3]].x, t[f[3]].y),
                         (t[f[3]].x, t[f[3]].y), (t[f[0]].x, t[f[0]].y)]
            try:
                pygame.draw.polygon(self.screen, colors[face_index],pointlist)
            except:
                print(self.colors)
                print(face_index)
                print(faces)
                exit()
            #print(danh sách điểm)

        if self.autoRotate:
            self.theta = (self.theta[0]+self.autorotate_speed, self.theta[1]+self.autorotate_speed)

    def renderText(self):
        rect = pygame.Rect(0,pygame.display.get_surface().get_size()[1]-100,pygame.display.get_surface().get_size()[0],100)
        pygame.draw.rect(self.screen, (255,255,255), rect)

        lineSpacing = -2
        # lấy chiều cao của phông chữ
        fontHeight = self.font.size("Tg")[1]

        y = rect.top - fontHeight - lineSpacing

        for i in self.info_box_text:
            x = 0
            y += fontHeight + lineSpacing
            for j in i:
                text = j[0]
                color = j[1]
                while text:
                    i = 1
                   # xác định xem hàng văn bản có nằm ngoài khu vực của chúng tôi không
                    if y + fontHeight > rect.bottom:
                        break
                   # xác định chiều rộng tối đa của dòng
                    while self.font.size(text[:i])[0] + x < rect.width and i < len(text):
                        i += 1

                    # nếu chúng ta đã ngắt dòng văn bản, thì hãy điều chỉnh phần ngắt dòng cho từ cuối cùng
                    if i < len(text):
                        i = text.rfind(" ", 0, i) + 1

                    image = self.font.render(text[:i], False, color)

                    self.screen.blit(image, (rect.left+x, y))

                    x += self.font.size(text[:i])[0]

                    if x >= rect.width or i < len(text):
                        x = 0
                        y += fontHeight + lineSpacing

                    # xóa văn bản chúng tôi vừa xóa
                    text = text[i:]

    # Thực hiện di chuyển được yêu cầu đến khối lập phương và thêm di chuyển vào màn hình
    # di chuyển = một bộ chứa nước đi mong muốn (mặt, loại)   

   # Thực hiện một đường dẫn AI và cho phép người dùng dễ dàng đi qua đường dẫn này
    # đường dẫn = đường dẫn trả về từ thuật toán AI

    def moveList(self, path):
        self.cube.state = path[0][1]
        self.state_list = path
        self.state_num = 0
        path_str = ''
        for i in range(1, len(path)):
            path_str += str(Cube.translateMove(path[i][0])) + ', '

        self.info_box_text[0].append((path_str[:-2], (0,0,0)))

# Làm cho một điểm trong 3 chiều. Dùng để vẽ khối lập phương 3D
class Point3D:
    # Tạo điểm
    # x = 0 = dây x
    # y = 0 = dây y
    # z = 0 = dây z
    def __init__(self, x = 0, y = 0, z = 0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    # Xoay điểm quanh trục X theo góc đã cho theo độ.
    # angle = góc mà điểm sẽ được xoay
    def rotateX(self, angle):
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        y = self.y * cosa - self.z * sina
        z = self.y * sina + self.z * cosa
        return Point3D(self.x, y, z)

  # Xoay điểm quanh trục Y theo góc đã cho theo độ.
    # angle = góc mà điểm sẽ được xoay
    def rotateY(self, angle):
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        z = self.z * cosa - self.x * sina
        x = self.z * sina + self.x * cosa
        return Point3D(x, self.y, z)

   # Xoay điểm quanh trục Z theo góc đã cho theo độ.
    # angle = góc mà điểm sẽ được xoay
    def rotateZ(self, angle):
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        x = self.x * cosa - self.y * sina
        y = self.x * sina + self.y * cosa
        return Point3D(x, y, self.z)

  # Chuyển đổi điểm 3D này thành 2D bằng phép chiếu phối cảnh.
    # win_width = chiều rộng cửa sổ
    # win_height = chiều cao cửa sổ
    # fow = trường nhìn
    # viewer_khoảng cách = người xem cách bao xa
    def project(self, win_width, win_height, fov, viewer_distance):
        factor = fov / (viewer_distance + self.z)
        x = self.x * factor + win_width / 2
        y = -self.y * factor + win_height / 2
        return Point3D(x, y, self.z)


    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"

# Lớp tạo hình chữ nhật và di chuyển khối 3D
class ThreeD_Cube:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.colors = []

 # Phương thức lấy trạng thái hình khối và tô màu, đồng thời tạo ra tất cả 3DPoints cần thiết để vẽ chúng lên màn hình
    # cube = cube.state sẽ được hiển thị
    # color_bank = ngân hàng màu mong muốn cho mỗi khuôn mặt
    def update(self, cube, color_bank):
       # dọn dẹp khối lập phương cũ
        self.vertices = []
        self.faces = []
        self.colors = []
        face_transformations = [[('n',0)],[('x',90)],[('y',270)],[('x',270)],[('y',90)],[('y',180)]] # Trước, lên, phải, xuống, trái, sau
        # Cần dịch ngược trạng thái để nó được định hướng chính xác
        cube = deepcopy(cube)
        back = deepcopy(cube[5])
        for i in range(len(back)):
            cube[5][i] = back[len(back)-i-1]

        size = int(math.log(len(cube[0]), 2)) #Cái gì demention được sử dụng
        offset = 2/(size)/25 # Khoảng cách giữa các hình khối
        cube_size = (2 - offset*(size+1))/size

        # Thêm từng hình vuông vào khuôn mặt và màu sắc
        for c in range(len(cube)):
            tmp_vertices = []
            p = (-1,1+cube_size,-1) # Điểm ban đầu nơi chúng ta bắt đầu vẽ từng ô vuông từ
            count = 0
            for i in range(0, size):
                p = (-1, p[1]-offset-cube_size, p[2])

                for j in range(0, size):
                    start_index = len(self.vertices) + len(tmp_vertices)
                    tmp_vertices.append(Point3D(p[0],p[1],p[2]))
                    tmp_vertices.append(Point3D(p[0]+cube_size,p[1],p[2]))
                    tmp_vertices.append(Point3D(p[0]+cube_size,p[1]-cube_size,p[2]))
                    tmp_vertices.append(Point3D(p[0],p[1]-cube_size,p[2]))
                    self.faces.append((start_index,start_index+1,start_index+2,start_index+3)) # Giữ tất cả các hình chữ nhật

                    self.colors.append(color_bank[cube[c][count]]) # Giữ màu của hình chữ nhật ở cùng một chỉ mục trong các mặt

                    p = (p[0]+cube_size+offset, p[1], p[2]) # Cập nhật p
                    count += 1

            # Biến đổi về đúng vị trí
            for i in range(len(tmp_vertices)):
                for j in range(len(face_transformations[c])):
                    if face_transformations[c][j][0]== 'x':
                        self.vertices.append(tmp_vertices[i].rotateX(face_transformations[c][j][1]))
                    elif face_transformations[c][j][0] == 'y':
                        self.vertices.append(tmp_vertices[i].rotateY(face_transformations[c][j][1]))
                    elif face_transformations[c][j][0] == 'z':
                        self.vertices.append(tmp_vertices[i].rotateZ(face_transformations[c][j][1]))
                    else:
                        self.vertices.append(tmp_vertices[i])