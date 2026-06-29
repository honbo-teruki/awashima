/**
 * 粟島 民宿 予約相談フォーム → スプレッドシート記録＆メール通知
 * 使い方:
 *  1. Googleスプレッドシートを新規作成
 *  2. 拡張機能 → Apps Script を開く
 *  3. このコードを全部貼り付けて保存
 *  4. デプロイ → 新しいデプロイ → 種類「ウェブアプリ」
 *     - 実行ユーザー: 自分
 *     - アクセスできるユーザー: 全員
 *  5. 発行された「ウェブアプリのURL」を輝紀に渡す（フォームに設定する）
 */
var NOTIFY_EMAIL = "honbo@reterras.co.jp";   // 通知の宛先
var SHEET_NAME   = "予約相談";

function doPost(e){
  try{
    var d = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if(sh.getLastRow() === 0){
      sh.appendRow(["受付日時","代表者","電話","メール","連絡方法","行く日","泊数","部屋数","大人","子供","食事","来る船","送迎","エリア希望","希望の宿","やりたいこと","その他希望","備考"]);
    }
    sh.appendRow([new Date(), d.name, d.tel, d.email, d.contact, d.checkin, d.nights, d.rooms, d.adults, d.kids, d.meal, d.boat, d.pickup, d.area, d.yado, d.experiences, d.expOther, d.note]);

    var details =
      "代表者　： " + d.name + "\n" +
      "電話　　： " + d.tel + "\n" +
      "メール　： " + (d.email || "（なし）") + "\n" +
      "希望の連絡方法： " + d.contact + "\n" +
      "行く日　： " + d.checkin + "　／　" + d.nights + "泊\n" +
      "部屋数　： " + d.rooms + "室\n" +
      "人数　　： 大人" + d.adults + "名・子供" + d.kids + "名\n" +
      "食事　　： " + d.meal + "\n" +
      "来る船　： " + d.boat + "\n" +
      "送迎　　： " + d.pickup + "\n" +
      "エリア希望： " + d.area + "\n" +
      "希望の宿： " + d.yado + "\n" +
      "やりたいこと： " + ((d.experiences || "") + (d.expOther ? "（その他:" + d.expOther + "）" : "") || "特になし") + "\n" +
      "備考　　： " + (d.note || "なし");

    // ① 幹事（自分）へ通知
    MailApp.sendEmail(NOTIFY_EMAIL, "【粟島 宿泊相談】" + d.name + "様",
      "新しい宿泊相談が届きました。\n\n" + details + "\n\n（フォームから自動送信されています）");

    // ② 相手（申込者）へ受付控え（メールが入力されていれば）
    if(d.email){
      MailApp.sendEmail(d.email, "【粟島 宿泊相談を受け付けました】" + d.name + "様",
        d.name + " 様\n\n" +
        "粟島の宿泊相談を受け付けました。\n幹事が宿の空き状況を確認し、追ってご連絡します。\n\n" +
        "――― ご入力内容 ―――\n" + details + "\n\n" +
        "※これは予約確定ではありません。確定後の変更・キャンセルは各自でお宿へ直接ご連絡ください。\n" +
        "※お心当たりがない場合はこのメールを破棄してください。");
    }

    return ContentService.createTextOutput(JSON.stringify({ok:true})).setMimeType(ContentService.MimeType.JSON);
  }catch(err){
    return ContentService.createTextOutput(JSON.stringify({ok:false, error:String(err)})).setMimeType(ContentService.MimeType.JSON);
  }
}

// 動作確認用（任意）: デプロイ後にブラウザでURLを開くとこの文字が出ればOK
function doGet(){
  return ContentService.createTextOutput("粟島 宿泊相談 受付スクリプト 稼働中");
}
