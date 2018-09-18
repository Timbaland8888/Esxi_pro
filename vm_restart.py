# -*- encoding:utf-8 -*-
#function:control exsi server for restart vm
#date:2018-09-16
#Arthor:Timbaland
_Arthur_ = 'Timbaland'

import pysphere,pymysql
from gi import VIServer
import logging
import ssl
import datetime,os,time
#全局取消证书验证,忽略连接VSPHERE时提示证书验证
ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VcentTools(object):
    def __init__(self,host_ip,user,password):
        self.host_ip = host_ip
        self.user = user
        self.password = password

    # 可以连接esxi主机，也可以连接vcenter

    def _connect(self):

        server_obj = VIServer()



    def esxi_version(self):
        server_obj = VIServer()
        try:
            server_obj.connect(self.host_ip, self.user,  self.password)
            servertype, version = server_obj.get_server_type(),server_obj.get_api_version()
            server_obj.disconnect()
            return servertype, version
        except Exception as  e:
            print e

    def vm_status(self,vm_name):

        server_obj = VIServer()
        try:
            server_obj.connect(self.host_ip, self.user,  self.password)
            # servertype, version = server_obj.get_server_type(),server_obj.get_api_version()


        except Exception as  e:
            print e

        # 通过名称获取vm的实例
        vm = server_obj.get_vm_by_name(vm_name)
        if vm.is_powered_off() == False:
            server_obj.disconnect()
            return 1

        if vm.is_powered_off()  == True:
            server_obj.disconnect()
            return 0
        return u"未知状态"

    def vmaction(self,vm_name):

        server_obj = VIServer()
        try:
            server_obj.connect(self.host_ip, self.user,  self.password)
        except Exception as  e:
            print e

        # 通过名称获取vm的实例
        vm = server_obj.get_vm_by_name(vm_name)
        if vm.is_powered_off() == False:
            try:
                vm.reset()
                for i in range(1,30):
                    print unicode('虚拟机%s 正在重置中。。。。，请等待注册\n'.format( vm_name.encode('utf-8')),'utf-8')
                    time.sleep(1)
                server_obj.disconnect()

                return
            except Exception as e:
                print e


        if vm.is_powered_off()  == True:
            vm.power_on()
            print unicode('虚拟机%s 正在开机中。。。。' % (vm_name), 'utf-8')
            server_obj.disconnect()
            return 0


        
        
        
class  Class_VM(object):
     def __init__(self,host,user,pwd,port,db,charset):
         self.host = host
         self.user = user
         self.pwd = pwd
         self.port = port
         self.db = db
         self.charset = charset
     # 获取教室里面的虚拟机信息
     def get_vmname(self,query_sql):
        try:
            # 连接mysql数据库参数字段
            con = None
            db = pymysql.connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db, port=self.port, charset=self.charset)
            cursor = db.cursor()
            vmlist = []
            cursor.execute(query_sql)
            result = cursor.fetchall()
            # 获取教室云桌面数量
            vm_count = len(result)
            print unicode('502教室云桌面虚拟机数量共{0}台'.format(vm_count), 'utf-8')

            # print len(cursor.fetchall())
            # cursor.execute(query_vm)
            for vm_id in range(0, vm_count, 1):
                # print result[vm_id][0]
                # print result[vm_id][1]
                vmlist.append(result[vm_id][0])
                # print result[vm_id][0]

            # print type(cursor.fetchall()[0])

            db.commit()

        except ValueError:
            db.roolback
            print 'error'
        # 关闭游标和mysql数据库连接
        cursor.close()
        db.close()
        return vmlist
if __name__ == '__main__':
    #连接vsphere
    obj = VcentTools("10.21.71.150", "administrator@gdaib.local", "1qaz@WSX")
    #查询教室虚拟机
    query_vm = '''SELECT vm_name FROM hj_vm  WHERE vm_type =1 '''
    #查询虚拟机信息
    p = Class_VM( '10.21.71.161','root','123456',3306,'hj3_backend','utf8')
    # print p.get_vmname(query_vm)[0]
    # 获取当前时间
    now_date = datetime.datetime.now().strftime('%H:%M')
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, 'settime.ini')
    # print path
    # print now_date
    # 自定义重启时间
    # set_retime = ['01:30', '01:31']
    settime = []
    with open(path,'r') as  f:
         settime = f.readlines()
    # print settime[1]


    while True:

        # if datetime.datetime.now().strftime('%H:%M') == settime[1].split('=')[1]:
        #     for vmname in p.get_vmname(query_vm):
        #         obj.vmaction(vmname)
        #         logger.info('正在重置%s' %(vmname))
        #         time.sleep(10)
        nowdate = datetime.datetime.now().strftime
        logger.info(u'现在时间%s,还未到才重置时间%s 请等待重置' %(now_date,settime[1].split('=')[1]))
        #检查是否有关机的虚拟机
        for  vmname in p.get_vmname(query_vm):
            # t = datetime.datetime.now().strftime('%H:%M')
            # print t
            # print settime[1].split('=')[1].lstrip()

            if datetime.datetime.now().strftime('%H:%M') == settime[1].split('=')[1].lstrip():
                for vmname in p.get_vmname(query_vm):
                    obj.vmaction(vmname)
                    logger.info(u'正在重置%s' % (vmname))
                    time.sleep(10)
            if obj.vm_status(vmname) == 0:
                obj.vmaction(vmname)
                logger.info(u'%s正在开机。。。。' %(vmname))
            else:
                logger.info(u'虚拟机%s正在运行,未到重置时间：%s'%(vmname,unicode(settime[1].split('=')[1].lstrip())))

            time.sleep(3)

