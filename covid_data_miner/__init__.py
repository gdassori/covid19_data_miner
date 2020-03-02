import csv

d = '''
Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered
Hubei,Mainland China,2020-02-29T12:13:10,66337,2727,28993
,South Korea,2020-02-29T18:13:07,3150,16,27
Guangdong,Mainland China,2020-02-29T15:33:03,1349,7,983
Henan,Mainland China,2020-02-29T12:43:05,1272,21,1170
Zhejiang,Mainland China,2020-02-29T09:13:10,1205,1,1016
,Italy,2020-02-29T18:03:05,1128,29,46
Hunan,Mainland China,2020-02-29T15:33:03,1018,4,846
Anhui,Mainland China,2020-02-29T05:03:13,990,6,868
Jiangxi,Mainland China,2020-02-29T01:23:07,935,1,811
Shandong,Mainland China,2020-02-29T15:33:03,756,6,421
Diamond Princess cruise ship,Others,2020-02-29T01:43:02,705,6,10
Jiangsu,Mainland China,2020-02-29T07:23:11,631,0,523
,Iran,2020-02-29T14:53:04,593,43,123
Chongqing,Mainland China,2020-02-29T23:13:06,576,6,438
Sichuan,Mainland China,2020-02-29T12:03:07,538,3,351
Heilongjiang,Mainland China,2020-02-29T12:03:07,480,13,301
Beijing,Mainland China,2020-02-29T03:33:02,411,8,271
Shanghai,Mainland China,2020-02-29T06:23:03,337,3,287
Hebei,Mainland China,2020-02-29T15:33:03,318,6,282
Fujian,Mainland China,2020-02-29T15:33:03,296,1,243
Guangxi,Mainland China,2020-02-29T12:03:07,252,2,176
Shaanxi,Mainland China,2020-02-29T09:03:06,245,1,207
,Japan,2020-02-29T15:53:04,241,5,32
Yunnan,Mainland China,2020-02-29T05:03:13,174,2,157
Hainan,Mainland China,2020-02-29T23:43:02,168,5,148
Guizhou,Mainland China,2020-02-27T00:43:02,146,2,112
Tianjin,Mainland China,2020-02-29T12:03:07,136,3,109
Shanxi,Mainland China,2020-02-29T23:13:06,133,0,114
Liaoning,Mainland China,2020-02-29T15:33:03,121,1,96
,Singapore,2020-02-29T14:33:03,102,0,72
,France,2020-02-29T19:03:04,100,2,12
Hong Kong,Hong Kong,2020-02-29T23:53:02,95,2,33
Jilin,Mainland China,2020-02-29T09:13:10,93,1,75
Gansu,Mainland China,2020-02-28T02:33:02,91,2,82
,Germany,2020-02-29T14:43:03,79,0,16
Xinjiang,Mainland China,2020-02-29T12:03:07,76,3,62
Inner Mongolia,Mainland China,2020-02-29T09:03:06,75,0,49
Ningxia,Mainland China,2020-02-29T05:53:02,73,0,69
,Kuwait,2020-02-28T16:23:03,45,0,0
,Spain,2020-02-29T19:13:08,45,0,2
Unassigned Location (From Diamond Princess),US,2020-02-28T20:03:03,44,0,0
,Thailand,2020-02-29T12:33:03,42,0,28
,Bahrain,2020-02-29T18:03:05,41,0,0
Taiwan,Taiwan,2020-02-29T07:13:05,39,1,9
,Malaysia,2020-02-29T04:03:18,25,0,18
,UK,2020-02-29T18:03:05,23,0,8
,United Arab Emirates,2020-02-29T12:33:03,21,0,5
Qinghai,Mainland China,2020-02-21T04:43:02,18,0,18
,Switzerland,2020-02-29T18:03:05,18,0,0
,Vietnam,2020-02-25T08:53:02,16,0,16
,Norway,2020-02-29T23:13:06,15,0,0
,Iraq,2020-02-29T18:03:05,13,0,0
,Sweden,2020-02-29T14:43:03,12,0,0
"Toronto, ON",Canada,2020-02-29T23:23:13,10,0,2
Macau,Macau,2020-02-27T12:43:02,10,0,8
Queensland,Australia,2020-02-29T02:03:10,9,0,1
,Austria,2020-02-29T14:43:03,9,0,0
British Columbia,Canada,2020-02-29T23:23:13,8,0,3
Victoria,Australia,2020-02-29T02:03:10,7,0,4
,Israel,2020-02-29T01:53:03,7,0,1
,Croatia,2020-02-29T18:03:05,6,0,0
,Netherlands,2020-02-29T18:03:05,6,0,0
,Oman,2020-02-29T12:33:03,6,0,1
"Seattle, WA",US,2020-02-29T22:33:03,6,1,1
New South Wales,Australia,2020-02-13T17:53:03,4,0,4
,Greece,2020-02-28T15:33:03,4,0,0
,Lebanon,2020-02-29T01:53:03,4,0,0
,Mexico,2020-02-29T21:13:17,4,0,0
,Pakistan,2020-02-29T18:03:05,4,0,0
South Australia,Australia,2020-02-29T02:03:10,3,0,2
,Denmark,2020-02-29T18:03:05,3,0,0
,Finland,2020-02-29T05:23:03,3,0,1
,India,2020-02-16T07:43:02,3,0,3
,Philippines,2020-02-12T07:43:02,3,1,1
,Romania,2020-02-28T15:33:03,3,0,0
"Santa Clara, CA",US,2020-02-29T01:33:03,3,0,1
Western Australia,Australia,2020-02-29T23:13:06,2,0,0
,Brazil,2020-02-29T21:03:05,2,0,0
,Russia,2020-02-12T14:43:03,2,0,2
"Chicago, IL",US,2020-02-09T19:03:03,2,0,2
"Sacramento County, CA",US,2020-02-27T20:33:02,2,0,0
"San Benito, CA",US,2020-02-03T03:53:02,2,0,0
"San Diego County, CA",US,2020-02-21T05:43:02,2,0,1
,Afghanistan,2020-02-24T23:33:02,1,0,0
,Algeria,2020-02-25T23:43:03,1,0,0
,Belarus,2020-02-28T16:23:03,1,0,0
,Belgium,2020-02-17T04:23:06,1,0,1
,Cambodia,2020-02-12T07:43:02,1,0,1
" Montreal, QC",Canada,2020-02-28T05:23:07,1,0,0
"London, ON",Canada,2020-02-12T18:53:03,1,0,1
,Egypt,2020-02-28T04:13:09,1,0,1
,Estonia,2020-02-27T16:23:03,1,0,0
,Georgia,2020-02-27T16:23:03,1,0,0
,Iceland,2020-02-29T00:33:01,1,0,0
,Ireland,2020-02-29T22:33:03,1,0,0
,Lithuania,2020-02-28T16:23:03,1,0,0
,Luxembourg,2020-02-29T21:03:05,1,0,0
Tibet,Mainland China,2020-02-12T06:43:02,1,0,1
,Monaco,2020-02-29T00:33:01,1,0,0
,Nepal,2020-02-12T14:43:03,1,0,1
,New Zealand,2020-02-28T16:23:03,1,0,0
,Nigeria,2020-02-28T16:23:03,1,0,0
,North Macedonia,2020-02-27T16:23:03,1,0,0
,Qatar,2020-02-29T14:33:03,1,0,0
,San Marino,2020-02-27T21:13:10,1,0,0
,Sri Lanka,2020-02-08T03:43:03,1,0,1
"Boston, MA",US,2020-02-28T21:13:12,1,0,1
"Humboldt County, CA",US,2020-02-21T05:13:09,1,0,0
"Los Angeles, CA",US,2020-02-01T19:53:03,1,0,0
"Madison, WI",US,2020-02-05T21:53:02,1,0,0
"Orange, CA",US,2020-02-01T19:53:03,1,0,0
"Portland, OR",US,2020-02-29T02:23:11,1,0,0
"San Antonio, TX",US,2020-02-13T18:53:02,1,0,0
"Snohomish County, WA",US,2020-02-29T15:03:04,1,0,0
"Tempe, AZ",US,2020-02-25T21:23:03,1,0,1
From Diamond Princess,Australia,2020-02-29T02:03:10,0,0,0
"Lackland, TX (From Diamond Princess)",US,2020-02-24T23:33:02,0,0,0
"Omaha, NE (From Diamond Princess)",US,2020-02-24T23:33:02,0,0,0
"Travis, CA (From Diamond Princess)",US,2020-02-24T23:33:02,0,0,0
'''

c = csv.reader(d)
print(c)
