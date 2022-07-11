import os
import pickle
import json
import time
from sanic import Sanic, response

app = Sanic("GRVPN_Backend_kL1eowHlo57mjC1eCapIo14d")

basecode = '''using System;
using System.Collections;
using UnityEngine;

public class BaseCode : MonoBehaviour
{
    public static RobotMove robot;
    public MainSensor MainSensor;

    private static float[] porg = new float[9];

    // Start is called before the first frame update

    void Start()
    {
        robot = GameObject.Find("RobotModel").GetComponent<RobotMove>();
        MainSensor = GameObject.Find("RobotModel").GetComponent<MainSensor>();
        
    }

    // Update is called once per frame
    void Update()
    {
        porg = MainSensor.porg;
    }

    void caserunner(string csenum) // 케이스 코루틴 실행함수
    {
        robot = GameObject.Find("RobotModel").GetComponent<RobotMove>();
        robot.StartCoroutine(caserun(Int32.Parse(csenum)));
    }

    public static IEnumerator StepHandler(string movef, params float[] disl)
    {
        yield return robot.StartCoroutine(robot.StepHandler(movef, disl));
    }

    public static IEnumerator caserun(int casenum) // 메인 케이스
    {
        switch (casenum)
        {
            case 0:
{{CaseCode}}
        }
    }

    /* 센서영역 */
    public static float p(int snum)
    {
        return porg[snum];
    }
}
'''

def FormatCode(code: str):
    basetab = "                "
    fcode = ""
    for item in code.split("\n"):
        if "w(" in item: # w함수 포매팅
            fcode += f"{Formatw(basetab, item)}\n"
        elif "TD(" in item: # TD함수 포매팅
            fcode += f"{FormatTD(basetab, item)};\n"
        elif "T(" in item: # T함수 포매팅
            fcode += f"{FormatT(basetab, item)};\n"
        elif "H(" in item: # H함수 포매팅
            fcode += f"{FormatH(basetab, item)};\n"
        elif "pb(" in item: # pb함수 포매팅
            fcode += f"{Formatpb(basetab, item)};\n"
        elif "bwp(" in item: # bwp함수 포매팅
            fcode += f"{Formatbwp(basetab, item)};\n"
        elif "wp(" in item: # wp함수 포매팅
            fcode += f"{Formatwp(basetab, item)};\n"
        elif "CC(" in item: # CC함수 포매팅
            fcode += f"{FormatCC(basetab, item)};\n"
        else:
            fcode += f"{basetab}{item}\n"
    fcode = fcode.replace("\r", "")
    fcode = FormatBase(fcode)
    return fcode

def FormatBase(code: str):
    rcode = code.replace("ff(", "robot.ff(") # ff 변환 

    rcode = rcode.replace("c50", FormatCC("", "CC(5,0,0,2);")) # c50 변환
    rcode = rcode.replace("c53", FormatCC("", "CC(5,3,230,2);")) # c53 변환
    rcode = rcode.replace("c56", FormatCC("", "CC(5,6,230,2);")) # c56 변환
    rcode = rcode.replace("c85", FormatCC("", "CC(8,5,230,2);")) # c85 변환
    rcode = rcode.replace("c14", FormatCC("", "CC(1,4,230,2);")) # c14 변환
    return rcode

def Formatw(basetab: str, code: str):
    if "wp(" not in code: # 무빙부분이 wp 라면(w 필터링 충돌방지)
        rccash =  f'{code.split("w")[1].split("),")[0][1:]});' # 무빙부분 추출
    else:
        if "bwp(" in code: # bwp가 있으면
            rccash = f'bwp{code.split("bwp")[1].split("),")[0]});' # 무빙부분 추출
        else:
            rccash =  f'wp{code.split("wp")[1].split("),")[0]});' # 무빙부분 추출

    if "H(" in rccash: # 무빙부분 포매팅
        rccash = "{ " + f"{FormatH('', rccash)};"
    elif "pb(" in rccash:
        rccash = "{ " + f"{Formatpb('', rccash)};"
    elif "bwp(" in rccash:
        rccash = "{ " + f"{Formatbwp('', rccash)};"
    elif "wp(" in rccash:
        rccash = "{ " + f"{Formatwp('', rccash)};"

    if "wp(" not in code: # 무빙부분이 wp 라면(w 필터링 충돌방지)
        ifcash = code.split("w")[1].split("),")[1].replace(");", "") # 조건문 추출
    else:
        if "bwp(" in code: # bwp가 있으면
            ifcash = code.split("bwp")[1].split("),")[1].replace(");", "") # 조건문 추출
        else:
            ifcash = code.split("wp")[1].split("),")[1].replace(");", "") # 조건문 추출

    whiniforg = "if({{ifcode}}) { robot.clear(); yield return new WaitForSeconds(0.05f); break; }".replace("{{ifcode}}", ifcash) # 추출결합
    rcode = f"{basetab}while(true) {rccash} {whiniforg} " + "};\n"
    return rcode

def FormatT(basetab: str, code: str):
    cashcf = code.split("T")[1].replace("(", "").replace(");", "") # 인수 추출
    rcode = f'{basetab}{code.split("T")[0]}yield return robot.StartCoroutine(StepHandler("TD", 0,0,{cashcf},0,50,0))'
    return rcode

def FormatTD(basetab: str, code: str):
    cashcf = code.split("TD")[1].replace("(", "").replace(");", "") # 인수 추출
    rcode = f'{basetab}{code.split("TD")[0]}yield return robot.StartCoroutine(StepHandler("TD", {cashcf}))'
    return rcode

def FormatH(basetab: str, code: str):
    cashcf = code.split("H")[1].replace("(", "").replace(");", "") # 인수 추출
    rcode = f'{basetab}{code.split("H")[0]}yield return robot.StartCoroutine(StepHandler("H", {cashcf}))'
    return rcode

def Formatpb(basetab: str, code: str):
    cashcf = code.split("pb")[1].replace("(", "").replace(");", "") # 인수 추출
    rcode = f'{basetab}{code.split("pb")[0]}yield return robot.StartCoroutine(StepHandler("pb", {cashcf}))'
    return rcode

def Formatbwp(basetab: str, code: str):
    cashcf = code.split("bwp")[1].replace("(", "").replace(");", "") # 인수 추출
    rcode = f'{basetab}{code.split("bwp")[0]}yield return robot.StartCoroutine(StepHandler("bwp", {cashcf}))'
    return rcode

def Formatwp(basetab: str, code: str):
    cashcf = code.split("wp")[1].replace("(", "").replace(");", "") # 인수 추출
    rcode = f'{basetab}{code.split("wp")[0]}yield return robot.StartCoroutine(StepHandler("wp", {cashcf}))'
    return rcode


def FormatCC(basetab: str, code: str):
    cashcf = code.split("CC")[1].replace("(", "").replace(");", "") # 인수 추출
    rcode = f'{basetab}{code.split("CC")[0]}yield return robot.StartCoroutine(StepHandler("CC", {cashcf}))'
    return rcode

@app.route("/", methods=["POST"])
async def index(request):
    return response.json(
        {
            "code": "ok"
        }
    )


@app.route("/upload", methods=["POST"])
async def upload(request):
    loadcode = FormatCode(request.args['code'][0]) # 클라이언트에서 불러온 코드 & 포매팅 진행
    savecode = basecode.replace("{{CaseCode}}",loadcode)
    with open("data.pickle","wb") as fw:
        pickle.dump(savecode, fw)
    return response.json(
        {
            "code": "ok"
        }
    )

@app.route("/download", methods=["GET"])
async def download(request):
    with open("data.pickle","rb") as fr:
        data = pickle.load(fr)
    return response.text(
        data
    )

@app.route("/loadmap", methods=["GET"])
async def loadmap(request):
    BaseDict = {"name":[], "time":[], "data":[]}
    #폴더 파일 불러오기
    files = os.listdir("./maps")
    #파일 불러오기
    for file in files:
        if file.endswith(".json"):
            with open(f"./maps/{file}", "rb") as fr:
                data = json.load(fr)
                BaseDict["name"].append(data['name'])
                BaseDict["time"].append(data['time'])
                BaseDict["data"].append(data['data'])
    return response.text(
        json.dumps(BaseDict)
    )

@app.route("/savemap", methods=["POST"])
async def savemap(request):
    if request.form:
        # 폴더 있는지 확인후 생성
        if not os.path.exists("./maps"):
            os.mkdir("./maps")
        with open(f"./maps/{request.form['name'][0]}.json", 'w', encoding="UTF8") as f:
            json.dump({"name":request.form['name'][0], "time":time.strftime('%Y-%m-%d %H:%M:%S'), "data":request.form['data'][0]}, f)
        return response.text(
            "ok"
        )
    else:
        return response.text(
            "error"
        )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8800,
    )