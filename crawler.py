# -*- coding: utf-8 -*-
import time
import datetime
import urllib2
import base64
import hmac
import hashlib
import json
import requests
import xmltodict
from time import sleep
import types

# API ID, KEY
## Amazon (PAAPI)
AWS_ACCESS_KEY_ID = 'AKIAJP5XVIKHEQMB5XWA'
AWS_SECRET_KEY = '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'
ASSOCIATE_TAG = 'powerzport-22'
ENDPOINT = 'webservices.amazon.co.jp'
REQUEST_URI = '/onca/xml'

# DBディレクトリ
## Amazonディレクトリ
AMA_DB_ROOT_PATH = './db/amazon/'
## 楽天ディレクトリ
RAK_DB_ROOT_PATH = './db/rakuten/'

# Amazonカテゴリリスト
AMA_CATEGORYLIST_PATH = './amazon_list.json'

# HTTPアクセススリープ(s)
HTTP_ACCESS_SLEEP = 2

# HTTPタイムアウト
HTTP_TIMEOUT = 2


def main():
    # Amazon Crawler
    amazonCrawler()
    

def amazonCrawler():
    # カテゴリリスト読込
    amazon_category = readCategoryList(AMA_CATEGORYLIST_PATH)

    # カテゴリを1つずつ処理
    for key in amazon_category:
        print "get : " + amazon_category[key]["name"]

        # browsenode(TopSeller10位まで)取得するパラメータ
        params = {
            "Service":"AWSECommerceService",
            "Operation":"BrowseNodeLookup",
            "AWSAccessKeyId":"AKIAJP5XVIKHEQMB5XWA",
            "AssociateTag":str(ASSOCIATE_TAG),
            "BrowseNodeId":str(amazon_category[key]["number"]),
            "ResponseGroup":"BrowseNodeInfo,TopSellers"
        }

        # URLを作成
        requestURL = amazonMakeURL(params)
        
        # XMLを取得 --> dict型に変換
        lookup = getDictData(requestURL)

        topseller = lookup["BrowseNodeLookupResponse"]["BrowseNodes"]["BrowseNode"]["TopSellers"]["TopSeller"]
        #print requestURL
        for i, tp in enumerate(topseller):
            print i, tp["Title"]



# カテゴリリスト(CategoryID, Name, Number)の読込(JSON)
def readCategoryList(filepath):
    file = open(filepath, 'r')
    json_dict = json.load(file)
    file.close()
    return json_dict


# Amazon(PAAPI) make URL
def amazonMakeURL(params):
    # Set current timestamp if not set
    if (("Timestamp" in params) is False):
        params["Timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Sort the parameters by key
    params = sorted(params.items())

    pairs = []

    for param in params:
        pairs.append(urllib2.quote(str(param[0])) + "=" + urllib2.quote(str(param[1])))

    # Generate the canonical query
    canonical_query_string = "&".join(pairs)
    
    # Generate the string to be signed
    string_to_sign = "GET\n" + str(ENDPOINT) + "\n" + str(REQUEST_URI) + "\n" + str(canonical_query_string)

    # Generate the signature required by the Product Advertising API
    signature = base64.b64encode(hmac.new(AWS_SECRET_KEY, string_to_sign, hashlib.sha256).digest())

    request_url = 'http://' + str(ENDPOINT) + str(REQUEST_URI) + '?' + str(canonical_query_string) + '&Signature=' + urllib2.quote(signature)

    # Generate the signed URL
    return str(request_url)


# APIを投げてXMLを取得後、dict型に変換
def getDictData(URL):
    while True:
        sleep(HTTP_ACCESS_SLEEP)
        xml_data = requests.get(URL, timeout=HTTP_TIMEOUT)
        # HTTP: 503の場合は、もう一度時間を開けて実行する
        if xml_data.status_code != 503:
            dict_data = xmltodict.parse(xml_data.text)
            break
    return dict_data


if __name__=='__main__':
    main()