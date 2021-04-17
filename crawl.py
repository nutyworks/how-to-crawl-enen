import requests
import re
import json

def flatten(lss):
    r = []
    for ls in lss:
        if isinstance(ls, list):
            for l in ls:
                r.append(l)
        else:
            r.append(ls)

    return r


def get_naver_enen(word):
    print("    Resolving ", word)
    searchjson = json.loads(
        requests.get(
            "https://en.dict.naver.com/api3/enko/search?m=pc&range=entrySearch&query=" + word,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"}
        ).text
    )

    meanjson = json.loads(
        requests.get(
            "https://en.dict.naver.com/api/platform/enko/entry.nhn?meanType=undefined&searchResult=false&entryId="
                + searchjson["searchResultMap"]["searchResultListMap"]["WORD"]["items"][0]["entryId"],
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"}
        ).text
    )

    if not meanjson["entry"]:
        return []

    dobosio = r"^→ see (\w*)(?<!also)$"
    igcaserep = re.compile(re.escape(word), re.IGNORECASE)
    return \
        list(
            map(
                lambda x: re.sub(igcaserep, "_______", x),
                filter(
                    lambda x: x and not ord('a') <= ord(x[0]) <= ord('z'),
                    map(
                        lambda x: re.sub(r"→.*", "", x),
                        flatten(
                            map(
                                lambda x: x if not re.match(dobosio, x)
                                            else get_naver_enen(re.match(dobosio, x)[1]),
                                map(
                                    lambda x: re.sub(r"<.+?>", "", x),
                                    map(
                                        lambda x: x["show_mean"],
                                        meanjson["entry"]["means"]
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )


def load_enen(day):
    print("Resolving day %d" % day)
    primaryoutput = open('./day%d-primary.txt' % day, 'w', encoding='utf-8')
    fulloutput = open('./day%d-full.txt' % day, 'w', encoding='utf-8')

    with open('./day%d.txt' % day, 'r', encoding='utf-8') as f:
        words = list(map(
            str.strip,
            f.readlines()
        ))

        for word in words:
            enens = get_naver_enen(word)
            if not enens:
                print("Couldn't find en-en that matches condition:", word)
                primaryoutput.write(word + "\t" + "============== Couldn't find en-en ==============" + '\n')
                fulloutput.write(word + "\t" + "============== Couldn't find en-en ==============" + '\n')
                continue
            primaryoutput.write(word + "\t" + enens[0] + '\n')
            for enen in enens:
                fulloutput.write(word + "\t" + enen + '\n')

        print(words)

    primaryoutput.close()
    fulloutput.close()

# crawl words from quizlet (on developer console): 
# console.log(Object.entries(window.Quizlet.setPageData.termIdToTermsMap).map(x => x[1].word).join('\n'))

start = 1
end = 50
for i in range(start, end + 1):
    load_enen(i)