import pickle
from re import I
import re
from sanic import Sanic, response

app = Sanic("GRVPN_Backend_kL1eowHlo57mjC1eCapIo14d")

basecode = '''using System;
using System.Collections;
using UnityEngine;

public class BaseCode : MonoBehaviour
{
    public static RobotMove robot;
    public MainSensor MainSensor;
    public static float[] distance;

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
        distance = robot.distance;
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
    for item in code.split("\r\n"):
        if "w(" in item: # w함수 포매팅
            fcode += Formatw(basetab, item)

        elif "H(" in item: # H함수 포매팅
            fcode += f"{FormatH(basetab, item)}\r\n"
        else:
            fcode += f"{basetab}{item}\r\n"
    return fcode

def Formatw(basetab: str, code: str):
    rccash =  f'{code.split("w")[1].split("),")[0][1:]});' # 무빙부분 추출

    if "H(" in rccash: # 무빙부분 포매팅
        rccash = f"{FormatH('', rccash)};"

    ifcash = code.split("w")[1].split("),")[1].replace(");", "") # 조건문 추출

    whiniforg = "{ if({{ifcode}}) { robot.f_agl = 0; break; }".replace("{{ifcode}}", ifcash) # 추출결합
    rcode = f"{basetab}while(true) {whiniforg} {rccash} " + "};\r\n"
    return rcode

def FormatH(basetab: str, code: str):
    cashcf = code.split("H")[1].replace("(", "").replace(");", "")
    rcode = f'{basetab}{code.split("H")[0]}yield return robot.StartCoroutine(StepHandler("H", {cashcf}))'
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

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8800,
    )
