import requests
import json


host = "http://api.jjdashi.com"
all_scenics_url = "/scenics/search?partner_id=118&categroy=&query="
scenic_spot_url = "/scenic_spot/find"


def get_all_scenics():
    ret = requests.get(host + all_scenics_url).json()
    with open('scenics.json', mode='w+', encoding='utf-8') as target:
        target.write(json.dumps(ret, ensure_ascii=False))
    return ret


def get_scenic_spot(scenic_id):
    ret = requests.get(host + scenic_spot_url,
                       params={'scenic_id': scenic_id}).json()['body']['scenic_spot']
    with open('spot.json', mode='w+', encoding='utf-8') as target:
        target.write(json.dumps(ret, ensure_ascii=False))
    return ret


def main():

    scenics = get_all_scenics()
    with open('resutl.csv', mode='w+', encoding='utf-8') as fp:
        fp.write('景区名,类型,讲解时间,景区等级,销量,讲解人员,售价\n')
        for index, scenic in enumerate(scenics):
            scenic_id = scenic['id']
            scenic_name = scenic['name']
            print(str(index) + "  " + scenic_name)
            categroy_name = scenic['categroy_name'].replace(',', '，')
            duration = str(scenic['duration']) + "分钟"
            level = scenic['level']

            detail = get_scenic_spot(scenic_id)
            all_order_count = detail.get('total_use_times', 0)
            docents = ""
            for docent in detail.get('price_list', []):
                docent_name = docent.get('name', '')
                desc = docent.get('descn', '').replace(
                    '\r', '').replace('\n', '').replace(',', '，').strip()
                if not desc:
                    desc = docent_name
                price = docent.get('total_fee', 0) / 100
                docents += "{},{},".format(desc, price)

            fp.write("{},{},{},{},{},{}\n".format(
                scenic_name, categroy_name, duration, level, all_order_count, docents[:-1]
            ))


if __name__ == '__main__':
    main()
