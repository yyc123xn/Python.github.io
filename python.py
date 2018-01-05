import requests
import bs4
import re
import time
import pymysql

from selenium import webdriver

con = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    db="websites",
    port=3306,
    use_unicode=True,
    charset="utf8"
)
cursor = con.cursor()

driver = webdriver.Chrome()

city = ''
cityUrl = ''

#上海 https://zh.airbnb.com/s/Shanghai--China?cdn_cn=1&s_tag=ejxIlhR7&allow_override%5B%5D=&section_offset={}
#北京 https://zh.airbnb.com/s/Beijing--China?cdn_cn=1&s_tag=kN1Hdq18&allow_override%5B%5D=&section_offset={}
#成都 https://zh.airbnb.com/s/Chengdu-Shi?cdn_cn=1&s_tag=DV8jh0yp&allow_override%5B%5D=&section_offset={}
for j in range(0,3,1):
    if j == 2:
        city = 'Shanghai'
        cityUrl = 'Shanghai--China?cdn_cn=1&s_tag=ejxIlhR7'
    if j == 1:
        city = 'Beijing'
        cityUrl = 'Beijing--China?cdn_cn=1&s_tag=kN1Hdq18'
    if j == 0:
        city = 'Chengdu'
        cityUrl = 'Chengdu-Shi?cdn_cn=1&s_tag=DV8jh0yp'

    #爬取数据

    for i in range(0, 17 , 1):

        url = ('https://zh.airbnb.com/s/'+cityUrl+'&allow_override%5B%5D=&section_offset={}').format(
            str(i))

        if i == 0:
            url = 'https://zh.airbnb.com/s/'+cityUrl+'&allow_override%5B%5D='

        driver.get(url)
        # print(i)
        #if i == 1270:
        #   elements = driver.find_elements_by_class_name('mod-1')
        #  for element in elements:
        #     element.click()

        time.sleep(2)
        html = driver.page_source#获取网页的html数据、
        soup = bs4.BeautifulSoup(html,'lxml')#对html进行解析
        r = soup.find_all('div', class_='_v72lrv')

        for tag in r:

            url = 'https://zh.airbnb.com/'+str(tag.find('a',class_="_j4ns53m").get('href'))
            title = str(tag.find('div',class_="_ew0cqip").text)
            priceContent = tag.find('span',class_="_hylizj6")
            priceTmp = priceContent.find_all('span')[2].text
            price = priceTmp[1:].replace(',', '')

            # price = str(priceContent.find('span').text)
            type = str(tag.find('small',class_='_5y5o80m').text)

            if tag.find('span',class_='_gb7fydm'):
                comments = tag.find('span',class_='_gb7fydm').text
            else:
                comments = 'NEW'

            if tag.find('span',class_='_1uyixqdu'):
                scoreTmp = tag.find('span',class_='_1uyixqdu')
                print(scoreTmp)
                score = scoreTmp.find_all('span')[0].get('aria-label').replace('评分是', '').replace('（满分为5）', '')
            else:
                score = '0'

            print(url)
            print(title)
            print(price)
            print(type)
            print(comments)
            print(score)
            print("\n")

            sql = "INSERT INTO Airbnb_" + city + "(url,price,type,comments,score) values('" \
                  + url + "','" + price + "','" + type + "','" + comments + "','" + score + "')"
            print(sql)
            cursor.execute(sql)
            con.commit()

            sql = "UPDATE Airbnb_"+city+" " \
                  "SET title = '"+title.replace("'", '').replace('"', '')+"' " \
                  "WHERE title = '0'"
            print(sql)
            cursor.execute(sql)
            con.commit()

# 图标展示

import plotly
plotly.tools.set_credentials_file(username='yyc', api_key='1puNznRHHWs5kPei8ESP')

import plotly.plotly as py
from plotly.graph_objs import *


city = ''
trace0 = ''
trace1 = ''
trace2 = ''

#每个城市图表
for i in range(0,3,1):
    if i == 2:
        city = 'Shanghai'
    if i == 1:
        city = 'Beijing'
    if i == 0:
        city = 'Chengdu'

    sql = "SELECT type,AVG(price) FROM Airbnb_"+city+" GROUP BY type"

    cursor.execute(sql)
    result = cursor.fetchall()
    print(result)

    roomType=[]
    price=[]

    for field in result:
        roomType.append(field[0])
        price.append(int(field[1]))

    if i == 2:
        Shanghai = Scatter(
            x=roomType,
            y=price,
            name='Shanghai'
        )
    if i == 1:
        Beijing = Scatter(
            x=roomType,
            y=price,
            name='Beijing'
        )
    if i == 0:
        Chengdu = Scatter(
            x=roomType,
            y=price,
            name='Chengdu'
        )


    print(roomType)
    print(price)

data = Data([Shanghai])

py.plot(data, filename = 'Shanghai')

data = Data([Beijing])

py.plot(data, filename = 'Beijing')

data = Data([Chengdu])

py.plot(data, filename = 'Chengdu')

#每个城市平均
for i in range(0,3,1):
    if i == 2:
        city = 'Shanghai'
    if i == 1:
        city = 'Beijing'
    if i == 0:
        city = 'Chengdu'

    sql = "SELECT AVG(price) FROM Airbnb_"+city+" "

    cursor.execute(sql)
    result = cursor.fetchall()
    print(result)

    price=int(result[0][0])

    print(price)

    if i == 2:
        Shanghai = Scatter(
            x="Shanghai",
            y=price,
            name='Shanghai'
        )
    if i == 1:
        Beijing = Scatter(
            x="Beijing",
            y=price,
            name='Beijing'
        )
    if i == 0:
        Chengdu = Scatter(
            x="Chengdu",
            y=price,
            name='Chengdu'
        )

data = Data([Chengdu,Shanghai,Beijing])

py.plot(data, filename = 'avg')

#每个城市比较
sql = "SELECT Airbnb_Shanghai.type,AVG(Airbnb_Shanghai.price),AVG(Airbnb_Chengdu.price),AVG(Airbnb_Beijing.price) FROM Airbnb_Shanghai " \
      "JOIN Airbnb_Chengdu ON Airbnb_Shanghai.type = Airbnb_Chengdu.type " \
      "JOIN Airbnb_Beijing ON Airbnb_Shanghai.type = Airbnb_Beijing.type " \
      "GROUP BY type"

cursor.execute(sql)
result = cursor.fetchall()
print(result)
roomType=[]
shanghaiPrice=[]
ChengduPrice=[]
BeijingPrice=[]

for field in result:
    roomType.append(field[0])
    shanghaiPrice.append(int(field[1]))
    ChengduPrice.append(int(field[2]))
    BeijingPrice.append(int(field[3]))


Shanghai = Scatter(
    x=roomType,
    y=shanghaiPrice,
    name='Shanghai'
)

Chengdu = Scatter(
    x=roomType,
    y=ChengduPrice,
    name='Chengdu'
)

Beijing = Scatter(
    x=roomType,
    y=BeijingPrice,
    name='Beijing'
)

print(roomType)
print(shanghaiPrice)
print(ChengduPrice)
print(BeijingPrice)

data = Data([Chengdu,Shanghai,Beijing])

py.plot(data, filename = 'compare')

city = ''
y1 = ''
y2 = ''
y3 = ''
#分数比较
for i in range(0,3,1):
    if i == 2:
        city = 'Shanghai'
    if i == 1:
        city = 'Beijing'
    if i == 0:
        city = 'Chengdu'

    sql = " SELECT (SELECT COUNT(*) FROM airbnb_"+city+" AS "+city+" WHERE "+city+".score = 3) AS '3' ," \
				"IFNULL((SELECT AVG(price) FROM airbnb_"+city+" AS "+city+" WHERE "+city+".score = 3),0) AS '3Price' ," \
				"(SELECT COUNT(*) FROM airbnb_"+city+" AS "+city+" WHERE "+city+".score = 4) AS '4' ," \
				"IFNULL((SELECT AVG(price) FROM airbnb_"+city+" AS "+city+" WHERE "+city+".score = 4),0) AS '4Price' ," \
				"(SELECT COUNT(*) FROM airbnb_"+city+" AS "+city+" WHERE "+city+".score = 4.5) AS '4.5' ," \
				"IFNULL((SELECT AVG(price) FROM airbnb_"+city+" AS "+city+" WHERE "+city+".score = 4.5),0) AS '4.5Price' ," \
				"(SELECT COUNT(*) FROM airbnb_"+city+" AS "+city+" WHERE "+city+".score = 5) AS '5' ," \
				"IFNULL((SELECT AVG(price) FROM airbnb_"+city+" AS "+city+" WHERE "+city+".score = 5),0) AS '5Price' " \
            "FROM airbnb_"+city+" LIMIT 1 "

    cursor.execute(sql)
    result = cursor.fetchall()
    print(result)

    price=[int(result[0][1]),int(result[0][3]),int(result[0][5]),int(result[0][7])]
    num=[int(result[0][0]),int(result[0][2]),int(result[0][4]),int(result[0][6])]

    print(price)

    if i == 2:
        Shanghai = Scatter(
            x=['3','4','4.5','5'],
            y=price,
            name='Shanghai'
        )
        y1 = num
    if i == 1:
        Beijing = Scatter(
            x=['3', '4', '4.5', '5'],
            y=price,
            name='Beijing'
        )
        y2 = num
    if i == 0:
        Chengdu = Scatter(
            x=['3', '4', '4.5', '5'],
            y=price,
            name='Chengdu'
        )
        y3 = num


data = Data([Chengdu,Shanghai,Beijing])

py.plot(data, filename = 'score')

#各个评分段的房屋个数
dataset = {'x': ['3', '4', '4.5', '5'],
           'y1': y1,
           'y2': y2,
           'y3': y3}

# 计算y1,y2,y3的堆叠占比
dataset['y1_stack'] = dataset['y1']
dataset['y2_stack'] = [y1 + y2 for y1, y2 in zip(dataset['y1'], dataset['y2'])]
dataset['y3_stack'] = [y1 + y2 + y3 for y1, y2, y3 in zip(dataset['y1'], dataset['y2'], dataset['y3'])]

dataset['y1_text'] = ['%s(%s%%)' % (y1, y1 * 100 / y3_s) for y1, y3_s in zip(dataset['y1'], dataset['y3_stack'])]
dataset['y2_text'] = ['%s(%s%%)' % (y2, y2 * 100 / y3_s) for y2, y3_s in zip(dataset['y2'], dataset['y3_stack'])]
dataset['y3_text'] = ['%s(%s%%)' % (y3, y3 * 100 / y3_s) for y3, y3_s in zip(dataset['y3'], dataset['y3_stack'])]

data_g = []
tr_1 = Scatter(
    x=dataset['x'],
    y=dataset['y1_stack'],
    text=dataset['y1_text'],
    hoverinfo='x+text',
    mode='lines',
    name='Shanghai',
    fill='tozeroy'  # 填充方式: 到x轴
)
data_g.append(tr_1)

tr_2 = Scatter(
    x=dataset['x'],
    y=dataset['y2_stack'],
    text=dataset['y2_text'],
    hoverinfo='x+text',
    mode='lines',
    name='Beijing',
    fill='tonexty'  # 填充方式:到下方的另一条线
)
data_g.append(tr_2)

tr_3 = Scatter(
    x=dataset['x'],
    y=dataset['y3_stack'],
    text=dataset['y3_text'],
    hoverinfo='x+text',
    mode='lines',
    name='Chengdu',
    fill='tonexty'
)
data_g.append(tr_3)

layout = Layout(title="field area plots", xaxis={'title': 'x'}, yaxis={'title': 'value'})
fig = Figure(data=data_g, layout=layout)
py.plot(fig, filename="pie")
