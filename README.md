# RGB_Cooling_HAT
Pi 4B 套件的簡易程式碼

我買了一個 Pi 的 [RGB 套件](https://github.com/YahboomTechnology/Raspberry-Pi-RGB-Cooling-HAT)

但套件的 IO 常常莫名的中斷，導致程式出錯
所以做了個修改版也加上開機動畫
很久沒寫 Py 了，東拼西湊，就上傳做個紀錄

整合 溫度顯示與 RGB 燈光控制

OLED 顯示開機動畫與溫度過高動畫

平時顯示 IP、CPU、RAM、溫度
還有一個動畫條用來看程式有沒有卡住

安裝方式:
run install.sh (會建立開機自啟動資料夾，將 start.desktop 放進去)
之後重開機會自動執行 start.desktop
等待五秒後呼叫 start.sh 執行程式
