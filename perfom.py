
#!/usr/bin/python
'''
Written by Gaurav Dogra
Github: https://github.com/dograga
Script to extract vm performance data
'''
import atexit
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import time
import datetime
from pyVmomi import vmodl
from threading import Thread
from pyVim import connect




class perfdata():
   def perfcounters(self):
      perfcounter=['cpu.usage.average','mem.usage.average']
      return perfcounter

   def run(self,content,vm,counter_name):
       output=[]
       try:
          perf_dict = {}
          perfManager = content.perfManager
          perfList = content.perfManager.perfCounter
          print(perfList)
          for counter in perfList: #build the vcenter counters for the objects
              counter_full = "{}.{}.{}".format(counter.groupInfo.key,counter.nameInfo.key,counter.rollupType)
              perf_dict[counter_full] = counter.key
          counterId = perf_dict[counter_name]
          metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance="")
          timenow=datetime.datetime.now()
          startTime = timenow - datetime.timedelta(days=15)
          print (startTime)
          endTime = timenow
          query = vim.PerformanceManager.QuerySpec(entity=vm,metricId=[metricId],startTime=startTime,endTime=endTime,maxSample=10)
          stats=perfManager.QueryPerf(querySpec=[query])
          count=0
          for val in stats[0].value[0].value:
              perfinfo={}
              val=float(val/100)
              perfinfo['timestamp']=stats[0].sampleInfo[count].timestamp
              perfinfo['hostname']=vm
              perfinfo['value']=val
              output.append(perfinfo)
              count+=1
          for out in output:
              print ("Counter: {} Hostname: {}  TimeStame: {} Usage: {}".format (counter_name,out['hostname'],out['timestamp'],out['value']))
       except vmodl.MethodFault as e:
           print("Caught vmodl fault : " + e.msg)
           return 0
       except Exception as e:
           print("Caught exception : " + str(e))
           return 0

def main():
    si = connect.SmartConnectNoSSL(host='vc-khut.srv.local', user='nokhrimenko', pwd = 'NikolonsO345831', port = 443)

    content = si.RetrieveContent()
    perf=perfdata()
    counters=perf.perfcounters()
    search_index = content.searchIndex
   # vm = perf.Get_VM_obj(vm_name = 'bi-rt-mstr9')
    vm = search_index.FindByDnsName(None, 'bi-rt-mstr9', True)  #   //vm dnsname is Hostname as reported by vmtool
    for counter in counters:
        p = Thread(target=perf.run,args=(content,vm,counter,))
        p.start()

# start
if __name__ == "__main__":
    main()