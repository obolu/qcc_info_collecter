#!/usr/bin/python3 
# -*- coding: utf-8 -*-
#coding: UTF-8
#python3 URL
#cookie可能会过期，过期了更换新的QCCSESSID字段即可

import urllib.parse
import requests
import re
import sys
import re

def get_conpany_name(content):
        findenty = re.compile(r'<title>(.*?) - 企查查</title>',re.DOTALL)
        enty = re.findall(findenty,content)
        name = enty[0]
        return name

def get_register_url(content):
        findenty = re.compile(r'\}\);" href="(.*?)" class="" target="_blank" data-trigger="hover" data-toggle="tooltip"')
        enty = re.findall(findenty,content)
        if len(enty)>0:
            url = enty[0]
        else:
            return "NULL"
        return url    

def wash(content):
        result1 = content.replace("\"","\n")
        result2 = result1.replace("<","")
        result3 = result2.replace(">","")
        result = result3.replace("/a /span /td td class=","")
        #清洗数据，返回一个数组["控制公司URL","公司名","",占股百分比"]
        array = result.split('\n')
        return array

def get_investment_conpany_num(content):
        findenty = re.compile(r'对外投资</span> <span class="tbadge">(.*?)</span>')
        enty = re.findall(findenty,content)
        if len(enty)==0:
            print ("该公司不存在对外投资公司")
            return exit()
        #判断是否存在控制公司
        num = enty[0]
        result = "该公司共有："+str(num)+" 个对外投资公司"
        print (result)
        print ("———————————————————————暂不支持对外投资公司信息收集——————————————————————————")
        return str(num)  

def get_son_conpany_num(content):
        findenty = re.compile(r'控制企业</h3> <span class="tbadge">(.*?)</span>')
        enty = re.findall(findenty,content)
        if len(enty)==0:
        	print ("该公司不存在控制公司/控制企业")
        	invest_num = get_investment_conpany_num(content)
        	if invest_num==0:
        		return exit()
        	else:
        		return invest_num
        #判断是否存在控制公司
        num = enty[0]
        result = "该公司共有："+str(num)+" 个控制企业"
        print (result)
        print ("————————————————————————————————————————————————————————————————")
        return str(num)       

def get_son_conpany_info(content):
        findenty = re.compile(r'class="whead-text"> <a href="(.*?)</td> <td> <div class="tdpath">')
        enty = re.findall(findenty,content)
        #实际就是一个数组，每个元素是一个控制公司的URL+公司名+公司所属关系+占股百分比
        return enty

def input_name_get_qcc_url(c_name):
        url = "https://www.qcc.com/web/search?key="+str(c_name)
        headers={
                     'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',                
                     'Cookie':'1'}      
        r=requests.get(url,headers=headers)
        findenty = re.compile(r'<a href="(.*?)" target="_blank" class="title" data-v-')
        enty = re.findall(findenty,r.text)
        result = enty[0]+"#base"
        #print (result)
        #获取查询主公司的URL
        return result

def get_conpany_unique(url):
        url1 = url.replace("https://www.qcc.com/firm/","")
        url2 = url1.replace(".html","")
        unique = url2.replace("#base","")
        return unique

def get_all_son_conpany(unique,conpany_name,num):
    for i in range(2,int(num)+1):
        url = "https://www.qcc.com/company_getinfos?unique="+str(unique)+"&companyname="+str(conpany_name)+"&p="+str(i)+"&tab=base&box=holdco&holdprovince=&holdindustry="
        headers={  
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'Cookie':'QCCSESSID='                
        }
        r=requests.get(url,headers=headers)
        #print (r.text)
        company_arr = get_son_conpany_info(r.text)
        if len(company_arr)>1:
            for i in range(0,len(company_arr)):
                url = 'https://www.qcc.com'+str(wash(company_arr[i])[0])
                print (url)
                print ("控制公司名称: "+wash(company_arr[i])[1])
                print ("控制公司占股比例: "+wash(company_arr[i])[3])
                r1=requests.get(url,headers=headers)
                print ("控制公司URL: "+get_register_url(r1.text))
                print ("————————————————————————————————————————————————————————————————")
                         

def main(conpany_url):
        url = conpany_url
        headers={
                     'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
                     'Cookie':'QCCSESSID='               
                     }
        #proxies = {'http': 'http://127.0.0.1:8080'}
        #r=requests.post(url,headers,proxies=proxies)
        #添加代理，测试代码
        r=requests.get(url,headers=headers)

        conpany_name = get_conpany_name(r.text)
        unique = get_conpany_unique(url)
        #获取主公司名称、unique码
        print ("主公司名称: "+conpany_name)
        print ("主公司URL: "+get_register_url(r.text))
        #输出主公司信息
        all_son_conpany_num = get_son_conpany_num(r.text)
        page_num = int(all_son_conpany_num)//10+1
        company_arr = get_son_conpany_info(r.text)
        #获得控制企业数据

        if len(company_arr)>1:
        	#存在控制公司，就输出信息
            for i in range(0,len(company_arr)):
                url = 'https://www.qcc.com'+str(wash(company_arr[i])[0])
                print ("控制公司名称: "+wash(company_arr[i])[1])
                print ("控制公司占股比例: "+wash(company_arr[i])[3])
                r1=requests.get(url,headers=headers)
                print ("控制公司URL: "+get_register_url(r1.text))
                print ("————————————————————————————————————————————————————————————————")   

        if page_num>1:
        	#如果大于10个控制公司，爬翻页后的
        	get_all_son_conpany(unique,conpany_name,page_num)
        	return "爬取完毕"
        else:
        	return "爬取完毕"

if __name__ == '__main__':
        c_name = sys.argv[1]
        c_url = input_name_get_qcc_url(c_name)
        main(c_url)
