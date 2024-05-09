import sqlite3
import json

conn = sqlite3.connect("button.db")
cur = conn.cursor()
conn.execute('''CREATE TABLE IF NOT EXISTS button
             (id INTEGER PRIMARY KEY, question TEXT, response TEXT, image TEXT, type int)''')

sample_questions = [
    {
        "question": "start", 
        "index": 1,
        "response": {
            "text": [
                "시동 및 도어",
                "장치",
                "주유/충전",
                "직접입력"
                ],
            "image": [],
            "type": 0,
        }
    },
    {
        "question": "시동 및 도어", 
        "index": 1,
        "response": {
            "text": [
                "시동버튼 위치",
                "스마트키 원격시동",
                "차 밖에서 문열기",
                "차 안에서 문열기"
                ],
            "image": [],
            "type": 0,
        }
    },
    {
        "question": "시동버튼 위치", 
        "index": 2,
        "response": {
            "text": [
                '시동버튼은 여기 있습니다',
                ],
            "image": [
                'https://mblogthumb-phinf.pstatic.net/MjAxODA0MTZfNTAg/MDAxNTIzODY3ODcyMzI5.IqNbzCXP56JI5G1cF3YpnqLn2lrbokipOq3Hdnac4T8g.tNVb_rGeukIDA46b-_cNvkaAI9Ut1UacE_b5OMR7Sokg.PNG.0323lena/image_5131097701523867771893.png?type=w800'
                ],
            "type": 1,
        }
    },
    {
        "question": "스마트키 원격시동", 
        "index": 3,
        "response": {
            "text": [
                '스마트키 원격시동은 이렇게 하십쇼'
                ],
            "image": [
                'https://i.ytimg.com/vi/fImEZifLV9U/maxresdefault.jpg'
                ],
            "type": 1,
        }
    },
    {
        "question": "차 밖에서 문열기", 
        "index": 4,
        "response": {
            "text": [
                '차 밖에서 문열기는 요러케'
                ],
            "image": [
                'https://mblogthumb-phinf.pstatic.net/MjAyMzA0MTJfNCAg/MDAxNjgxMjc5OTEwMTkx.I2hdGumdsJlugAhkRm5WVGFhYnHOw0G-uDI2fXr90aQg.W8Bf8KL6gcHf_96ZAtXmLekQcdqvP88ee0Rd4PgweyUg.JPEG.cyg0703nani/IMG_7052.jpg?type=w800'
                ],
            "type": 1,
        }
    },
    {
        "question": "차 안에서 문열기", 
        "index": 5,
        "response": {
            "text": [
                '차 안에서 문열기는 요러케'
                ],
            "image": [
                'https://i.ytimg.com/vi/kxslSjObGD8/maxresdefault.jpg'
                ],
            "type": 1,
        }
    },
    {
        "question": "장치", 
        "index": 6,
        "response": {
            "text": [
                "후면 트렁크 열고닫기",
                "전면 트렁크 열고닫기",
                "변속기 조절하기"
                ],
            "image": [],
            "type": 0,
        }
    },
    {
        "question": "후면 트렁크 열고닫기", 
        "index": 7,
        "response": {
            "text": [
                '후면 트렁크 열기 버튼을 누르고 위로 올리면 열려요',
                ],
            "image": [
                'https://www.tesla.com/ownersmanual/images/GUID-0C9CE425-C8ED-4ACB-8178-94BB7CF46C3E-online-en-US.png'
                ],
            "type": 1,
        }
    },
    {
        "question": "전면 트렁크 열고닫기", 
        "index": 8,
        "response": {
            "text": [
                '전면 트렁크 열기 버튼을 누르고 위로 올리면 열려요'
                ],
            "image": [
                'https://www.tesla.com/ownersmanual/images/GUID-64C680DF-1B33-4182-9D23-E0E33CBAF8BB-online-en-US.png'
                ],
            "type": 1,
        }
    },
    {
        "question": "변속기 조절하기", 
        "index": 9,
        "response": {
            "text": [
                '변속기 다이얼 돌리세요'
                ],
            "image": [
                'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSbqUmq4ZVKPhtDzcEG1US0OHDdYN2lwrFQT95txr21A&s'
                ],
            "type": 1,
        }
    },
    {
        "question": "주유/충전", 
        "index": 10,
        "response": {
            "text": [
                "충전 도어 열고 닫기",
                "충전방법",
                ],
            "image": [],
            "type": 0,
        }
    },
    {
        "question": "충전 도어 열고 닫기", 
        "index": 11,
        "response": {
            "text": [
                '번호판 옆 등같은거 불쑥 튀어나온거 있음'
                ],
            "image": [
                'https://image.edaily.co.kr/images/Photo/files/NP/S/2021/03/PS21031900347.jpg'
                ],
            "type": 1,
        }
    },
    {
        "question": "충전방법", 
        "index": 12,
        "response": {
            "text": [
                '충전단자에 충전기 연결하자'
                ],
            "image": [
                'https://image.kmib.co.kr/online_image/2022/1111/2022111115563193052_1668149791_0017662886.jpg'
                ],
            "type": 1,
        }
    },
    {
        "question": "직접입력", 
        "index": 999,
        "response": {
            "text": [],
            "image": [],
            "type": 2,
        }
    },

]

for i in sample_questions:
    response = i["response"]["text"]
    image = i["response"]["image"]
    button_type = i["response"]["type"]
    question = i["question"]

    response = json.dumps(response)
    image = json.dumps(image)

    cur.execute('''INSERT INTO button (question, response, image, type) VALUES (?, ?, ?, ?)''',
                (question, response, image, button_type))
    conn.commit()
conn.close()