#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
               x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
               result.append((x, int(y0 + k * (x - x0))))       
    elif algorithm == 'DDA':   # DDA算法 
        if x0 == x1: # 垂直x轴
            if y0 > y1:
                y0,y1=y1,y0
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            k = (y1 - y0) / (x1 - x0)
            if abs(k)<= 1: # x增加1 y增加k
                step=abs(x1-x0)
                if x0>x1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                fx=float(x0)
                fy=float(y0)
                for i in range(0,step+1):
                    result.append((int(fx),round(fy)))
                    fx=fx+1
                    fy=fy+k
            elif abs(k)> 1: # y增加1 x增加k
                step=abs(y1-y0)
                if y0>y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                fx=float(x0)
                fy=float(y0)
                for i in range(0,step+1):
                    result.append((round(fx),int(fy)))
                    fy=fy+1
                    fx=fx+1/k
    
    elif algorithm == 'Bresenham':
        if x0 == x1: # 垂直x轴
            if y0 > y1:
                y0,y1=y1,y0
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            k = (y1 - y0) / (x1 - x0)
            if abs(k) <= 1: # 以x为基准判断
                step=abs(x1-x0)
                if ((k>0) and (x0>x1)) or ((k<0) and (x0<x1)):
                    x0, y0, x1, y1 = x1, y1, x0, y0
                cal_p=2*abs(y1-y0)-abs(x1-x0)
                fx,fy=x0,y0
                result.append((fx,fy))
                for i in range(0,step):
                    if k>0 or ((k==0) and x0<x1):
                       fx=fx+1
                    else:
                       fx=fx-1
                    if cal_p<=0:
                        cal_p=cal_p+2*abs(y1-y0)
                    else:
                        fy=fy+1
                        cal_p=cal_p+2*abs(y1-y0)-2*abs(x1-x0)
                    result.append((fx,fy))
            else:
                step=abs(y1-y0)
                cal_p=2*abs(x1-x0)-abs(y1-y0)
                if ((k>0) and (y0>y1)) or ((k<0) and (y0<y1)):
                    x0, y0, x1, y1 = x1, y1, x0, y0
                fx,fy=x0,y0
                result.append((fx,fy))
                for i in range(0,step):
                    if k>0:
                       fy=fy+1
                    else:
                       fy=fy-1
                    if cal_p<=0:
                        cal_p=cal_p+2*abs(x1-x0)
                    else:
                        fx=fx+1
                        cal_p=cal_p+2*abs(x1-x0)-2*abs(y1-y0)
                    result.append((fx,fy))
    
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """

    # standby
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if x0>x1:
        x0,x1=x1,x0
        y0,y1=y1,y0
    result = []
    final=[]

    rx=abs(float((x1-x0)/2))
    ry=abs(float((y1-y0)/2))
    a,b=(x0+x1)/2,(y0+y1)/2

    if x0==x1 and y0==y1:
        final.append([x0,y0])
    else:
        # phase 1
        p1=ry*ry-rx*rx*ry+rx*rx/4  # 区域1决策初值
        fx,fy=0,int(ry)
        result.append([fx,fy])
        result.append([fx,-fy])
        while ry*ry*fx<rx*rx*fy:
            fx=fx+1
            if p1<0:
                p1=p1+2*ry*ry*fx+ry*ry
            else:
                fy=fy-1
                p1=p1+2*ry*ry*fx+ry*ry-2*rx*rx*fy

            result.append([fx,fy])
            result.append([-fx,fy])
            result.append([fx,-fy])
            result.append([-fx,-fy])
        
        # phase 2
        p2=rx*rx-rx*ry*ry+ry*ry/4   # 区域2决策初值
        fx,fy=int(rx),0
        result.append([fx,fy])
        result.append([-fx,fy])
        while ry*ry*fx>=rx*rx*fy:
            fy=fy+1
            if p2<0:
                p2=p2+2*rx*rx*fy+rx*rx
            else:
                fx=fx-1
                p2=p2+2*rx*rx*fy+rx*rx-2*ry*ry*fx

            result.append([fx,fy])
            result.append([-fx,fy])
            result.append([fx,-fy])
            result.append([-fx,-fy])

        # end phase
        for point in result:
            final.append([int(point[0]+a),int(point[1]+b)])

    return final

def draw_curve(p_list, algorithm):
    """绘制曲线
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    
    result=[]
    x=[]
    y=[]
    n=len(p_list)-1 
    for point in p_list:
        x.append(point[0])
        y.append(point[1])
    #if algorithm=='Bezier': # Bezier算法 
    point_num=5000 # 30000 points 
    coe=[1,1]
    for i in range(n-1):
        coe=de_Casteljau_optimize(coe)
    for i in range(0,point_num):
        u=float(i/point_num)
        res_x,res_y=0,0
        for p in range(n+1):
            res_x+=coe[p]*pow(u,p)*pow((1-u),n-p)*x[p]
            res_y+=coe[p]*pow(u,p)*pow((1-u),n-p)*y[p]

        result.append([int(res_x+0.5),int(res_y+0.5)])
    
    '''
    elif algorithm=='B-spline': # 三次均匀B样条
        k=3 # 三次
        node=[i/(n+k+1) for i in range(0,n+k+2)] # 节点矢量
        point_num=1000*(n+k+1)
        j=3
        counter=0
        for t in range(int(node[k]*point_num),int(node[n+1]*point_num)+1):
        
            u=float(t/point_num)
            x,y=deBoor_Cox(u,j,3,node,p_list)
            counter+=1
            if counter==1000:
                counter=0
                j+=1
            result.append([int(x+0.5),int(y+0.5)])
    '''
    return result

def de_Casteljau_optimize(coe):
    res=[]
    for i in range(len(coe)):
        if i==0:
            res.append(1)
        else:
            res.append(coe[i]+coe[i-1])
    res.append(1)
    return res

def deBoor_Cox(u,i,r,node,p_list):
    if r==0:
        return p_list[i][0],p_list[i][1]
    else:
        l1=node[i+3-r]-node[i]
        l2=u-node[i]
        if l1==0 :  
            l1=1
        u1=l2/l1
        x=u1*deBoor_Cox(u,i,r-1,node,p_list)[0]+(1-u1)*deBoor_Cox(u,i-1,r-1,node,p_list)[0]
        y=u1*deBoor_Cox(u,i,r-1,node,p_list)[1]+(1-u1)*deBoor_Cox(u,i-1,r-1,node,p_list)[1]
        return x,y





def translate(p_list, dx, dy):
    """平移变换
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result=[]
    for point in p_list:
        result.append([point[0]+dx,point[1]+dy])
    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result=[]
    r_sin=math.sin(r*(math.pi)/180)
    r_cos=math.cos(r*(math.pi)/180)
    for point in p_list:
        fx=x+(point[0]-x)*r_cos-(point[1]-y)*r_sin
        fy=y+(point[0]-x)*r_sin+(point[1]-y)*r_cos
        result.append([round(fx),round(fy)])
    return result

def scale(p_list, x, y, s):
    """缩放变换
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result=[]
    for point in p_list:
        fx=point[0]*s+x*(1-s)
        fy=point[1]*s+y*(1-s)
        result.append([round(fx),round(fy)])
    return result

def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪
    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """

    result=[]
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if x0==x1:    # 线段垂直x轴
        if x0>x_min and x0<x_max:
            if y0>y1:
                y1,y0=y0,y1
            result.append([x0,min(y1,y_max)])
            result.append([x0,max(y0,y_min)])
        else:
            result=[[0,0],[0,0]] 
    elif y0==y1:  # 线段平行x轴
        if y0>y_min and y0<y_max:
            if x0>x1:
                x1,x0=x0,x1
            result.append([min(x1,x_max),y0])
            result.append([max(x0,x_min),y0])
        else:
            result=[[0,0],[0,0]] 
    else:
        #  1 left  2 right 3 below 4 top
        k=float((y1-y0)/(x1-x0)) # 斜率
        Q = [x0-x1, x1-x0, y0-y1, y1-y0] 
        D0 = [x0-x_min, x_max-x0, y_max-y0, y0-y_min]
        D1 = [x1-x_min, x_max-x1, y_max-y1, y1-y_min]

        if algorithm == 'Cohen-Sutherland':
            s1, s2=0, 0
            for i in range(4):
                if D0[i]<0:
                    s1+=pow(2,i)
                if D1[i]<0:
                    s2+=pow(2,i)
    
            if s1==0 and s2==0 : # 完全可见
                result=[[x0,y0],[x1,y1]] 
            elif s1 & s2 !=0: # 完全不可见
                result=[[0,0],[0,0]] 
            else: # s1、s2不完全为0
                if (s1 & 1) !=0:
                    y0 = int(y0 + ((x_min-x0) * k)+0.5)
                    x0 = x_min
                if (s1 & 2) !=0:
                    y0 = int(y0 + ((x_max-x0) * k)+0.5)
                    x0 = x_max
                if (s1 & 4) !=0:
                    if y0>y_max:
                        x0 = int(x0 + ((y_max-y0) / k)+0.5)
                        y0 = y_max
                if (s1 & 8) !=0:
                    if y0<y_min:
                        x0 = int(x0 + ((y_min-y0) / k)+0.5)
                        y0 = y_min
                
                if (s2 & 1) !=0:
                    y1 = int(y1 + ((x_min-x1) * k)+0.5)
                    x1 = x_min
                if (s2 & 2) !=0:
                    y1 = int(y1 + ((x_max-x1) * k)+0.5)
                    x1 = x_max
                if (s2 & 4) !=0:
                    if y1>y_max:
                        x1 = int(x1 + ((y_max-y1) / k)+0.5)
                        y1 = y_max
                if (s2 & 8) !=0:
                    if y1<y_min:
                        x1 = int(x1 + ((y_min-y1) / k)+0.5)
                        y1 = y_min
                result=[[x0,y0],[x1,y1]]
            return result

        elif algorithm == 'Liang-Barsky' :  
            D2 = [x0-x_min, x_max-x0,  y0-y_min,y_max-y0]
            u1, u2 = 0, 1
            for i in range(4):
                if Q[i] < 0:
                    u1 = max(u1, D2[i]/Q[i])
                elif Q[i] > 0:
                    u2 = min(u2, D2[i]/Q[i])
                if u1 > u2:
                    result = [[0,0], [0,0]]
            
                    return result
                
            res_x0 = int(x0 + u1*(x1-x0) + 0.5)
            res_y0 = int(y0 + u1*(y1-y0) + 0.5)           
            res_x1 = int(x0 + u2*(x1-x0) + 0.5)
            res_y1 = int(y0 + u2*(y1-y0) + 0.5)
            result = [[res_x0, res_y0], [res_x1, res_y1]]
    
            return result
    return result


