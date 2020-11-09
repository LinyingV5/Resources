import tkinter
import tkinter.font as tkFont
import threading, time
from pynput import mouse, keyboard
import linecache
import random

#定义单词的类
class EnglishWord(object):
    
    #初始化单词的位置、速度和字体等
    def __init__(self, canvas, font, text, width, x_pos, y_pos, x_speed):
        self.canvas = canvas
        self.font = font
        self.text = text
        self.width = width
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_speed = x_speed
        
    #在画布中创建文字
    def create(self):
        self.word_text = self.canvas.create_text(self.x_pos, self.y_pos, text=self.text, font=self.font, fill='brown', anchor='nw')
    
    #单词进入屏幕
    def move(self):
        self.canvas.move(self.word_text, self.x_speed, 0)
        self.x_pos += self.x_speed
        
    #获得当前位置
    def get_x(self):
        return self.x_pos
    
    #将单词从画布中删除
    def remove(self):
        self.canvas.delete(self.word_text)

#屏保类实现 
class ScreenServer():
        
    def __init__(self, num_words, move_speed):
        self.words = list()
        self.num_words = num_words
        self.move_speed = move_speed
        
        self.ft = tkFont.Font(family='Helvetica', weight=tkFont.BOLD) #使用的字体
        self.text_list = linecache.getlines('words.txt') #获取文件中的单词
        
        self.wait_time = 0 #单词停止移动的世界
        self.waited = False #等待标记
        self.recreate = False #重建标记

    #开启屏保
    def screen_server_start(self):      
        #画布窗口
        self.canvas_window = tkinter.Tk()
        self.canvas_window.overrideredirect(1)
        self.canvas_window.attributes('-alpha', 0.5)
        #绑定监听事件
        self.canvas_window.bind('<Motion>', self.input_listener)
        self.canvas_window.bind('<Key>', self.input_listener)
        #创建画布
        self.width, self.height = self.canvas_window.winfo_screenwidth(), self.canvas_window.winfo_screenheight()
        self.canvas = tkinter.Canvas(self.canvas_window, width=self.width, height=self.height)
        self.canvas.pack()
        
        #依次创建单词
        self.create_words()
            
        self.run_screen_saver()
        
        self.canvas_window.mainloop()
    
    #绘制单词
    def create_words(self):
        for i in range(self.num_words):
            word_text = self.text_list[random.randint(1, 2090)]
            x_pos = self.width
            y_pos = self.height - self.height / self.num_words * i - 80
            word = EnglishWord(self.canvas, self.ft, word_text, self.width, x_pos, y_pos, self.move_speed)
            word.create()
            self.words.append(word)
        
    #单词的位置移动   
    def run_screen_saver(self):
        for i in range(self.num_words):
            if(time.time() - self.wait_time > 5):
                self.words[i].move()
            if self.words[i].get_x() < self.width / 2 and not self.waited: 
                self.waited = True
                self.wait_time = time.time()
            if self.words[i].get_x() < 0:
                self.words[i].remove()
                if i == self.num_words - 1:
                    self.recreate = True

        if(self.recreate):
            self.words.clear()
            self.create_words()
            self.recreate = False
            self.waited = False
        
        self.balls_drawing = self.canvas.after(30,self.run_screen_saver) 
        
    #监听输入
    def input_listener(self, event):
        self.canvas.after_cancel(self.balls_drawing)
        self.canvas_window.destroy()

#时间管理类        
class TimeManager():
    
    def __init__(self, setting_manager):   
        self.wait_time = setting_manager.get_wait_time()
        self.server_on = setting_manager.get_server_state()
        self.time_record = time.time()
        self.run_flag = False
        self.listener = mouse.Listener()

    def time_manager_start(self):
        while True:
            with mouse.Events() as mouse_events, keyboard.Events() as keyboard_events:
                mouse_event = mouse_events.get(1.0)
                keyboard_event = keyboard_events.get(1.0)
                if mouse_event is None and keyboard_event is None:
                    if time.time() - self.time_record > self.wait_time:
                        break
                else:
                    self.time_record = time.time()
                    if not self.server_on: break

#初始设置界面        
class SettingManager():
    
    def __init__(self):
        self.wait_time = 5 #屏保等待时间
        self.server_on = False #判断屏保程序是否开启
    
        self.setting_window = tkinter.Tk()
        #得到屏幕大小
        self.width, self.height = self.setting_window.winfo_screenwidth(), self.setting_window.winfo_screenheight()
        #初始窗口
        self.setting_window.title('屏保设置')
        self.setting_window.geometry('300x150+%d+%d' % (self.width/2-300, self.height/2-150))
        self.setting_window.resizable(0, 0)
        #提示文本
        lab = tkinter.Label(self.setting_window, text='设置屏保出现的时间')
        lab.pack()
        #屏保时间单选按钮
        self.selection_var = tkinter.IntVar()
        self.selection_var.set(1)
                
        r1 = tkinter.Radiobutton(self.setting_window, text='5秒', variable=self.selection_var, value=1, command=self.time_selection)
        r1.pack()
        r2 = tkinter.Radiobutton(self.setting_window, text='30秒', variable=self.selection_var, value=2, command=self.time_selection)
        r2.pack()
        r3 = tkinter.Radiobutton(self.setting_window, text='3分钟', variable=self.selection_var, value=3, command=self.time_selection)
        r3.pack()
        #启动按钮
        self.start_button = tkinter.Button(self.setting_window, text='开始', width=10, height=1, command=lambda:self.thread_it(self.button_onclick))
        self.start_button.pack()
        
        self.setting_window.mainloop()
    
    def server_start(self):
        while(1):
            time_manager = TimeManager(self)
            time_manager.time_manager_start()
            if not self.server_on:break
            screen_server = ScreenServer(6, -20)
            screen_server.screen_server_start()
            
    #另开一个线程实现
    def thread_it(self, func):
        t = threading.Thread(target=func)
        t.setDaemon(True)
        t.start()
        
    #时间选择监听事件
    def time_selection(self):
        if self.selection_var.get() == 1:
            self.wait_time = 5
        elif self.selection_var.get() == 2:
            self.wait_time = 30
        elif self.selection_var.get() == 3:
            self.wait_time = 180
            
    #开始按钮点击事件
    def button_onclick(self):
        #开始监听
        if self.server_on == False:
            self.server_on = True
            self.start_button['text'] = '关闭'
            self.start_button['bg'] = 'red'
            self.setting_window.iconify()
            self.server_start()
        else:
            self.server_on = False
            self.start_button['text'] = '开始'
            self.start_button['bg'] = 'white'
    
    #返回服务状态
    def get_server_state(self):
        return self.server_on
    
    #返回等待时间
    def get_wait_time(self):
        return self.wait_time
        
if __name__=='__main__':
    SettingManager()