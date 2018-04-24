# coding : utf-8
# created by wyj
import numpy as np
import pandas as pd
import math
from utils.feature_utils import df_empty

def build_time_features(data):
    # train_addtime = train
    # test_addtime = test
    data['TIME_year'] = data['TIME'].dt.year
    data['TIME_month'] = data['TIME'].dt.month
    data['TIME_day'] = data['TIME'].dt.day
    data['TIME_weekofyear'] = data['TIME'].dt.weekofyear
    data['TIME_hour'] = data['TIME'].dt.hour
    data['TIME_minute'] = data['TIME'].dt.minute
    data['TIME_weekday'] = data['TIME'].dt.weekday
    data['TIME_is_weekend'] = data['TIME_weekday'].map(lambda d: 1 if (d == 0) | (d == 6)else 0)
    data['TIME_week_hour'] = data['TIME_weekday'] * 24 + data['TIME_hour']

    # 取单独的一个用户组进行综合提取
    # TERMINALNO, TIME, TRIP_ID, LONGITUDE, LATITUDE, DIRECTION, HEIGHT, SPEED, CALLSTATE

    train_user = data['TERMINALNO'].unique()
    train_data=pd.DataFrame(columns=['TERMINALNO', 'maxTime', 'phonerisk', 'dir_risk', 'height_risk', 'speed_max',
                           'speed_mean', 'height_mean', 'Zao', 'Wan', 'Sheye','time_weekend',"height_down"],index=train_user)

    for TERMINALNO in train_user:
        user_data = data.loc[data['TERMINALNO'] == TERMINALNO]
        # 初始化 时间，方向变化
        tempTime = data["TIME_STAMP"].iloc[0]
        tempSpeed = data["SPEED"].iloc[0]
        tempdir = data["DIRECTION"].iloc[0]
        tempheight = data["HEIGHT"].iloc[0]
        # 根据时间信息判断最长时间
        maxTime = 0
        maxTimelist = []
        # 用户行驶过程中，打电话危机上升
        phonerisk = 0
        # Direction 突变超过
        dir_risk = 0
        dir_risklist=[]
        # Height 高度的危险值
        height_risk = 0
        height_risklist=[]

        #基于实时速度而不是速度的变化率的危险系数

        height_speed=0
        height_speedlist=[]
        # 时间区间
        Zao = 0
        Wan = 0
        Sheye =0
        other=0
        #下坡
        sumh=0
        height=99999
        height_sumlist=[]
        for index, row in user_data.iterrows():

            p_time = row['TIME_hour']
            if 6 <= p_time <= 9:
                Zao = 1
            elif 17 <= p_time <= 19:
                Wan = 1
            elif 0 <= p_time < 6:
                Sheye = 1


            # 如果具有速度，且在打电话
            if tempSpeed > 0 and row["CALLSTATE"] != 4:

                # 人设打电话状态未知情况下，他的危机指数为 0.05
                if row["CALLSTATE"] == 0:
                    phonerisk += math.exp(tempSpeed / 10) * 0.02
                else:
                    phonerisk += math.exp(tempSpeed / 10)

            # # 根据时间行驶判断
            if row["TIME_STAMP"] - tempTime == 60:

                sumh += row['HEIGHT'] - tempheight
                if sumh < height:
                    height = sumh
                if sumh > 0:
                    sumh = 0

                maxTime += 60
                tempTime = row["TIME_STAMP"]

                # 判断方向变化程度与具有车速之间的危险系数
                dir_change = (min(abs(row["DIRECTION"] - tempdir), abs(360 + tempdir - row["DIRECTION"])) / 90.0)
                if tempSpeed != 0 and row["SPEED"] > 0:
                    dir_risk += math.pow((row["SPEED"] / 10), dir_change)

                # 海拔变化大的情况下和速度的危险系数
                height_risk += math.pow(abs(row["SPEED"] - tempSpeed) / 10, (abs(row["HEIGHT"] - tempheight) / 100))
                height_speed+=math.pow(row['SPEED'],(abs(row["HEIGHT"] - tempheight) / 100))
                tempdir = row["DIRECTION"]
                tempSpeed = row["SPEED"]
                tempheight = row["HEIGHT"]

            elif row["TIME_STAMP"] - tempTime > 60:
                height_sumlist.append(height)
                height=99999
                sumh=0

                dir_risklist.append(dir_risk)
                dir_risk=0

                height_risklist.append(height_risk)
                height_risk=0

                height_speedlist.append(height_speed)
                height_speed=0

                maxTimelist.append(maxTime)
                maxTime = 0

                tempTime = row["TIME_STAMP"]

                tempdir = row["DIRECTION"]
                tempheight = row["HEIGHT"]
                tempSpeed = row["SPEED"]

        speed_max = user_data["SPEED"].max()
        speed_mean = user_data["SPEED"].mean()

        time_weekend=user_data['TIME_is_weekend'].mean()

        height_mean = user_data["HEIGHT"].mean()

        maxTimelist.append(maxTime)
        maxTime = max(maxTimelist)

        height_sumlist.append(height)
        height = sum(height_sumlist)/len(height_sumlist)

        dir_risklist.append(dir_risk)
        dir_risk = sum(dir_risklist)/len(dir_risklist)

        height_risklist.append(height_risk)
        height_risk = sum(height_risklist)/len(height_risklist)

        height_speedlist.append(height_speed)
        height_speed = sum(height_speedlist)/len(height_speedlist)
        #早中晚的占比


        train_data.loc[TERMINALNO] = [TERMINALNO, maxTime, phonerisk, dir_risk, height_speed,speed_max, speed_mean, height_mean,
                                Zao,
                                Wan, Sheye,time_weekend,height]
    train_data=train_data.astype(float)
    train_data[['TERMINALNO']]=train_data[['TERMINALNO']].astype(int)

    train_data.set_index('TERMINALNO', inplace=True,drop=True)
    # TERMINALNO, TIME, TRIP_ID, LONGITUDE, LATITUDE, DIRECTION, HEIGHT, SPEED, CALLSTATE


    return train_data






    #
    # test_addtime['TIME_is_weekend'] = test_addtime['TIME_weekday'].map(lambda d: 1 if (d == 0) | (d == 6)else 0)
    # test_addtime['TIME_week_hour'] = test_addtime['TIME_weekday'] * 24 + test_addtime['TIME_hour']
    #
    # train_weekend=train_addtime[['TERMINALNO','TRIP_ID','TIME_is_weekend']].groupby(['TERMINALNO', 'TRIP_ID'],
    #                                                            as_index=False).agg(lambda x: np.mean(pd.Series.mode(x)))
    # train_weekend=train_weekend[['TERMINALNO','TIME_is_weekend']].groupby(['TERMINALNO'],
    #                                                            as_index=True).mean()
    # test_weekend = test_addtime[['TERMINALNO', 'TRIP_ID', 'TIME_is_weekend']].groupby(['TERMINALNO', 'TRIP_ID'],
    #                                                                                     as_index=False).agg(
    #     lambda x: np.mean(pd.Series.mode(x)))
    # test_weekend = test_weekend[['TERMINALNO', 'TIME_is_weekend']].groupby(['TERMINALNO'],
    #                                                                          as_index=True).mean()
    #
    #
    # return train_weekend,test_weekend
