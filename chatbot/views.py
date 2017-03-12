#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.http import HttpResponse

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import requests
import re
from pprint import pprint
import random 
from datetime import date, timedelta
import numpy

import pandas
from bs4 import BeautifulSoup as bs

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from pandas_datareader import data
from yahoo_finance import Share
import xml.etree.ElementTree as ET
import urllib2

# Create your views here.

VERIFY_TOKEN = 'VERIFY_TOKEN'
PAGE_ACCESS_TOKEN = 'PAGE_ACCESS_TOKEN'
def main():
  pass
def stock_search(symbol="YHOO"):
  stock=Share(symbol)
  open_price=stock.get_open()
  close_price=stock.get_prev_close()
  price=stock.get_price()
  high=stock.get_days_high()
  low=stock.get_days_low()
  volume=stock.get_volume()

  return stock,open_price,close_price,price,high,low,volume

def historical_data(start_date="2016-09-23",end_date="2016-09-24",symbol="YHOO"):
  stock=Share(symbol)
  return stock.get_historical(start_date, end_date)

def stock_info(symbol="YHOO"):
  stock=Share(symbol)
  return str(stock.get_info())

def list_df(data):
  Adj_Close=[]
  Close=[]
  Open=[]
  Close=[]
  High=[]
  Low=[]
  Volume=[]
  Date=[]
  CloseNext=[]
  DailyReturn=[]
  for item in data:
    for keys,values in item.iteritems():
      if keys=="Adj_Close":
        Adj_Close.append(values)
      if keys=="Close":
        Close.append(values)
      if keys=="Open":
        Open.append(values)
      if keys=="High":
        High.append(values)
      if keys=="Low":
        Low.append(values)
      if keys=="Volume":
        Volume.append(values)
      if keys=="Date":
        Date.append(values)

  close=7

  for item in Close:
    CloseNext.append(close)
    DailyReturn.append(close)


  
  data=zip(Date,Adj_Close,Close,High,Low,Volume,Open,CloseNext)
  data = pandas.DataFrame(data,
        columns=["Date", "Adj_Close", "Close", "High","Low","Volume","Open","CloseNext"])
  data.CloseNext=data.Close.shift(-1)
  
  
  return data

def get_data_slow():
  data=historical_data("2015-08-07","2016-08-07")
  training_set=list_df(data)

  data=historical_data("2016-08-07","2016-08-08")

  test=list_df(data)
  data=historical_data("2016-08-08","2016-08-09")
  today=list_df(data)

def get_data(symbol,start_date,end_date):
  df = data.get_data_yahoo(symbol,start_date,end_date)
  
  if df.empty:
    df=data.get_data_yahoo(symbol,"2016-08-07","2016-08-08")
  return df

def predic_price(symbol="YHOO"):
  yesterday = date.today() - timedelta(2)
  yesterday=yesterday.strftime('%Y-%m-%d')
  previous= date.today() - timedelta(3)
  previous=previous.strftime('%Y-%m-%d')
  test_date= date.today() - timedelta(365)
  test_date=test_date.strftime('%Y-%m-%d')
  today_date=date.today()-timedelta(1)
  today_date=today_date.strftime('%Y-%m-%d')

  df=get_data(symbol,test_date,previous)
  df['CloseNext']=df['Close']
  df.CloseNext=df.Close.shift(-1)
  

  test=get_data(symbol,previous,yesterday)

  
  today=get_data(symbol,yesterday,today_date)
  
  columns = df.columns.tolist()
  columns = [ "Adj Close", "High","Low","Volume","Open","Close"]
  target = "CloseNext"

  train=df[:-10]
  
  arr=[]
  
  for value in today['Close']:

    arr.append(value)
  actual=arr[0]

    # Initialize the model class.
  model = LinearRegression()
    # Fit the model to the training data.
  model.fit(train[columns], train[target])
  predictions = model.predict(test[columns])
  return actual,predictions

def stock_news_company(company):
  url=urllib2.urlopen('https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US'%(company))
  tree = ET.parse(url)
  root = tree.getroot()
  
  image_url=root[0][6][0].text
  news1= root[0][7][0].text
  news1_url=root[0][7][1].text
  news1_description= root[0][7][2].text
  news2= root[0][8][0].text
  news2_url=root[0][8][1].text
  news2_description= root[0][8][2].text
  news3= root[0][9][0].text
  news3_url=root[0][9][1].text
  news3_description= root[0][9][2].text
  return image_url,news1,news1_url,news1_description,news2,news2_url,news2_description,news3,news3_url,news3_description

def stock_news_top():
  url=urllib2.urlopen('http://finance.yahoo.com/rss/topfinstories')
  tree = ET.parse(url)
  root = tree.getroot()
  image_url=root[0][5][0].text

  news1= root[0][6][0].text
  news1_url=root[0][6][1].text
  news1_description= root[0][6][2].text

  news2= root[0][7][0].text
  news2_url=root[0][7][1].text
  news2_description= root[0][7][2].text

  news3= root[0][8][0].text
  news3_url=root[0][8][1].text
  news3_description= root[0][8][2].text

  return  image_url,news1,news1_url,news1_description,news2,news2_url,news2_description,news3,news3_url,news3_description

def stock(message):
  code = get_code(message)
  output_text=""
  info=""
  if code != "No code":
    print code
    url = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/jsonp?symbol=%s&callback=myFunction'%(code)
    resp = requests.get(url=url).text.split('(')[1].split(')')[0]
    data=json.loads(resp)
    
    output_text = 'Open: %s\nLast Price: %s\nChange Percent: %s\nHigh: %s\nLow: %s'%(data['Open'],data['LastPrice'],data['ChangePercent'],data['High'],data['Low'])

    info='Name: %s\nSymbol: %s\n'%(data['Name'],data['Symbol'])

  return info,output_text,code

def get_code(name):
  get_code = 'http://dev.markitondemand.com/MODApis/Api/v2/Lookup?input=%s'%(name)
  soup=bs(requests.get(get_code).text,"lxml")
  # print soup
  data = soup.find_all('symbol')
  if len(data)>0:
    print data
    # print data
    code = data[0].text
    print 'code=%s'%code
  else:
    code="No code"
  return code


def set_greeting_text():
  post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%(PAGE_ACCESS_TOKEN)
  
  request_msg = {
    "setting_type":"greeting",
      "greeting":{
        "text":"Stock bo: Type symbol or name of the stock to get started. Use Menu for help."
      }
  }
  response_msg = json.dumps(request_msg)

  status = requests.post(post_message_url, 
        headers={"Content-Type": "application/json"},
        data=response_msg)

  logg(status.text,symbol='--GR--')


def index(request):
  # giphysearch()
  set_menu()
  post_facebook_message('asd','assd')
  handle_quickreply('assd','sss')
  stock_news_company("dd")
  handle_postback("assd","nfu")
  set_greeting_text()
  # post_facebook_message('as','asd')
  # handle_quickreply("as","asd")
  # colour()
  # output_text = quizGen()
  # output_text = pprint.pformat(output_text)
  # output_text=giphysearch()
  output_text="stock_search "
  
  return HttpResponse(output_text, content_type='application/json')


def post_facebook_message(fbid,message_text):
  post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
  info,output_text,code = stock(message_text)
  if len(output_text)>0:
      
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text": info }})
    
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    
    
    response_msg_quickreply =json.dumps(   {

        "recipient":{
            "id":fbid
          },
          "message":{
            "text":"What do you want to find ??",
            "quick_replies":[
              # {
              #   "content_type":"text",
              #   "title":"Historical Data",
              #   #"payload": check(quiz['answer'][0],quiz['options'][0])
              #   "payload":"Info,%s"%(code)
              # },
              {
                "content_type":"text",
                "title":"Today's Data",
                "payload":output_text
              },
              {
                "content_type":"text",
                "title":"graph",
                "payload":"graph,%s"%(code)
              },
              {
                "content_type":"text",
                "title":"predict",
                "payload":"predict,%s"%(code)
              },
              {
                "content_type":"text",
                "title":"Company news",
                "payload":"news,%s"%(code)
              },
              
            ]
          }

    })

    requests.post(post_message_url, 
    headers={"Content-Type": "application/json"},
    data=response_msg_quickreply)
  else:
    output_text="No Stock found"
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text": output_text }})
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)




def logg(message,symbol='-'):
  print '%s\n %s \n%s'%(symbol*10,message,symbol*10)

def handle_quickreply(fbid,payload):
  if not payload:
    return

  post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
  logg(payload,symbol='-QR-')
  response_msg = {"recipient":{"id":fbid}, "message":{"text":payload}}
  payload=payload.split(",")
  a=""
  b=""
  try:
    a=payload[0]
    b=payload[-1]
    logg(a,symbol='-QR-')
    logg(b,symbol='-QR-')
    
         
  except:
    pass

  if a=="Info":
    output_text= str(historical_data("2016-09-23","2016-09-24",b))
    response_msg = {"recipient":{"id":fbid}, "message":{"text":output_text}}

  if a=="predict":
    actual,predict=predic_price(b)

    output_text= "Actual:%s Predicted:%s"%(actual,predict[0])
    response_msg = {"recipient":{"id":fbid}, "message":{"text":output_text}}
  
  # if a=="Data":
  #   stock,open_price,close_price,price,high,low,volume=stock_search(b)
  #   output_text = 'Open: %s\nLast Price: %s\nVolume: %s\nHigh: %s\nLow: %s'%(open_price,close_price,volume,high,low)
  #   response_msg = {"recipient":{"id":fbid}, "message":{"text":output_text}}


   
  
  if a=="graph":
    image_url="http://chart.finance.yahoo.com/z?s=%s&t=1m&q=l&l=on&z=s&p=m2,p"%(b)
    response_msg={

      "recipient":{
          "id":fbid
        },
        "message":{
          "attachment":{
            "type":"image",
            "payload":{
              "url":image_url,
            }
          }
        }

  }
  if a=="news":
    image_url,news1,news1_url,news1_description,news2,news2_url,news2_description,news3,news3_url,news3_description= stock_news_company(b)
     
    logg("COrrect Answer",symbol='-YEhejnecmrS-')
    
    image_url=""
    response_msg= {

      "recipient":{
          "id":fbid
        },
        "message":{
          "attachment":{
            "type":"template",
            "payload":{
              "template_type":"generic",
              "elements":[
                {
                  "title":news1,
                  "item_url":news1_url,
                  "image_url":image_url,
                  "subtitle":news1_description,
                  "buttons":[
                    {
                      "type":"web_url",
                      "url":news1_url,
                      "title":"View News"
                    },
                                 
                  ]
                },
                {
                  "title":news2,
                  "item_url":news2_url,
                  "image_url":image_url,
                  "subtitle":news2_description,
                  "buttons":[
                    {
                      "type":"web_url",
                      "url":news2_url,
                      "title":"View News"
                    },
                                 
                  ]
                },
                {
                  "title":news3,
                  "item_url":news3_url,
                  "image_url":image_url,
                  "subtitle":news3_description,
                  "buttons":[
                    {
                      "type":"web_url",
                      "url":news3_url,
                      "title":"View News"
                    },
                                 
                  ]
                },
              ]
            }
          }
        }

   
    }
  
  

  

  
  

  response_msg = json.dumps(response_msg)
  requests.post(post_message_url,headers={"Content-Type": "application/json"},data=response_msg)
  return

def set_menu():
    post_message_url = 'https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s'%PAGE_ACCESS_TOKEN
    
    response_object =   {
                          "setting_type" : "call_to_actions",
                          "thread_state" : "existing_thread",
                          "call_to_actions":[
                            {
                              "type":"postback",
                              "title":"HELP",
                              "payload":"MENU_HELP"
                            },
                            {
                              "type":"postback",
                              "title":"TOP NEWS",
                              "payload":"top_news"
                            },
                            
                          ]
                        }

    menu_object = json.dumps(response_object)
    status = requests.post(post_message_url,
          headers = {"Content-Type": "application/json"},
          data = menu_object)

    logg(status.text,'-MENU-OBJECT-')

def  handle_postback(fbid,payload):
  if not payload:
    return

  post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
  logg(payload,symbol='-QR-')
  response_msg = {"recipient":{"id":fbid}, "message":{"text":payload}}
  
  if payload=="MENU_HELP":
    output_text="To know about stocks, either type the symbol or name of the Stock"
    response_msg = {"recipient":{"id":fbid}, "message":{"text":output_text}}

  

  if payload=="top_news":
   
    image_url,news1,news1_url,news1_description,news2,news2_url,news2_description,news3,news3_url,news3_description= stock_news_top()
     
    logg("COrrect Answer",symbol='-YEhejnecmrS-')
    
    image_url=""
    response_msg= {

      "recipient":{
          "id":fbid
        },
        "message":{
          "attachment":{
            "type":"template",
            "payload":{
              "template_type":"generic",
              "elements":[
                {
                  "title":news1,
                  "item_url":news1_url,
                  "image_url":image_url,
                  "subtitle":news1_description,
                  "buttons":[
                    {
                      "type":"web_url",
                      "url":news1_url,
                      "title":"View News"
                    },
                                 
                  ]
                },
                {
                  "title":news2,
                  "item_url":news2_url,
                  "image_url":image_url,
                  "subtitle":news2_description,
                  "buttons":[
                    {
                      "type":"web_url",
                      "url":news2_url,
                      "title":"View News"
                    },
                                 
                  ]
                },
                {
                  "title":news3,
                  "item_url":news3_url,
                  "image_url":image_url,
                  "subtitle":news3_description,
                  "buttons":[
                    {
                      "type":"web_url",
                      "url":news3_url,
                      "title":"View News"
                    },
                                 
                  ]
                },
              ]
            }
          }
        }

   
    }
  response_msg = json.dumps(response_msg)
  requests.post(post_message_url,headers={"Content-Type": "application/json"},data=response_msg)
  return




class MyChatBotView(generic.View):
  def get (self, request, *args, **kwargs):
    if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
      return HttpResponse(self.request.GET['hub.challenge'])
    else:
      return HttpResponse('Oops invalid token')

  @method_decorator(csrf_exempt)
  def dispatch(self, request, *args, **kwargs):
    return generic.View.dispatch(self, request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    incoming_message= json.loads(self.request.body.decode('utf-8'))
    
    logg(incoming_message)

    for entry in incoming_message['entry']:
      for message in entry['messaging']:

        try:
          if 'postback' in message:
            handle_postback(message['sender']['id'],message['postback']['payload'])
            return HttpResponse()
          else: 
            pass
        except Exception as e:
          logg(e,symbol='-140-')

        try:
          if 'quick_reply' in message['message']:
            handle_quickreply(message['sender']['id'],
              message['message']['quick_reply']['payload'])
            return HttpResponse()
          else:
            pass
        except Exception as e:
          logg(e,symbol='-140-')
        
        try:
          sender_id = message['sender']['id']
          message_text = message['message']['text']
          post_facebook_message(sender_id,message_text) 
        except Exception as e:
          logg(e,symbol='-147-')

    return HttpResponse()
