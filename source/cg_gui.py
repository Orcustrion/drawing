#!/usr/bin/env python
# -*- coding:utf-8 -*-

import math
from math import sqrt
import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import QRectF, center


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''
        self.status = ''
        
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None

        self.polygon_point=0
        self.curve_point=0

        self.edit=None
        self.core=None
        self.center=None
    
    # 线段
    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    
    # 多边形
    def start_draw_polygon(self, algorithm, item_id): 
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    
    # 椭圆
    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id

    # 曲线
    def start_draw_curve(self,algorithm,item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    
    # 编辑
    def start_translate(self):
        self.status = 'translate'
    def start_rotate(self):
        self.main_window.statusBar().showMessage('点击选择旋转中心')
        self.status = 'rotate'
    def start_scale(self):
        self.main_window.statusBar().showMessage('点击选择缩进中心')
        self.status = 'scale'
    def start_clip_cohen_sutherland(self):
        self.main_window.statusBar().showMessage('点击选择裁剪框')   
        self.status = 'clip_CS'
    def start_clip_liang_barsky_action(self):
        self.main_window.statusBar().showMessage('点击选择裁剪框')
        self.status = 'clip_LB'
    

             
    # 其他
    def finish_draw(self):
        self.temp_id = self.main_window.get_id()

    def end_draw_polygon(self):
        self.temp_item.p_list[-1]=self.temp_item.p_list[0]
        self.item_dict[self.temp_id] = self.temp_item
        self.list_widget.addItem(self.temp_id)
        self.polygon_point=0
        self.finish_draw()
    
    def end_draw_curve(self):
        self.item_dict[self.temp_id] = self.temp_item
        self.list_widget.addItem(self.temp_id)
        self.curve_point=0
        self.finish_draw()

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''
    
    def selection_changed(self, selected):
        if len(self.item_dict)>0 and selected !='':
            self.main_window.statusBar().showMessage('图元选择： %s' % selected)
            if self.selected_id != '':
                self.item_dict[self.selected_id].selected = False
                self.item_dict[self.selected_id].update()
            
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
            #self.status = ''
            self.updateScene([self.sceneRect()])
           

    def mousePressEvent(self, event: QMouseEvent) -> None:  # 鼠标点击
        pos = self.mapToScene(event.localPos().toPoint()) 
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        if self.status == 'polygon':
            if self.polygon_point==0:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm)
                self.polygon_point+=1
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x,y])
                self.polygon_point+=1
        if self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        if self.status == 'curve':
            if self.curve_point==0:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm)
                self.curve_point+=1
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x,y])
                self.curve_point+=1
        if self.status == 'translate' and self.selected_id !='':
            self.edit=[x,y]
        if self.status == 'rotate'and self.selected_id !='':
            if self.core==None:
                self.core=[x,y]
                self.item_dict['core']=MyItem('core','point',[[x,y]],'')
                self.scene().addItem(self.item_dict['core'])
                self.main_window.statusBar().showMessage('滑动确定旋转角度')
            else:
                self.edit=[x,y]
        if self.status == 'scale'and self.selected_id !='':
            if self.core==None:
                self.core=[x,y]
                self.item_dict['core']=MyItem('core','point',[[x,y]],'')
                self.scene().addItem(self.item_dict['core'])
                self.main_window.statusBar().showMessage('移动确定缩进程度')
            else:
                center_x,center_y=0,0
                for point in self.item_dict[self.selected_id].p_list:
                    center_x+=point[0]
                    center_y+=point[1]
                self.center=[int(center_x/len(self.item_dict[self.selected_id].p_list)),int(center_y/len(self.item_dict[self.selected_id].p_list))]
                self.edit=[x,y]
        if self.status == 'clip_CS' and self.selected_id !='':
            if self.item_dict[self.selected_id].item_type=='line':
                    self.item_dict['frame']=MyItem('frame','rectangle',[[x,y],[x,y]],'Cohen-Sutherland')
                    self.scene().addItem(self.item_dict['frame'])
        if self.status == 'clip_LB' and self.selected_id !='':
            if self.item_dict[self.selected_id].item_type=='line':
                    self.item_dict['frame']=MyItem('frame','rectangle',[[x,y],[x,y]],'Liang-Barsky')
                    self.scene().addItem(self.item_dict['frame'])

        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # 鼠标移动
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        if self.status == 'polygon':
            if self.polygon_point>0:
                if abs(x-self.temp_item.p_list[0][0])<=3 and abs(y-self.temp_item.p_list[0][1])<=3 and self.polygon_point>1:
                    self.end_draw_polygon()
                else:
                    self.temp_item.p_list[-1] = [x, y]
        if self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        if self.status == 'curve':
            self.temp_item.p_list[-1] = [x, y]
        if self.status == 'translate' and self.selected_id !='':
            if [x,y] != self.edit:
                dx,dy=x-self.edit[0],y-self.edit[1]
                self.item_dict[self.selected_id].p_list=alg.translate(self.item_dict[self.selected_id].p_list,dx,dy)
                self.edit=[x,y]
        if self.status == 'rotate' and self.selected_id !='' and self.edit!=None:        
            angle=self.cal_angle(self.edit,[x,y],self.core)
            if angle > 3:
                if self.item_dict[self.selected_id].item_type!= 'ellipse':
                    self.item_dict[self.selected_id].p_list=alg.rotate(self.item_dict[self.selected_id].p_list,self.core[0],self.core[1],angle)
                    self.edit=[x,y]
        if self.status == 'scale' and self.selected_id !='' and self.edit!=None:                   
            s=self.cal_ss(self.edit,[x,y])   
            self.item_dict[self.selected_id].p_list=alg.scale(self.item_dict[self.selected_id].p_list,self.core[0],self.core[1],s)
            self.edit=[x,y]
        if (self.status == 'clip_CS' or self.status == 'clip_LB')  and self.selected_id !='':
            if self.item_dict[self.selected_id].item_type=='line':
                self.item_dict['frame'].p_list[1]=[x,y]
        
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # 鼠标释放
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        if self.status == 'polygon':
            if len(self.temp_item.p_list)>=2 and self.polygon_point>0:
                self.polygon_point+=1
                temp=self.temp_item.p_list[-1]
                self.temp_item.p_list.append(temp)
        if self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        if self.status == 'curve':
            if len(self.temp_item.p_list)>=2 and self.curve_point>0:
                self.curve_point+=1
                temp=self.temp_item.p_list[-1]
                self.temp_item.p_list.append(temp)
        if self.status == 'translate' and self.selected_id !='':
            self.edit=None
        if self.status == 'rotate' and self.selected_id !='':
            self.edit=None
        if self.status == 'scale' and self.selected_id !='':
            self.edit=None
            self.center=None
        if (self.status == 'clip_CS' or self.status == 'clip_LB') and self.selected_id !='':
            self.item_dict[self.selected_id].p_list=alg.clip(
                    self.item_dict[self.selected_id].p_list,
                    self.item_dict['frame'].p_list[0][0],
                    self.item_dict['frame'].p_list[0][1],
                    self.item_dict['frame'].p_list[1][0],
                    self.item_dict['frame'].p_list[1][1],
                    self.item_dict['frame'].algorithm)
            if 'frame' in  self.item_dict: 
                self.main_window.scene.removeItem(self.item_dict['frame'])
                self.item_dict.pop('frame')   
            self.updateScene([self.sceneRect()])
        
        super().mouseReleaseEvent(event)
    
    def cal_angle(self,p1,p2,core):
        a=sqrt(pow((p1[0]-core[0]),2)+pow((p1[1]-core[1]),2))
        b=sqrt(pow((p2[0]-core[0]),2)+pow((p2[1]-core[1]),2))
        c=sqrt(pow((p1[0]-p2[0]),2)+pow((p1[1]-p2[1]),2))
        if a==0 or b==0 or c==0 :
            return 0
        return math.degrees(math.acos((c*c-a*a-b*b)/(-2*a*b))) 

    def cal_ss(self,p1,p2):

        # 计算两个向量夹角
        dis_1=pow((p1[0]-p2[0]),2)+pow((p1[1]-p2[1]),2)
        arr_1=[self.center[0]-self.core[0],self.center[1]-self.core[1]]
        arr_2=[p1[0]-p2[0],p1[1]-p2[1]]
        cos_theta=arr_1[0]*arr_2[0]+arr_1[1]*arr_2[1]

        if cos_theta < 0: # 放大
            return 2-math.exp(-dis_1/20)
        else:             # 缩小    
            return math.exp(-dis_1/20)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'rectangle':
            point_list=[self.p_list[0],self.p_list[1],[self.p_list[0][0],self.p_list[1][1]],[self.p_list[1][0],self.p_list[0][1]]]
            item_pixels=[]
            item_pixels.extend(alg.draw_line([point_list[0],point_list[2]], 'Bresenham'))
            item_pixels.extend(alg.draw_line([point_list[0],point_list[3]], 'Bresenham'))
            item_pixels.extend(alg.draw_line([point_list[1],point_list[2]], 'Bresenham'))
            item_pixels.extend(alg.draw_line([point_list[1],point_list[3]], 'Bresenham'))
            painter.setPen(QColor(0, 255, 255))
            for p in item_pixels:
                painter.drawPoint(*p) 
        elif self.item_type == 'point':
            mx,my=self.p_list[0][0],self.p_list[0][1]
            item_pixels = [[mx,my],[mx+1,my+1],[mx,my+1],[mx+1,my],[mx-1,my-1],[mx,my-1],[mx-1,my],[mx+1,my-1],[mx-1,my+1]]
            for p in item_pixels:
                painter.drawPoint(*p)
        elif self.item_type == 'polygon':
            item_pixels=[]
            for i in range(0,len(self.p_list)-1):
                item_pixels.extend(alg.draw_line([self.p_list[i],self.p_list[i+1]], self.algorithm))
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            indicate_pixels=[]
            for i in range(0,len(self.p_list)-1):
                indicate_pixels.extend(alg.draw_line([self.p_list[i],self.p_list[i+1]], 'Bresenham'))
            painter.setPen(QColor(0, 255, 255))
            for p in indicate_pixels:
                painter.drawPoint(*p) 
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            painter.setPen(QColor(0, 0, 0))
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'point': 
            mx,my=self.p_list[0][0],self.p_list[0][1]
            return QRectF(mx-3, my - 3, 4,4)
        elif self.item_type == 'rectangle':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon':
            first,second=[],[]
            for point in self.p_list:
                first.append(point[0])
                second.append(point[1]) 
            x = min(first)
            y = min(second)
            w = max(first) - x
            h = max(second) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'curve':
            first,second=[],[]
            np_list=alg.draw_curve(self.p_list, self.algorithm)
            for point in np_list:
                first.append(point[0])
                second.append(point[1]) 
            x = min(first)
            y = min(second)
            w = max(first) - x
            h = max(second) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)   
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()

        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        exit_act = file_menu.addAction('退出')

        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        end_draw_act=curve_menu.addAction('结束绘画')
        

        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        deselection_act=menubar.addAction('取消选择')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)

        reset_canvas_act.triggered.connect(self.reset_canvas)
        deselection_act.triggered.connect(self.de_selection)

        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_DDA_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)

        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)

        ellipse_act.triggered.connect(self.ellipse_action)

        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        end_draw_act.triggered.connect(self.end_draw_action)

        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        


        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def reset_canvas(self): # 重置画布  
        self.item_cnt = 0

        self.canvas_widget.selected_id = ''
        self.canvas_widget.status = ''
        self.canvas_widget.temp_algorithm = ''
        self.canvas_widget.temp_id = ''
        self.canvas_widget.temp_item = None
        self.canvas_widget.clear_selection()
        self.canvas_widget.item_dict={}

        self.scene.clear()
        self.list_widget.clear()

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.de_selection()
    
    def line_DDA_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.de_selection()
    
    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.de_selection()
    
    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.de_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.de_selection()
    
    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.de_selection()
    
    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier',self.get_id())
        self.statusBar().showMessage('Bezier算法绘制椭曲线')
        self.de_selection()

    def curve_b_spline_action(self):
        pass

    def translate_action(self):
        self.statusBar().showMessage('平移图像')
        if self.canvas_widget.selected_id !='':
            self.canvas_widget.start_translate()

    def rotate_action(self):
        if self.canvas_widget.selected_id !='':
            self.canvas_widget.start_rotate()
    
    def scale_action(self):
        if self.canvas_widget.selected_id !='':
            self.canvas_widget.start_scale()

    def clip_cohen_sutherland_action(self):
        if self.canvas_widget.selected_id !='':
            self.canvas_widget.start_clip_cohen_sutherland()
    
    def clip_liang_barsky_action(self):
        if self.canvas_widget.selected_id !='':
            self.canvas_widget.start_clip_liang_barsky_action()

    def end_draw_action(self):
        self.canvas_widget.end_draw_curve()
    
    def de_selection(self):  # 取消选择·改进版
        if self.canvas_widget.selected_id != '':
            self.list_widget.clearSelection()
            self.list_widget.setCurrentItem(None)
            self.canvas_widget.clear_selection()
            self.canvas_widget.core=None
            self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])
            if 'core' in  self.canvas_widget.item_dict: 
                self.scene.removeItem(self.canvas_widget.item_dict['core'])
                self.canvas_widget.item_dict.pop('core')
           
            
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
