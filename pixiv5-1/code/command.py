import requests,time,random,os
from threading import Thread
from queue import Queue

#---------------常规设置----------------
USER_AGENT = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
PICTURE_SAVE_PATH = r"./pictures/"
THREAD_NUM = 8
#-------------------------------------

#-----------------------------------主功能--------------------------------------------------------

def get_url(url,url_queue:Queue,num:int):    #用于获取P站图片链接
    """
    爬取网页图片真实地址
    :param url: url
    :param url_queue: 存储网页内地址队列
    :param num: 线程数量
    :return: None
    """
    picture_id = url.split("/")[-1]
    main_url = fr"https://www.pixiv.net/ajax/illust/{picture_id}/pages?lang=zh" #存储图片真实url的json文件
    response = requests.get(main_url, headers={"User-Agent":USER_AGENT, "Referer": "https://www.pixiv.net/"}) #Referer检测是否从pixiv官网上爬取
    body = response.json()["body"]
    for urls in body:
        original = urls["urls"]["original"] #获取直连链接
        url_queue.put(original) #将直连网址导入队列
    for i in range(num):  #发送5个停止命令
        url_queue.put(False)


def download_picture(url, thread_num:int=8):  #下载图片(main)
    """
    下载网页中的所有图片
    :param url: url
    :param thread_num: 线程数量
    :return: OK
    """
    url_queue = Queue() #接收图片真实地址队列
    get_url(url, url_queue, thread_num)
    for i in range(thread_num): #创建线程
        get_ = DownloadThread(url_queue)
        get_.start()
    while True:
        if url_queue.empty():
            print("下载完成")
            break


class DownloadThread(Thread):   #下载图片的线程任务分配
    """
    多线程任务分配
    """
    def __init__(self,uq:Queue):
        super().__init__()
        self.uq = uq    #get_url之后留有各各图片真实url的队列
    def run(self):
        while True:
            url_pix = self.uq.get()
            if url_pix is False:    #判断是否接收到停止信号
                self.uq.task_done()
                break
            self.uq.task_done()
            pix = requests.get(url=url_pix,
                               headers={"User-Agent": USER_AGENT, "Referer": "https://www.pixiv.net/"})
            time.sleep(random.random()) #时停限制(防封号)
            name = time.time()  #用时间戳来起文件名(防重名)
            with open(fr"{PICTURE_SAVE_PATH}{name}.{url_pix[-3:]}", "wb") as f:    #图片保存位置
                f.write(pix.content)  # 下载

#--------------------------------------------------------------------------------------------------

#-------------------------------------附加功能------------------------------------------------------
def file_check(name:str,model:int):
    """
    文件管理
    :param name: 文件/路径
    :param model: 模式
    :return: bool
    """
    if model == 1:
        #检查文件/目录是否存在
        if os.path.exists(name):
            return True
        else:
            return False
    elif model == 2:
        #创建文件
        if not file_check(name,1):
            with open(name, "w") as f:
                f.write("")
    elif model == 3:
        #创建目录
        if not file_check(name,1):
            os.makedirs(name)
#-------------------------------------------------------------------------------------------------

def get_picture():
    #爬取图片页面
    os.system("cls")
    file_check(PICTURE_SAVE_PATH,3)
    url = input("请输入网址(看准以https开头,输入exit退出):")
    if not url == "exit":
        try:
            download_picture(url,THREAD_NUM)
        except Exception as e:
            print(f"出错了,错误内容:{e}")
            time.sleep(3)

def setting():
    #设置
    os.system("cls")
    print("设置(输入exit退出):\n1,设置保存路径\n2,设置线程数\n")
    global THREAD_NUM,PICTURE_SAVE_PATH
    print(f"当前设置:\n图片保存路径:{PICTURE_SAVE_PATH}\n线程数量:{THREAD_NUM}\n")
    choose = input("输入选项:")
    if choose == "1":
        os.system("cls")
        path = input("输入保存图片路径(路径结尾加斜杠,请使用'/'斜杠,输入exit退出):")
        if not path == "exit":
            PICTURE_SAVE_PATH = path
            print("更改成功")
    elif choose == "2":
        os.system("cls")
        num = input("请输入修改线程数量(默认8,输入exit退出):")
        if not num == "exit":
            try:
                num = int(num)
                if num <= 0:
                    raise ZeroDivisionError
            except ValueError:
                print("输入值有误请输入数字")
                time.sleep(2)
            except ZeroDivisionError:
                print("数字不能小于零或等于零")
                time.sleep(2)
            else:
                THREAD_NUM = num
                print("更改成功")
    else:
        print("输入错误")
        time.sleep(2)

def main():
    """
    命令窗口
    :return: picture
    """
    while True:
        print("欢迎使用liu制作的pixiv爬虫工具,以下为菜单选项:\n1,爬取图片\n2,设置\n输入exit退出\n")
        choose = input("输入选项:")
        if choose == "1":
            get_picture()
        elif choose == "2":
            setting()
        elif choose == "exit":
            break
        else:
            print("输入内容有误,请重新输入")
        os.system("cls")

if __name__ == '__main__':
    main()