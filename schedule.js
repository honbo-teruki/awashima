/* =========================================================================
   粟島汽船ダイヤ 共通データ（フェリーボット index.html と 宿フォーム yado.html の両方が使用）
   ★★★ ダイヤ更新はこのファイルだけ直せば両方に反映される ★★★
   出典: 粟島汽船 公式「令和8年3月～9月 粟島汽船運航時刻表」
        https://awashimakisen.co.jp/schedule.html
   船: フェリー「ニューあわしま」(片道約95分)。3/23-4/7のみ高速船(約60分)。
   便の向き: d="粟"=粟島発→岩船着 / d="岩"=岩船発→粟島着
   t=出発時刻, a=到着時刻, hs:true=高速船
   ※検証方法: PDFをpdfplumberで座標抽出＋300dpi画像で全便確認済み（目視一発はNG）
   ========================================================================= */
const INFO = {
  official:"https://awashimakisen.co.jp/schedule.html",
  tel:"0254-55-2131",
  validFrom:"2026-03-01", validTo:"2026-09-30",
  source:"令和8年3月～9月ダイヤ",
};

const S = (d,t,a,hs)=>({d,t,a,hs:!!hs});
const PAT = {
  STD4:[S("粟","8:00","9:35"),  S("岩","10:15","11:50"), S("粟","12:45","14:20"), S("岩","15:00","16:35")],
  STD2:[S("粟","8:00","9:35"),  S("岩","15:00","16:35")],
  STD4E:[S("粟","8:00","9:35"), S("岩","10:15","11:50"), S("粟","12:45","14:20"), S("岩","15:00","16:35"), S("粟","17:10","18:45")],
  OUT4:[S("岩","8:00","9:35"),  S("粟","10:30","12:05"), S("岩","12:45","14:20"), S("粟","15:00","16:35")],
  OUT5:[S("岩","8:00","9:35"),  S("粟","10:30","12:05"), S("岩","12:45","14:20"), S("粟","15:00","16:35"), S("岩","17:10","18:45")],
  EVE3:[S("粟","8:00","9:35"),  S("岩","14:00","15:35"), S("粟","16:10","17:45")],   // 16:10は粟島発
  SUN3:[S("岩","8:00","9:35"),  S("粟","14:00","15:35"), S("岩","16:10","17:45")],
  HS2: [S("粟","8:00","9:00",true), S("岩","15:00","16:00",true)],
  MARA:[S("粟","8:00","9:35"),  S("岩","10:15","11:50"), S("粟","13:30","15:05"), S("岩","15:30","17:05")],
  C620:[S("粟","8:00","9:35"),  S("岩","10:15","11:50"), S("粟","12:15","13:50"), S("岩","14:15","15:50"), S("粟","16:15","17:50")], // 16:15は粟島発
  C621:[S("岩","8:00","9:35"),  S("粟","10:30","12:05"), S("岩","12:45","14:20"), S("粟","15:00","16:35"), S("岩","17:00","18:35")],
};

// 曜日テンプレ：配列の並びは [日,月,火,水,木,金,土]
const T_A    = ["STD2","STD4","STD2","STD2","STD2","STD4","STD2"];
const T_B    = ["STD4","STD4","STD2","STD2","STD2","STD4","STD4"];
const T_SUM  = ["OUT4","OUT5","STD4","STD4E","OUT4","OUT4","OUT4"];
const T_FALL = ["SUN3","STD4","STD2","STD2","STD2","EVE3","OUT4"];
const one = p => [p,p,p,p,p,p,p];

const PERIODS = [
  {from:"2026-03-01", to:"2026-03-22", dow:T_A},
  {from:"2026-03-23", to:"2026-04-07", dow:one("HS2"), label:"フェリードック・高速船運航"},
  {from:"2026-04-08", to:"2026-04-17", dow:T_A},
  {from:"2026-04-18", to:"2026-04-18", dow:one("STD4")},
  {from:"2026-04-19", to:"2026-04-19", dow:one("MARA"), label:"島内マラソン"},
  {from:"2026-04-20", to:"2026-04-27", dow:T_B},
  {from:"2026-04-28", to:"2026-04-28", dow:one("EVE3")},
  {from:"2026-04-29", to:"2026-05-05", dow:one("OUT4"), label:"GW特別ダイヤ"},
  {from:"2026-05-06", to:"2026-05-06", dow:one("SUN3")},
  {from:"2026-05-07", to:"2026-05-13", dow:T_B},
  {from:"2026-05-14", to:"2026-05-14", dow:one("STD4")},
  {from:"2026-05-15", to:"2026-05-15", dow:one("EVE3"), label:"島内健診"},
  {from:"2026-05-16", to:"2026-06-19", dow:T_B},
  {from:"2026-06-20", to:"2026-06-20", dow:one("C620"), label:"増便日"},
  {from:"2026-06-21", to:"2026-06-21", dow:one("C621"), label:"クリーンアップ"},
  {from:"2026-06-22", to:"2026-07-16", dow:T_B},
  {from:"2026-07-17", to:"2026-07-17", dow:one("EVE3")},
  {from:"2026-07-18", to:"2026-07-19", dow:one("OUT4")},
  {from:"2026-07-20", to:"2026-08-15", dow:T_SUM, label:"夏ダイヤ"},
  {from:"2026-08-16", to:"2026-08-16", dow:one("OUT5"), label:"夏ダイヤ"},
  {from:"2026-08-17", to:"2026-09-18", dow:T_FALL},
  {from:"2026-09-19", to:"2026-09-22", dow:one("OUT4"), label:"連休ダイヤ"},
  {from:"2026-09-23", to:"2026-09-23", dow:one("SUN3"), label:"秋分の日"},
  {from:"2026-09-24", to:"2026-09-30", dow:T_FALL},
];

const FARE = {
  note:"片道・フェリー。※2026年7月1日に運賃改定予定（最新は公式で確認）",
  rows:[ ["大人（中学生以上）","2,520円"], ["小学生","1,260円"] ]
};

/* ---------- 共通ユーティリティ ---------- */
const DOW=["日","月","火","水","木","金","土"];
const pad=n=>String(n).padStart(2,"0");
const iso=d=>`${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
const toMin=t=>{const[h,m]=t.split(":").map(Number);return h*60+m;};

/* ---------- その日のダイヤ ---------- */
function scheduleForDate(d){
  const day=iso(d);
  const p=PERIODS.find(p=>day>=p.from && day<=p.to);
  if(!p) return null;
  const sailings=PAT[p.dow[d.getDay()]] || [];
  return {sailings, label:p.label||null};
}

/* ---------- 宿フォーム用ヘルパー ----------
   指定日の便を方向で絞って時刻順に返す。
   dir: "岩"=島へ向かう(岩船発) / "粟"=島から帰る(粟島発) / null=全部
   戻り値: {outOfRange, label, list:[{d,t,a,hs,depLabel,arrPort}]} */
function boatsFor(dateObj, dir){
  const s=iso(dateObj);
  if(s<INFO.validFrom || s>INFO.validTo) return {outOfRange:true, label:null, list:[]};
  const res=scheduleForDate(dateObj);
  if(!res) return {outOfRange:true, label:null, list:[]};
  let list=res.sailings.slice().sort((a,b)=>toMin(a.t)-toMin(b.t));
  if(dir) list=list.filter(x=>x.d===dir);
  list=list.map(x=>({...x, depLabel:x.d==="粟"?"粟島発":"岩船発", arrPort:x.d==="粟"?"岩船":"粟島"}));
  return {outOfRange:false, label:res.label, list};
}
