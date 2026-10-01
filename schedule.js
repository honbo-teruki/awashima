/* =========================================================================
   粟島汽船ダイヤ 共通データ（フェリーボット ferry.html と 宿フォーム index.html の両方が使用）
   ★★★ ダイヤ更新はこのファイルだけ直せば両方に反映される ★★★
   出典: 粟島汽船 公式「令和8年10月～令和9年2月 粟島汽船運航時刻表」（9月17日修正版）
        https://awashimakisen.co.jp/schedule.html （PDF作成日 2026-09-30 / 取得日 2026-10-01）
   ※令和9年3月以降のダイヤは公式未掲載（2026-10-01時点）。公開されたら PERIODS に追記し validTo を延ばす。
   船: フェリー「ニューあわしま」(片道約95分)。この期間に高速船の設定はなし。
   便の向き: d="粟"=粟島発→岩船着 / d="岩"=岩船発→粟島着
   t=出発時刻, a=到着時刻, hs:true=高速船
   ※検証方法: PDFをpdfplumberで座標抽出＋300dpi画像で全便確認済み（目視一発はNG）
   ========================================================================= */
const INFO = {
  official:"https://awashimakisen.co.jp/schedule.html",
  status:"https://awashimakisen.co.jp/",   // 当日の運航状況（○×・欠航告知）は公式トップページに出る
  tel:"0254-55-2131",
  validFrom:"2026-10-01", validTo:"2027-02-28",
  source:"令和8年10月～令和9年2月ダイヤ",
};

const S = (d,t,a,hs)=>({d,t,a,hs:!!hs});
const PAT = {
  STD4:[S("粟","8:00","9:35"),  S("岩","10:15","11:50"), S("粟","12:45","14:20"), S("岩","15:00","16:35")],
  STD2:[S("粟","8:00","9:35"),  S("岩","15:00","16:35")],
  OUT4:[S("岩","8:00","9:35"),  S("粟","10:30","12:05"), S("岩","12:45","14:20"), S("粟","15:00","16:35")],
  EVE3:[S("粟","8:00","9:35"),  S("岩","13:00","14:35"), S("粟","15:10","16:45")],   // 15:10は粟島発（9月までの14:00/16:10から変更）
  SUN3:[S("岩","8:00","9:35"),  S("粟","13:00","14:35"), S("岩","15:10","16:45")],   // 15:10は岩船発
};

// 曜日テンプレ：配列の並びは [日,月,火,水,木,金,土]
const T_OCT = ["SUN3","STD4","STD2","STD2","STD2","EVE3","OUT4"];
const T_NOV = ["STD2","STD4","STD2","STD4","STD2","STD4","STD2"];   // 月水金=4便 / 火木土日=2便
const one = p => [p,p,p,p,p,p,p];

const PERIODS = [
  {from:"2026-10-01", to:"2026-10-10", dow:T_OCT},
  {from:"2026-10-11", to:"2026-10-11", dow:one("OUT4"), label:"連休ダイヤ"},
  {from:"2026-10-12", to:"2026-10-12", dow:one("SUN3"), label:"スポーツの日"},
  {from:"2026-10-13", to:"2026-11-01", dow:T_OCT},
  {from:"2026-11-02", to:"2026-12-28", dow:T_NOV},
  {from:"2026-12-29", to:"2027-02-28", dow:one("STD2")},
];

const FARE = {
  // 出典: 公式 schedule.html の運賃表／「令和8年10月～12月の燃料油価格変動調整金について」（基本2,100円/1,050円＋調整金740円/370円）
  note:"片道・フェリー。燃料油価格変動調整金込み・令和8年10〜12月の額（調整金は3か月ごとに見直し。最新は公式で確認）",
  rows:[ ["大人（中学生以上）","2,840円"], ["小学生","1,420円"] ]
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
