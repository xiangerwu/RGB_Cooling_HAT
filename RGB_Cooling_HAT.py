#========================
#       Library
#========================
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_GPIO.I2C as I2C
import time
import os
import smbus
import Adafruit_SSD1306
import subprocess

# 備註:
# HAT 是 FAN HAT， OLED 是 OLED  兩個是分開的

# I2C 匯流排
bus = smbus.SMBus(1)
# RST
RST = None     # on the PiOLED this pin isnt used
#========================
#       Class
#========================
# HAT 設定
class HAT_Set:
    
    # HAT 套件初始化
    def __init__(self):
        self.addr       = 0x0d # 本身位址
        self.rgb        = 0x00 # RGB 位址
        self.rgb_effect = 0x04 # RGB 特效
        self.rgb_speed  = 0x05 # RGB 速度
        self.rgb_color  = 0x06 # RGB 顏色 
        self.fan        = 0x08 # 風扇位址
        self.fan_state = 0 # 控制風扇用變數
    
    # 控制風扇速度 (0~9)
    def SetFanSpeed(self,speed):
        # 因為我的套件好像接觸不良，有時候會跳錯誤中斷程式
        # 所以用 try&catch 來避免程式中斷
        try:
            bus.write_byte_data(self.addr, self.fan, speed&0xff)  
        except Exception as e:
            print("[I/O Error]")  
        
    
    # 判斷溫度控制轉速
    def TempCtrlSpeed(self,Temp):
        # FAN_Speed
        if( Temp <= 43 ):            
            self.SetFanSpeed(0)
            self.fan_state = 0
            # print(f"轉速0,state:'{self.fan_state}'")
        elif( Temp <= 48 and Temp > 43 and self.fan_state != 1):
            self.SetFanSpeed(1)
            self.fan_state = 1
            print(f"溫度:'{Temp}',轉速1,state:'{self.fan_state}'")
        elif( Temp <= 50 and Temp > 48 and self.fan_state != 2):
            self.SetFanSpeed(3)
            self.fan_state = 2
            print(f"溫度:'{Temp}',轉速3,state:'{self.fan_state}'")
        elif( Temp <= 53 and Temp > 50 and self.fan_state != 3):
            self.SetFanSpeed(5)
            self.fan_state = 3
            print(f"溫度:'{Temp}',轉速5,state:'{self.fan_state}'")
        elif( Temp <= 58 and Temp > 53 and self.fan_state != 4):
            self.SetFanSpeed(7)
            self.fan_state = 4
            print(f"溫度:'{Temp}',轉速7,state:'{self.fan_state}'")
        elif( Temp > 60 and Temp > 58 and self.fan_state != 5):
            self.SetFanSpeed(9)
            self.fan_state = 5
            print(f"溫度:'{Temp}',轉速9,state:'{self.fan_state}'")        
    
    # 控制 RGB 特效 (0~4)
    def SetRGBEffect(self,effect):
        if effect >= 0 and effect <= 4:
            bus.write_byte_data(self.addr, self.rgb_effect, effect&0xff)
    
    # 控制 RGB 顏色 (0~6)
    def SetRGBColor(self,color):        
        # 因為我的套件好像接觸不良，有時候會跳錯誤中斷程式
        # 所以用 try&catch 來避免程式中斷
        try:
             if color >= 0 and color <= 6:
                bus.write_byte_data(self.addr, self.rgb_color, color&0xff)   
        except Exception as e:
            print("[I/O Error]")  
    
    # 控制 RGB 速度(1~3)
    def SetRGBSpeed(self,speed):
        if speed >= 1 and speed <= 3:
            bus.write_byte_data(self.addr, self.rgb_speed, speed&0xff)

# OLED 設定
class OLED_Set:
    
    # OLED 初始化
    def __init__(self):
        # Adafruit_SSD1306 函式庫設定
        # 128x32 display with hardware I2C:
        self.display = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
        # 
        self.cpu_count = 0 # CPU 計數用
        self.progress_bar = 0 # 顯示進度 變數
        # 取得寬高
        self.width = self.display.width
        self.height = self.display.height
        # 創造用於繪圖的空白圖像，確定創造的圖像模式是單色 '1'
        self.image = Image.new('1', (self.width, self.height)) 
        # 創造 draw 物件用於 畫圖
        self.draw = ImageDraw.Draw(self.image)        
        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        self.padding = -2
        self.top = self.padding
        self.bottom = self.height-self.padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self.x = 0
        # Load default font.
        self.font = ImageFont.load_default()
        # 
        self.Temp = 0
    
    # display 的初始化
    def Adafruit_SSD1306_Init(self):
        # Initialize library.
        self.display.begin()
        # Clear display.
        self.display.clear()
        # disp.scroll_right();
        self.display.display()
    
    # 取得 CPU 負載
    def GetCPULoadRate(self):
        f1 = os.popen("cat /proc/stat", 'r')
        stat1 = f1.readline()
        count = 10
        data_1 = []
        for i  in range (count):
            data_1.append(int(stat1.split(' ')[i+2]))
        total_1 = data_1[0]+data_1[1]+data_1[2]+data_1[3]+data_1[4]+data_1[5]+data_1[6]+data_1[7]+data_1[8]+data_1[9]
        idle_1 = data_1[3]
        time.sleep(.5)
        f2 = os.popen("cat /proc/stat", 'r')
        stat2 = f2.readline()
        data_2 = []
        for i  in range (count):
            data_2.append(int(stat2.split(' ')[i+2]))
        total_2 = data_2[0]+data_2[1]+data_2[2]+data_2[3]+data_2[4]+data_2[5]+data_2[6]+data_2[7]+data_2[8]+data_2[9]
        idle_2 = data_2[3]

        total = int(total_2-total_1)
        idle = int(idle_2-idle_1)
        usage = int(total-idle)
        # print("idle:"+str(idle)+"  total:"+str(total))
        usageRate =int(float(usage * 100/ total))
        # print("usageRate:%d"%usageRate)
        return "CPU:"+str(usageRate)+"%"

    # 顯示進度條
    def ProgressBar(self):
        # 顯示的符號
        symbol = '#'
        # 條的長度
        bar_length = 21    
        if self.progress_bar <= 100:
            self.progress_bar += 1
        else:
            self.progress_bar = 1    
        # 計算目前的條長度
        filled_length = int(round(bar_length * self.progress_bar / 100))
        # 設定輸出格式，使用 \r 將光標移動到行首
        # 使用 end='' 讓 print 函式不換行輸出
        block = str(symbol * filled_length)
        space = str(". " * (bar_length - filled_length))   
        #print(f'Progress: [{symbol * filled_length}{" " * (bar_length - filled_length)}] {progress}%', end='\r')
        l_szTemp = str(block+space)
        # 更新進度       
        return l_szTemp

    # 設定 OLED 顯示
    def SetOLEDshow(self):
        # 使用黑色填滿畫布
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
        # CPU 字串 : 使用率
        CPU = self.GetCPULoadRate()
        # CPU 溫度
        cmd = os.popen('vcgencmd measure_temp').readline()
        CPU_TEMP = cmd.replace("temp=","Temp:").replace("'C\n","C")
        # 塞溫度給變數
        self.Temp = float(cmd.replace("temp=","").replace("'C\n",""))
        # 記憶體使用率
        cmd = "free -m | awk 'NR==2{printf \"RAM:%d%%\",($3)/($2)*100}'"
        MemUsage = subprocess.check_output(cmd, shell = True )
        # Disk 空間使用率
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk:%d%%\",  ($3)/($2)*100}'"
        Disk = subprocess.check_output(cmd, shell = True )
        # IP
        cmd = "hostname -I | cut -d\' \' -f1"
        IP = subprocess.check_output(cmd, shell = True )

        # 依照個人喜好顯示
        # draw.text((x, top), str("Akita's RaspberrPi"), font=font, fill=255)
        self.draw.text((self.x, self.top), "IP:" + str(IP.decode('utf-8')),  font=self.font, fill=255)
        self.draw.text((self.x, self.top+8), str(CPU), font=self.font, fill=255)
        self.draw.text((self.x+50, self.top+8), str(MemUsage.decode('utf-8')),  font=self.font, fill=255)
        # self.draw.text((self.x, self.top+16), str(Disk.decode('utf-8')),  font=self.font, fill=255)
        self.draw.text((self.x, self.top+16), str(CPU_TEMP), font=self.font, fill=255)
        self.draw.text((self.x, self.top+24), self.ProgressBar(), font=self.font, fill=255)        
        # Display image.
        self.display.image(self.image)
        self.display.display()
        # time.sleep(.1)


#========================
#       Main Function
#========================
if __name__ == "__main__":

    # 迴圈更新時間
    loop_time = 0.5
    # 風扇更新運轉速度時間(秒)
    Fan_update_time = 2
    # RGB_LED更新時間(秒)
    RGB_update_time = 5
    # Class 設定
    HAT  = HAT_Set()
    OLED = OLED_Set()
    # 風扇速度設為 0
    HAT.SetFanSpeed(0)
    # RGB 設定 
    HAT.SetRGBEffect(1) # 呼吸燈效果
    HAT.SetRGBSpeed(3)  # 亮滅速度最慢
    # 階段溫度
    level_temp = 0
    # 風扇運轉計數
    time_count_Fan = 0
    # RGB_LED 執行計數
    time_count_RGB = 0
    # RGB_LED 現在顏色
    now_color = 0
    # OLED 初始化設定
    OLED.Adafruit_SSD1306_Init()
    # Warning Flag
    warning_flag = 0
    # Warning Temp
    warning_Temp = 60
    # 開機動畫
    for i in range(43):        
        image =  Image.open(f"/home/Akita/RGB_Cooling_HAT/boot_imgs/frame_{i}.png").resize((128, 32), Image.ANTIALIAS)
        canvas = Image.new('RGB', (OLED.display.width, OLED.display.height), (0, 0, 0)).convert('1')   
        # 顯示圖像
        canvas.paste(image, (0, 0))
        # # Display image.
        OLED.display.image(canvas)
        OLED.display.display()
        time.sleep(0.1)
    # 一直執行
    while True:
        # 更新 OLED 顯示畫面
        OLED.SetOLEDshow()	
        # 風扇根據溫度更新運轉速度
        if(time_count_Fan > (Fan_update_time/loop_time)):
            # print(OLED.Temp)
            HAT.TempCtrlSpeed(OLED.Temp)            
            time_count_Fan = 0                
             
        # RGB_LED 每隔一段時間更新顏色
        if(time_count_RGB > (RGB_update_time/loop_time)):
            # 顏色循環
            if(now_color > 9):
                now_color = 0
            HAT.SetRGBColor(now_color)
            now_color += 1
            time_count_RGB = 0

        time_count_Fan += 1
        time_count_RGB += 1
        # 溫度警告動畫
        if(OLED.Temp >  warning_Temp and( warning_flag == 0)):
            for i in range(13):        
                image =  Image.open(f"/home/Akita/RGB_Cooling_HAT/warning_imgs/frame_{i}.png").resize((128, 32), Image.ANTIALIAS)
                canvas = Image.new('RGB', (OLED.display.width, OLED.display.height), (0, 0, 0)).convert('1')
                # 顯示圖像
                canvas.paste(image, (0, 0))
                # # Display image.
                OLED.display.image(canvas)
                OLED.display.display()
                # 調整顯示
                if(i!=12):
                    time.sleep(0.01)
            warning_flag = 1
        # 低於 40 度重設 flag
        if(OLED.Temp < 40):
            warning_flag = 0
        # 0.05 秒執行一次
        time.sleep(loop_time)
        