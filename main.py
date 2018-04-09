# -*- coding:utf-8 -*-

from train_model.xgboost_model import model_train
from conf.configure import Configure
from functions.functions import save_all_features
from input.read_data import read_data
import time

if __name__ == "__main__":
    print("******* start at:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '*******')
    # 程序入口
    trainSet, testSet = read_data(Configure.train_path, Configure.test_path)

    save_all_features(trainSet, testSet)

    model_train(trainSet, testSet)

    print("******* end at:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '*******')
