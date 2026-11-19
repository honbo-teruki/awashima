"""三ツ目デザインのスライドを、見本のpptx（template.pptx）のレイアウトから作る。

表紙の赤枠と斜線、本文ページの角の3本線、タイトルの位置・色・書体は、すべて
template.pptx のスライドレイアウトに入っている。このモジュールはレイアウトを使って
ページを足すだけなので、デザインは見本と完全に同じになる。

座標は 1920×1080 の px で指定する（見本の実寸 10in×5.625in を px に直したもの）。
文字の大きさは pt（見本と同じ。本文 10〜11pt、見出し 14〜20pt）。

使い方:
    import sys; sys.path.insert(0, "<このフォルダ>")
    from mitsume_deck import Deck
    d = Deck()                       # 見本を読み、見本のスライドは消した状態から始める
    d.cover("魚沼市ふるさと納税\\n寄附拡大のご提案", "2026年11月20日　三ツ目株式会社")
    s = d.content("資料の目次")
    d.toc(s, ["会社紹介", "実績と事例紹介"])
    s = d.clone(15)                  # 見本の15枚目（3つの円）を複製して文字を差し替える
    d.replace(s, {"返礼品の数": "品数", ...})
    d.thanks("三ツ目株式会社\\n澤　正史", "【連絡先】\\n...")
    d.save("out.pptx")
"""
import copy
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.pptx")

PX = 4762.5  # 1px（1920幅）あたりのEMU
FONT = "Meiryo"

RED = RGBColor(0xFF, 0x00, 0x00)
PINK = RGBColor(0xFF, 0xB7, 0xB7)
PALE = RGBColor(0xFF, 0xEA, 0xEA)
INK = RGBColor(0x33, 0x33, 0x33)
SUB = RGBColor(0x59, 0x59, 0x59)
NOTE = RGBColor(0x66, 0x66, 0x66)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MEMO_FILL = RGBColor(0xFF, 0xF6, 0xCC)
MEMO_LINE = RGBColor(0xD9, 0xA4, 0x00)
MEMO_TEXT = RGBColor(0x6B, 0x4E, 0x00)

LAYOUT_COVER = "TITLE"
LAYOUT_BODY = "TITLE_AND_BODY"                  # 角に3本線（右上・左下）
LAYOUT_BODY_FRAMED = "TITLE_AND_BODY_1"         # 赤枠（代表プロフィールなど）
LAYOUT_THANKS = "SECTION_TITLE_AND_DESCRIPTION"  # 右半分が赤


def px(v):
    return Emu(int(round(v * PX)))


def units(line):
    """1行の幅（全角=1、半角=0.6）。"""
    return sum(0.6 if ord(ch) < 0x2E80 else 1.0 for ch in line)


def fit(text, width_px, max_pt, min_pt=9):
    """どの行も width_px に1割の余裕を持って収まる、いちばん大きい文字サイズ（pt）を返す。
    1pt = 1920幅で約2.67px。行は自分で改行しておく（自動の折り返しに任せない）。"""
    longest = max(units(l) for l in text.split("\n")) or 1
    inner = width_px - 40  # 文字枠の左右の内側の余白（各約19px）を引く
    pt = inner / 1.15 / (longest * 2.667)
    return max(min_pt, min(max_pt, int(pt * 2) / 2))


class Deck:
    def __init__(self, template=TEMPLATE, keep_slides=False):
        self.template = template
        self.prs = Presentation(template)
        self._src = Presentation(template)  # 複製元（見本のスライドを残しておく）
        # 同じ名前のレイアウトが複数のマスターにあるので、見本のスライドが実際に使っているものを選ぶ
        self.layouts = {}
        for sl in self.prs.slides:
            self.layouts.setdefault(sl.slide_layout.name, sl.slide_layout)
        for m in self.prs.slide_masters:
            for l in m.slide_layouts:
                self.layouts.setdefault(l.name, l)
        if not keep_slides:
            sld_ids = self.prs.slides._sldIdLst
            for sld_id in list(sld_ids):
                self.prs.part.drop_rel(sld_id.rId)
                sld_ids.remove(sld_id)

    # ---------- ページ ----------
    def _add(self, layout_name):
        slide = self.prs.slides.add_slide(self.layouts[layout_name])
        return slide

    @staticmethod
    def _ph(slide, idx):
        for ph in slide.placeholders:
            if ph.placeholder_format.idx == idx:
                return ph
        return None

    def _clear_unused(self, slide, keep):
        for ph in list(slide.placeholders):
            if ph.placeholder_format.idx not in keep and ph.placeholder_format.type != 13:  # 13=スライド番号
                ph._element.getparent().remove(ph._element)

    def cover(self, title, date_line):
        """表紙。title は中央左の大きな赤文字（42pt）、date_line は下の赤文字の行。"""
        s = self._add(LAYOUT_COVER)
        t = self._ph(s, 0)
        t.left, t.top, t.width, t.height = px(93), px(304), px(1136), px(431)  # 見本1枚目と同じ位置
        self._set_text(t, title, size=fit(title, 1136, 42), bold=True, color=RED, align=PP_ALIGN.CENTER)
        st = self._ph(s, 1)
        self._set_text(st, date_line, size=20, bold=True, color=RED, align=PP_ALIGN.CENTER)
        self._clear_unused(s, {0, 1})
        return s

    def content(self, title, subtitle=None, framed=False):
        """本文ページ。title は左上の赤文字（28pt太字）、subtitle はその下の赤い一文（18pt太字）。"""
        s = self._add(LAYOUT_BODY_FRAMED if framed else LAYOUT_BODY)
        self._set_text(self._ph(s, 0), title, size=28, bold=True, color=RED)
        if subtitle:
            self._set_text(self._ph(s, 2), subtitle, size=18, bold=True, color=RED)
        keep = {0, 2} if subtitle else {0}
        self._clear_unused(s, keep)
        self._slide_number(s)
        return s

    def thanks(self, name_lines, contact_lines, title="Thank you!"):
        """締め。左に Thank you!（赤）と名前・連絡先、右半分は赤の面に白抜きロゴ（レイアウトに入っている）。"""
        s = self._add(LAYOUT_THANKS)
        self._set_text(self._ph(s, 0), title, size=42, color=RED, align=PP_ALIGN.CENTER)
        self._set_text(self._ph(s, 1), name_lines + "\n\n" + contact_lines, size=21, color=RED,
                       align=PP_ALIGN.CENTER)
        self._clear_unused(s, {0, 1})
        logo = os.path.join(HERE, "thanks_logo.png")
        if os.path.exists(logo):
            s.shapes.add_picture(logo, px(960), px(60), px(960), px(960))
        return s

    def clone(self, pattern_no):
        """見本の pattern_no 枚目（1始まり）を複製して末尾に足す。画像も一緒に写す。"""
        src = self._src.slides[pattern_no - 1]
        s = self.prs.slides.add_slide(self._layout_like(src.slide_layout))
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        for el in src.shapes._spTree.iterchildren():
            if el.tag.endswith("}nvGrpSpPr") or el.tag.endswith("}grpSpPr"):
                continue
            s.shapes._spTree.append(copy.deepcopy(el))
        # 画像などの参照IDを、新しいスライドのIDに一度に付け替える（順に置き換えると番号がぶつかる）
        remap = {}
        for rel in list(src.part.rels.values()):
            if "notesSlide" in rel.reltype or "slideLayout" in rel.reltype:
                continue
            if rel.is_external:
                remap[rel.rId] = s.part.rels.get_or_add_ext_rel(rel.reltype, rel.target_ref)
            else:
                remap[rel.rId] = s.part.rels.get_or_add(rel.reltype, rel.target_part)
        attrs = (qn("r:embed"), qn("r:link"), qn("r:id"))
        for node in s.shapes._spTree.iter():
            for attr in attrs:
                v = node.get(attr)
                if v in remap:
                    node.set(attr, remap[v])
        return s

    def _layout_like(self, src_layout):
        pn = src_layout.part.partname
        for m in self.prs.slide_masters:
            for l in m.slide_layouts:
                if l.part.partname == pn:
                    return l
        return self.layouts[src_layout.name]

    @staticmethod
    def replace(slide, mapping):
        """スライド内の文字を置き換える（書式は残す）。runをまたぐ語は段落単位で置き換える。"""
        def fix(tf):
            for para in tf.paragraphs:
                full = "".join(r.text for r in para.runs)
                new = full
                for a, b in mapping.items():
                    new = new.replace(a, b)
                if new != full and para.runs:
                    para.runs[0].text = new
                    for r in para.runs[1:]:
                        r.text = ""

        def walk(shapes):
            for sh in shapes:
                if sh.shape_type == 6:
                    walk(sh.shapes)
                if sh.has_text_frame:
                    fix(sh.text_frame)
                if getattr(sh, "has_table", False) and sh.has_table:
                    for row in sh.table.rows:
                        for cell in row.cells:
                            fix(cell.text_frame)
        walk(slide.shapes)

    def save(self, path):
        self.prs.save(path)
        return path

    # ---------- 部品（見本から測った寸法） ----------
    def _slide_number(self, slide):
        tb = slide.shapes.add_textbox(px(1798), px(974), px(115), px(83))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        fld = p._p.makeelement(qn("a:fld"), {"id": "{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}", "type": "slidenum"})
        rpr = fld.makeelement(qn("a:rPr"), {"lang": "ja-JP", "sz": "1000"})
        fld.append(rpr)
        t = fld.makeelement(qn("a:t"), {})
        t.text = "‹#›"
        fld.append(t)
        p._p.append(fld)

    @staticmethod
    def _set_text(shape, text, size=11, bold=False, color=INK, align=PP_ALIGN.LEFT, font=FONT):
        tf = shape.text_frame
        tf.clear()
        for i, line in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            r = p.add_run()
            r.text = line
            f = r.font
            f.size = Pt(size)
            f.bold = bold
            f.name = font
            f.color.rgb = color
            rpr = r._r.get_or_add_rPr()
            ea = rpr.find(qn("a:ea"))
            if ea is None:
                ea = rpr.makeelement(qn("a:ea"), {})
                rpr.append(ea)
            ea.set("typeface", font)
        return shape

    def text(self, slide, x, y, w, h, text, size=11, bold=False, color=INK, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP):
        tb = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
        tb.text_frame.word_wrap = True
        tb.text_frame.vertical_anchor = anchor
        return self._set_text(tb, text, size, bold, color, align)

    def box(self, slide, x, y, w, h, fill=None, line=None, line_pt=1.0, shape=MSO_SHAPE.RECTANGLE,
            text=None, size=11, bold=True, color=INK, align=PP_ALIGN.CENTER):
        sh = slide.shapes.add_shape(shape, px(x), px(y), px(w), px(h))
        st = sh._element.find(qn("p:style"))  # テーマの影・既定色を外す（見本の図形には影がない）
        if st is not None:
            sh._element.remove(st)
        if fill is None:
            sh.fill.background()
        else:
            sh.fill.solid()
            sh.fill.fore_color.rgb = fill
        if line is None:
            sh.line.fill.background()
        else:
            sh.line.color.rgb = line
            sh.line.width = Pt(line_pt)
        if text is not None:
            sh.text_frame.word_wrap = True
            sh.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
            self._set_text(sh, text, size, bold, color, align)
        return sh

    def toc(self, slide, items):
        """目次（見本2枚目）。赤い丸に番号、淡いピンクの角丸の帯に項目名。最大5項目。"""
        y0, step = 251, 165
        for i, item in enumerate(items):
            y = y0 + i * step
            self.box(slide, 160, y, 133, 133, fill=RED, shape=MSO_SHAPE.OVAL,
                     text=f"{i + 1:02d}", size=14, bold=True, color=WHITE)
            self.box(slide, 325, y, 1493, 133, fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
                     text=item, size=14, bold=True, color=RED, align=PP_ALIGN.LEFT)

    def cards3(self, slide, heads, bodies, y=315, h=564, size=20):
        """3枚のカード（見本4枚目）。ピンクの太枠3pt、上端にピンクの帯と赤い見出し14pt、中は赤の太字。
        中の文は1行全角10字まで（18pt）。長いときは size を下げるか改行を自分で入れる。"""
        xs = (107, 750, 1393)  # 左右の余白をそろえた配置（カード幅421、間222）
        body_pt = min(fit(bd, 373, size) for bd in bodies)  # 3枚の文字サイズをそろえる
        head_pt = min(fit(hd, 381, 14) for hd in heads)
        for x, hd, bd in zip(xs, heads, bodies):
            self.box(slide, x, y, 421, h, line=PINK, line_pt=3.0)
            self.box(slide, x, y, 421, 83, fill=PINK, text=hd, size=head_pt, bold=True, color=RED)
            self.text(slide, x + 24, y + 110, 373, h - 150, bd, size=body_pt, bold=True, color=RED,
                      align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    def points3(self, slide, labels, captions):
        """3つの円（見本15枚目）。直径467のピンクの円に①②③と赤20pt太字、下に11ptの説明。"""
        lab_pt = min(fit(l, 300, 20) for l in labels)  # 円の中で文字が入る幅は直径の約3分の2
        cap_pt = min(fit(c, 592, 11) for c in captions)
        for i, (lab, cap) in enumerate(zip(labels, captions)):
            x = 147 + i * 592
            self.box(slide, x, 288, 467, 467, fill=PINK, shape=MSO_SHAPE.OVAL,
                     text=f"{'①②③'[i]}\n{lab}", size=lab_pt, bold=True, color=RED)
            self.text(slide, x - 62, 773, 592, 160, cap, size=cap_pt, color=INK, align=PP_ALIGN.CENTER)

    def point_boxes(self, slide, items, highlight=0, y=299, h=400):
        """横並びの角丸の箱（見本10枚目）。強調する1つだけピンク、ほかは淡いピンク。"""
        n = len(items)
        w = (1680 - 40 * (n - 1)) / n
        for i, t in enumerate(items):
            self.box(slide, 107 + i * (w + 40), y, w, h, fill=PINK if i == highlight else PALE,
                     shape=MSO_SHAPE.ROUNDED_RECTANGLE, text=t, size=11, bold=True, color=SUB)

    def kpi(self, slide, label, value, lines, x=107, y=299, w=773):
        """大きな数字（見本8枚目）。ラベル、赤の大きな数字、説明。"""
        self.text(slide, x, y, w, 64, label, size=12, bold=True, color=INK)
        v = self.text(slide, x - 16, y + 48, w + 43, 240, value, size=fit(value, w + 43, 66), bold=True, color=RED)
        v.text_frame.word_wrap = False  # 大きな数字は折り返さない
        self.text(slide, x, y + 282, w, 117, lines, size=13, bold=True, color=INK)

    def bars(self, slide, labels, values, highlight_n=3, x=960, y=299, w=880, base=100.0, title=None,
             fmt="{:.1f}%", height=364):
        """縦棒（見本8枚目）。上位 highlight_n 本は赤、残りはピンク。基準線と基準値を添える。"""
        if title:
            self.text(slide, x, y, w, 59, title, size=11, bold=True, color=INK)
        n = len(values)
        top, bottom = y + 137, y + 501
        vmax = max(values)
        lo = min(base, min(values)) if base is not None else 0
        span = (vmax - lo) or 1
        pitch = 160
        x0 = x + 37
        for i, (lab, v) in enumerate(zip(labels, values)):
            hgt = max(8, (v - lo) / span * height)
            bx = x0 + i * pitch
            self.box(slide, bx, bottom - hgt, 96, hgt, fill=RED if i < highlight_n else PINK)
            self.text(slide, bx - 37, bottom - hgt - 59, 171, 53, fmt.format(v), size=12, bold=True,
                      color=RED if i < highlight_n else INK, align=PP_ALIGN.CENTER)
            self.text(slide, bx - 32, bottom + 11, 160, 53, lab, size=11, color=INK, align=PP_ALIGN.CENTER)
        ln = slide.shapes.add_connector(1, px(x + 27), px(bottom), px(x0 + (n - 1) * pitch + 106), px(bottom))
        ln.line.color.rgb = INK
        ln.line.width = Pt(1.2)
        if base is not None:
            self.text(slide, x - 75, bottom - 21, 107, 43, fmt.format(base).replace(".0", ""), size=10,
                      color=SUB, align=PP_ALIGN.RIGHT)

    def table(self, slide, rows, x=107, y=299, w=1680, col_w=None, row_h=64, highlight_rows=()):
        """表（見本9・16枚目）。見出し行は赤地に白の太字11pt、本文は11pt #333333、強調行はピンク地。"""
        nr, nc = len(rows), len(rows[0])
        gf = slide.shapes.add_table(nr, nc, px(x), px(y), px(w), px(row_h * nr))
        tbl = gf.table
        tblPr = tbl._tbl.tblPr
        style = tblPr.find(qn("a:tableStyleId"))
        if style is not None:
            style.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"  # 罫線なしのシンプルな表
        if col_w:
            for i, cw in enumerate(col_w):
                tbl.columns[i].width = px(cw)
        for r, row in enumerate(rows):
            tbl.rows[r].height = px(row_h)
            for c, val in enumerate(row):
                cell = tbl.cell(r, c)
                cell.fill.solid()
                if r == 0:
                    cell.fill.fore_color.rgb = RED
                elif r in highlight_rows:
                    cell.fill.fore_color.rgb = PINK
                else:
                    cell.fill.fore_color.rgb = WHITE if r % 2 else PALE
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                self._set_text(cell, str(val), size=11, bold=(r == 0 or c == 0),
                               color=WHITE if r == 0 else INK,
                               align=PP_ALIGN.CENTER if r == 0 else PP_ALIGN.LEFT)
        return gf

    def note(self, slide, text, x=107, y=896, w=1653, h=80):
        """出典・注記（8pt #666666）。"""
        return self.text(slide, x, y, w, h, text, size=8, color=NOTE)

    def memo(self, slide, text, x=107, y=725, w=1680, h=229):
        """未確定の情報の置き場（見本10・16枚目の黄色い箱）。「✎ 入れてください｜」で始める。
        渡されていない数字・事例・名前はここに書き、本文には［ ］の仮置きを入れる。"""
        if not text.startswith("✎"):
            text = "✎ 入れてください｜\n" + text
        return self.box(slide, x, y, w, h, fill=MEMO_FILL, line=MEMO_LINE, line_pt=1.0,
                        shape=MSO_SHAPE.ROUNDED_RECTANGLE, text=text, size=10, bold=True,
                        color=MEMO_TEXT, align=PP_ALIGN.LEFT)
