# coding: UTF-8

import sys

from hyperopt import fmin, tpe

from src import logger
from src.mex import BitMex
from src.mex_stub import BitMexStub
from src.mex_test import BitMexTest


class Bot:
    # パラメータ
    params = {}
    # 取引所
    exchange = None
    # 時間足
    tr = '1h'
    # 足の期間
    periods = 20
    # テストネットを利用するか
    test_net = False
    # バックテストか
    back_test = False
    # スタブ取引か
    stub_test = False
    # パラメータ探索か
    hyperopt = False

    def __init__(self, tr):
        """
        コンストラクタ。
        :param tr: 時間足
        :param periods: 期間
        """
        self.tr = tr

    def options(self):
        """
        パレメータ探索用の値を取得する関数。
        """
        pass

    def input(self, title, type, defval):
        """
        パレメータを取得する関数。
        :param title: パレメータ名
        :param defval: デフォルト値
        :return: 値
        """
        p = {} if self.params is None else self.params
        if title in p:
            return type(p[title])
        else:
            return defval

    def strategy(self, open, close, high, low):
        """
        戦略関数。Botを作成する際は、この関数を継承して実装してください。
        :param open: 始値
        :param close: 終値
        :param high: 高値
        :param low: 安値
        """
        pass

    def params_search(self):
        """
 ˜      パラメータ検索を行う関数。
        """
        def objective(args):
            self.params = args
            self.exchange = BitMexTest(self.tr)
            self.exchange.on_update(self.strategy)
            return self.exchange.lose_loss/self.exchange.win_profit

        best_params = fmin(objective, self.options(), algo=tpe.suggest, max_evals=100)
        logger.info(f"Best params is {best_params}")

    def run(self):
        """
˜       Botを起動する関数。
        """
        if self.hyperopt:
            self.params_search()
            return

        elif self.stub_test:
            self.exchange = BitMexStub(self.tr)
        elif self.back_test:
            self.exchange = BitMexTest(self.tr)
        else:
            self.exchange = BitMex(self.tr, demo=self.test_net)

        logger.info(f"Starting Bot")
        logger.info(f"Strategy : {type(self).__name__}")

        self.exchange.on_update(self.strategy)
        self.exchange.show_result()

    def stop(self):
        """
˜       Botを停止する関数。Openしている注文は、キャンセルする。
        """
        if self.exchange is None:
            return

        logger.info(f"Stopping Bot")

        self.exchange.stop()
        self.exchange.cancel_all()
        sys.exit()
