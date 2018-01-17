# -*- coding: utf-8 -*-
"""
@time: 2018-01-04
@author: ssf
"""

"""
Usage:
    python hack12306.py [-c] <configpath>
Options:
    -h,--help   显示帮助菜单
    -c          指定config.ini绝对路径
Example:
    python hack12306.py -c /usr/local/services/config.ini
    或者
    python hack12306.py
"""

from splinter.browser import Browser
from configparser import ConfigParser
from time import sleep
import traceback
import time, sys
import codecs
import argparse
import os

class hackTickets(object):
    """docstring for hackTickets"""
	
    """读取配置文件"""
    def readConfig(self, config_file='config.ini'):
        # 补充文件路径，获得config.ini的绝对路径，默认为主程序当前目录
        path = os.path.join(os.getcwd(), config_file)

        cp = ConfigParser()
        try:
            # 指定读取config.ini编码格式，防止中文乱码（兼容windows）
            cp.readfp(codecs.open(config_file, "r", "utf-8-sig"))
        except IOError as e:
            print(u'打开配置文件"%s"失败, 请先创建或者拷贝一份配置文件config.ini' % (config_file))
            input('Press any key to continue')
            sys.exit()
        # 登录名
        self.username = cp.get("login", "username")
        self.email_username = cp.get("login", "email_username")
        # 密码
        self.passwd = cp.get("login", "password")
        self.email_passwd = cp.get("login", "email_password")
        # 始发站
        starts_city = cp.get("cookieInfo", "starts")
        # config.ini配置的是中文，转换成"武汉,WHN"，再进行编码
        self.starts = self.convertCityToCode(starts_city).encode('unicode_escape').decode("utf-8").replace("\\u", "%u").replace(",", "%2c")
        # 终点站
        ends_city = cp.get("cookieInfo", "ends");
        self.ends = self.convertCityToCode(ends_city).encode('unicode_escape').decode("utf-8").replace("\\u", "%u").replace(",", "%2c")
        # 乘车时间
        self.dtime = cp.get("cookieInfo", "dtime")
        # 车次
        orderStr = cp.get("orderItem", "order")
        # 配置文件中的是字符串，转换为int
        self.order = int(orderStr)
        # 乘客名
        self.users = cp.get("userInfo", "users").split(",")
        # 车次类型
        self.train_types = cp.get("trainInfo", "train_types").split(",")
        # 发车时间
        self.start_time = cp.get("trainInfo", "start_time")
        # 可接受的座位类型
        self.seat_types = cp.get("trainInfo", "seat_types").split(",")

        # 网址
        self.ticket_url = cp.get("urlInfo", "ticket_url")
        self.login_url = cp.get("urlInfo", "login_url")
        self.initmy_url = cp.get("urlInfo", "initmy_url")
        self.buy = cp.get("urlInfo", "buy")

        # 浏览器名称：目前使用的是chrome
        self.driver_name = cp.get("pathInfo", "driver_name")
        # 浏览器驱动（目前使用的是chromedriver）路径
        self.executable_path = cp.get("pathInfo", "executable_path")

    def loadConfig(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', help='Specify config file, use absolute path')
        args = parser.parse_args()
        if args.config:
            # 使用指定的配置文件
            self.readConfig(args.config)
        else:
            # 使用默认的配置文件config.ini
            self.readConfig()

    """
        加载映射文件，并将中文"武汉"转换成编码后的格式：“武汉,WHN“
    """
    def loadCityCode(self):
        city_codes = {}
        with open('city_code.txt', 'r+', encoding='utf-8') as f:
            for l in f.readlines():
                city = l.split(':')[0]
                code = l.split(':')[1].strip()
                city_codes[city] = city + "," + code
        return city_codes

    def convertCityToCode(self, c):
        try:
            return self.city_codes[c]
        except KeyError:
            print("转换城市错误，请修改config.ini中starts或者ends值为中文城市名")
            return False

    def __init__(self):
        # 读取城市中文与三字码映射文件，获得转换后到城市信息-- “武汉”: "武汉,WHN"
        self.city_codes = self.loadCityCode();

        # 读取配置文件，获得初始化参数
        self.loadConfig();

    def login(self):
        # 登录
        self.driver.visit(self.login_url)
        # 自动填充用户名
        self.driver.fill("loginUserDTO.user_name", self.username)
        # 自动填充密码
        self.driver.fill("userDTO.password", self.passwd)

        print(u"等待验证码，自行输入...")

        # 验证码需要自行输入，程序自旋等待，直到验证码通过，点击登录
        while True:
            if self.driver.url != self.initmy_url:
                sleep(1)
            else:
                break
    
    """更多查询条件"""            
    def searchMore(self):
        # 选择车次类型
        for type in self.train_types:
            #type = type.replace("\"", "")
            # 车次类型选择
            train_type_dict = {'T': u'T-特快',                # 特快
                                'G': u'GC-高铁/城际',         # 高铁
                                'D': u'D-动车',               # 动车
                                'Z': u'Z-直达',               # 直达
                                'K': u'K-快速'                # 快速
                                }
            if type == 'T' or type == 'G' or type == 'D' or type == 'Z' or type == 'K':
                print(u'--------->选择的车次类型', train_type_dict[type])
                self.driver.find_by_text(train_type_dict[type]).click()
            else:
                print(u"车次类型异常或未选择!(train_type=%s)" % type)
		
        # 选择发车时间
        print(u'--------->选择的发车时间', self.start_time)
        self.driver.find_option_by_text(self.start_time).first.click()
	
    """填充查询条件"""
    def preStart(self):
        # 加载查询信息
        # 出发地
        self.driver.cookies.add({"_jc_save_fromStation": self.starts})
        # 目的地
        self.driver.cookies.add({"_jc_save_toStation": self.ends})
        # 出发日
        self.driver.cookies.add({"_jc_save_fromDate": self.dtime})

    def buyTickets(self):
        order_ok = False

        try:
            print(u"购票页面开始...")
            
            # 填充查询条件
            self.preStart()
            
            # 带着查询条件，重新加载页面
            self.driver.reload()

            count=0
            # 预定车次算法：根据order的配置确定开始点击预订的车次，0-从上至下点击
            if self.order==0:
                while self.driver.url == self.ticket_url:
                    # 勾选车次类型，发车时间
                    self.searchMore();
                    #sleep(0.05)
                    sleep(1.0)
                    self.driver.find_by_text(u"查询").click()
                    count += 1
                    print(u"循环点击查询... 第 %s 次" % count)
                    
                    try:
                        for i in self.driver.find_by_text(u"预订"):
                            i.click()
                            # 等待0.3秒，提交等待的时间
                            sleep(0.3)

                    except Exception as e:
                        print(e)
                        print(u"还没开始预订 %s" %count)
                        continue
            print(u"开始预订...")

            #选择用户
            print(u'开始选择用户...')
            while True:
                sleep(0.1)
                try:
                    for user in self.users:
                        self.driver.find_by_text(user).last.click()
                    break
                except:
                    pass

            #提交订单
            print(u"提交订单...")
            submitOrder_id = self.driver.find_by_id('submitOrder_id')
            while not submitOrder_id:
                sleep(0.1)
                submitOrder_id = self.driver.find_by_id('submitOrder_id')
            submitOrder_id.click()



            order_start = time.time()  # 下单开始时间
            order_timeout = 10.0  # 下单超时时间
            print(u"确认选座...")

            seat_type_dict = {
                'A': u'高级软卧',
                'B': u'软卧',
                'C': u'动卧',
                'D': u'硬卧',
                'E': u'软座',
                'F': u'硬座',
                'G': u'无座',
                'H': u'其他',
            }
            seat_need_types = []    #e.g. [u'硬卧', u'硬座'']
            for seat_type in self.seat_types:
                seat_need_type = seat_type_dict[seat_type]
                seat_need_types.append(seat_need_type)
            print(seat_need_types)

            while True:
                sleep(1.0)
                try:
                    order_list = self.driver.find_by_id('check_ticketInfo_id')
                    if order_list and len(order_list)>0:
                        order_item = order_list[0]
                        seat_type_text = order_item.find_by_xpath("//tr//td[@class='no-seat']").text
                        if seat_type_text in seat_need_types:
                            self.driver.find_by_id('qr_submit_id').click()
                            order_ok = True
                            break
                        else:
                            order_ok = False
                            print('座位类型不匹配，再来!')
                except:
                    pass

                if order_start + order_timeout > time.time():
                    break
                else:
                    print('等待订单弹窗...')

        except Exception as e:
            print(e)
        finally:
            return order_ok

    """发送邮件"""

    def send_mail(email_username, email_password):
        import re
        import smtplib
        from email.mime.text import MIMEText

        # SMTPserver = 'smtp.163.com'
        # SMTPserver = 'smtp.qq.com'
        SMTPserver = ''
        try:
            pattern = re.compile('.*@(.*).com')
            m = re.match(pattern, email_username)

            company = m.group(1)
            SMTPserver = 'smtp.%s.com' % company
        except:
            print('解析邮件名失败!')
            return

        sender = email_username
        destination = email_username
        password = email_password

        message = '抢票软件已经下单，您快去支付一下'
        msg = MIMEText(message)

        msg['Subject'] = '抢票软件通知'
        msg['From'] = sender
        msg['To'] = destination

        # mailserver = smtplib.SMTP(SMTPserver, 25)
        # mailserver.login(sender, password)
        mailserver = smtplib.SMTP()
        mailserver.connect(SMTPserver, 25)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.set_debuglevel(1)
        mailserver.login(sender, password)

        mailserver.sendmail(sender, [sender], msg.as_string())
        mailserver.quit()
        print('send email success')

    """入口函数"""
    def start(self):
        # 初始化驱动
        self.driver=Browser(driver_name=self.driver_name,executable_path=self.executable_path)
        # 初始化浏览器窗口大小
        self.driver.driver.set_window_size(1400, 1000)

        # 登录，自动填充用户名、密码，自旋等待输入验证码，输入完验证码，点登录后，访问 tick_url（余票查询页面）
        self.login()

        order_ok = False
        while not order_ok:
            # 登录成功，访问余票查询页面
            self.driver.visit(self.ticket_url)

            # 自动购买车票
            order_ok = self.buyTickets()

        if order_ok:
            print('抢票成功')
            self.send_mail(self.email_username, self.email_passwd)
        else:
            print('亲，你重新启动抢票程序再来一次吧')


if __name__ == '__main__':
    hackTickets = hackTickets()
    hackTickets.start()
