from multiprocessing.dummy import Pool
import requests


def frange(x, y, step):
    while x < y:
        yield x
        x += step


def get_location():
    for lng in frange(73, 135, 0.001):
        for lat in frange(4, 53, 0.001):
            yield (lng, lat)


def locate(lng, lat):
    url = "https://restapi.amap.com/v3/geocode/regeo?key=f3288ae97e6adaa02555e5ebf5b32fde&location={0},{1}".format(
        lng, lat)
    try:
        ret = requests.get(url, timeout=5)
    except requests.exceptions.Timeout as e:
        print("请求超时")
    if ret.status_code != 200:
        print("返回信息错误：" + ret.json())
    print(ret.json())


def main():
    pool = Pool()
    pool.map(locate, get_location())
    pool.start()
    pool.join()
    # for lng in frange(73, 135, 0.001):
    #     for lat in frange(4, 53, 0.001):
    #         locate(lng, lat)


if __name__ == '__main__':
    main()
