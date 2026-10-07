"""Klamotten Kurator — Editorial Minimal. Start: python main.py."""
import json
import random
import sys
from pathlib import Path
import wardrobe
from PySide6.QtCore import Qt, QStandardPaths, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QScrollArea,
    QStackedWidget, QMessageBox, QComboBox, QLayout, QFileDialog)

COLORS = dict(zip(wardrobe.COLORS, ['#eeeae1','#242424','#888888','#c6b89a','#f0e4ca','#263b53','#886448','#426b9c','#9cbed6','#727c59','#773b50']))
TYPES = wardrobe.SUBCATEGORIES
STYLES = wardrobe.OCCASIONS
SEASONS = wardrobe.SEASONS
CATEGORY_LABELS = {'Top':'Oberteile','Bottom':'Hosen','Footwear':'Schuhe','Socks':'Socken','Outerwear':'Jacken','Headwear':'Kopfbedeckungen'}

def label(text, role=None):
    w=QLabel(text); w.setWordWrap(True)
    if role: w.setObjectName(role)
    return w

def button(text, callback, role=None):
    w=QPushButton(text); w.setCursor(Qt.CursorShape.PointingHandCursor)
    if role: w.setObjectName(role)
    w.clicked.connect(callback)
    return w

class Garment(QWidget):
    """Scalable clothing illustrations; no external assets required."""
    def __init__(self, item):
        super().__init__(); self.item=item; self.setMinimumHeight(160)
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side=min(self.width(),self.height()); p.translate((self.width()-side)/2,(self.height()-side)/2)
        p.scale(side/200,side/200)
        p.setPen(QPen(QColor('#48463e'),1.3)); p.setBrush(QColor(COLORS[self.item['Color']]))
        category=self.item['Category']
        if category in ['Top','Outerwear']:
            points=[(65,30),(85,23),(100,35),(115,23),(135,30),(170,65),(145,85),(132,65),(132,168),(68,168),(68,65),(55,85),(30,65)]
            p.drawPolygon(QPolygonF([QPointF(x,y) for x,y in points]))
            p.drawArc(83,17,34,25,180*16,180*16)
            if category=='Outerwear' or self.item['Subcategory']=='Shirt':
                p.drawLine(100,36,100,166)
                for y in [60,83,106,129,152]: p.drawEllipse(QPointF(105,y),2,2)
                p.drawRect(76,92,16,22); p.drawRect(112,92,16,22)
        elif category=='Bottom':
            p.drawPolygon(QPolygonF([QPointF(x,y) for x,y in [(65,25),(135,25),(140,170),(108,170),(100,75),(92,170),(60,170)]]))
            p.drawLine(65,39,135,39); p.drawLine(100,39,100,64)
        elif category=='Footwear':
            for offset in [0,57]:
                p.drawRoundedRect(37+offset,60,36,75,5,5)
                p.drawRoundedRect(25+offset,115,62,30,9,9)
                p.drawLine(26+offset,145,87+offset,145)
                for y in [79,89,99,109]: p.drawLine(44+offset,y,66+offset,y)
        elif category=='Socks':
            for offset in [0,60]:
                p.drawPolygon(QPolygonF([QPointF(x+offset,y) for x,y in [(45,35),(77,35),(77,115),(93,135),(88,150),(45,150),(35,135),(45,115)]]))
        else:
            p.drawPie(48,48,104,100,0,180*16); p.drawRoundedRect(42,94,116,22,5,5)
        p.end()

class Store:
    def __init__(self, path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.items=wardrobe.load_wardrobe(self.path) if self.path.exists() else []
        self.outfits_path=self.path.with_name('saved_outfits.json')
        self.outfits=json.loads(self.outfits_path.read_text(encoding='utf-8')) if self.outfits_path.exists() else []
    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        wardrobe.save_wardrobe(self.items,self.path)
        temp=self.outfits_path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.outfits,ensure_ascii=False,indent=2),encoding='utf-8')
        temp.replace(self.outfits_path)

class Window(QMainWindow):
    def __init__(self, store):
        super().__init__(); self.store=store; self.filter='Alle'; self.anchor=None; self.outfit=[]
        self.setWindowTitle('Klamotten Kurator'); self.resize(1200,820); self.setMinimumSize(1000,700)
        root=QWidget(); outer=QVBoxLayout(root); outer.setContentsMargins(36,20,36,20); outer.setSpacing(24)
        header=QHBoxLayout(); header.addWidget(label('KLAMOTTEN  /  KURATOR','brand')); header.addStretch()
        for text,page in [('Startseite','home'),('Mein Kleiderschrank','wardrobe'),('Outfits','outfit')]:
            header.addWidget(button(text,lambda checked=False,p=page:self.show_page(p),'nav'))
        outer.addLayout(header)
        self.stack=QStackedWidget(); outer.addWidget(self.stack)
        outer.addWidget(label('DEIN STIL. AUS DEM, WAS DU HAST.','eyebrow'))
        self.setCentralWidget(root); self.show_page('home')
    def content(self):
        page=QWidget(); layout=QVBoxLayout(page); layout.setContentsMargins(8,12,8,12); layout.setSpacing(22); layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setWidget(page)
        old=self.stack.currentWidget()
        if old: self.stack.removeWidget(old); old.deleteLater()
        self.stack.addWidget(scroll); self.stack.setCurrentWidget(scroll)
        return layout
    def show_page(self,page):
        self.page=page
        {'home':self.home,'wardrobe':self.wardrobe,'add':self.start_add,'outfit':self.outfit_page}[page]()
    def home(self):
        l=self.content(); l.addWidget(label('DEIN PERSÖNLICHER KLEIDERSCHRANK','eyebrow'))
        hero=QHBoxLayout(); copy=QVBoxLayout()
        headline=label('Dein Kleiderschrank.\nNeu kombiniert.','hero'); headline.setMinimumHeight(250); copy.addWidget(headline)
        copy.addWidget(label('Entdecke neue Outfits aus Kleidungsstücken,\ndie du bereits besitzt.','subtitle'))
        copy.addStretch(); hero.addLayout(copy,3)
        if self.store.items:
            art=Garment(self.store.items[0]); art.setMinimumHeight(280); hero.addWidget(art,2)
        l.addLayout(hero)
        cards=QHBoxLayout()
        cards.addWidget(button(f'01\n\nMein Kleiderschrank\n\n{len(self.store.items)} Teile   →',lambda:self.show_page('wardrobe'),'action'))
        cards.addWidget(button('02\n\nOutfit finden\n\nJetzt kombinieren   →',lambda:self.show_page('outfit'),'action'))
        l.addLayout(cards); l.addWidget(button('+  Kleidungsstück hinzufügen',lambda:self.show_page('add'),'primary')); l.addWidget(button('JSON-Kleiderschrank importieren',self.import_dataset)); l.addStretch()
    def import_dataset(self):
        filename,_=QFileDialog.getOpenFileName(self,'Kleiderschrank importieren','','JSON-Dateien (*.json)')
        if not filename: return
        try:
            items=wardrobe.load_wardrobe(filename)
            # Import a copy; preserve the source file and retain existing garments.
            merged={i['Clothing_ID']:i for i in self.store.items}
            for item in items:
                if item['Clothing_ID'] in merged and merged[item['Clothing_ID']] != item:
                    raise wardrobe.ClothingDataError('ID-Konflikt: '+item['Clothing_ID']+'. Import abgebrochen; keine Daten verändert.')
                merged[item['Clothing_ID']]=item
            wardrobe.save_wardrobe(list(merged.values()),self.store.path)
            self.store.items=list(merged.values()); self.filter='Alle'; self.show_page('wardrobe')
        except (OSError,wardrobe.ClothingDataError) as e:
            QMessageBox.warning(self,'Import fehlgeschlagen',str(e))
    def item_card(self,item,callback):
        frame=QFrame(); frame.setObjectName('card'); box=QVBoxLayout(frame)
        box.addWidget(Garment(item)); box.addWidget(label(item['Name'],'itemTitle'))
        box.addWidget(label(item['Color']+' · '+', '.join(item['Occasion']),'muted'))
        box.addWidget(button('Als Outfit-Basis wählen  →',callback,'nav'))
        return frame
    def choose(self,item):
        self.anchor=item['Clothing_ID']; self.show_page('outfit')
    def wardrobe(self):
        l=self.content(); row=QHBoxLayout(); row.addWidget(label('Mein Kleiderschrank','title')); row.addStretch()
        row.addWidget(button('+ Hinzufügen',lambda:self.show_page('add'),'primary')); l.addLayout(row)
        filters=QHBoxLayout()
        for cat in ['Alle',*TYPES]:
            b=button(CATEGORY_LABELS.get(cat,cat),lambda checked=False,c=cat:self.set_filter(c),'chip'); b.setCheckable(True); b.setChecked(cat==self.filter); filters.addWidget(b)
        l.addLayout(filters); grid=QGridLayout(); grid.setSpacing(16)
        items=[i for i in self.store.items if self.filter=='Alle' or i['Category']==self.filter]
        for n,item in enumerate(items): grid.addWidget(self.item_card(item,lambda checked=False,i=item:self.choose(i)),n//3,n%3)
        l.addLayout(grid)
        if not items: l.addWidget(label('Hier ist noch Platz. Füge dein erstes Kleidungsstück hinzu.','subtitle'))
        l.addStretch()
    def set_filter(self,cat): self.filter=cat; self.wardrobe()
    def start_add(self):
        self.step=0; self.draft={'Occasion':[],'Season':[]}; self.wizard()
    def wizard(self):
        l=self.content(); l.addWidget(button('← Abbrechen',lambda:self.show_page('wardrobe'),'nav'))
        l.addWidget(label(f'NEUES KLEIDUNGSSTÜCK  /  SCHRITT {self.step+1} VON 5','eyebrow'))
        fields=['Category','Subcategory','Color','Occasion','Season']; field=fields[self.step]
        titles=['Was möchtest du hinzufügen?','Welche Kleidungsart?','Welche Farbe?','Für welche Anlässe?','Für welche Jahreszeiten?']
        choices=[list(TYPES),TYPES.get(self.draft.get('Category'),[]),list(COLORS),STYLES,SEASONS][self.step]
        l.addWidget(label(titles[self.step],'title'))
        l.addWidget(label('Mehrere auswählen möglich.' if self.step>=3 else 'Wähle eine Option aus.','muted'))
        grid=QGridLayout(); self.options=[]
        for n,value in enumerate(choices):
            b=button(CATEGORY_LABELS.get(value,value),lambda checked=False:None,'chip'); b.setCheckable(True)
            b.setMinimumHeight(66)
            selected=self.draft.get(field,[])
            b.setChecked(value in selected if isinstance(selected,list) else value==selected)
            b.clicked.connect(lambda checked,v=value:self.select_option(v,checked))
            grid.addWidget(b,n//3,n%3); self.options.append((value,b))
        l.addLayout(grid); l.addStretch(); actions=QHBoxLayout()
        if self.step: actions.addWidget(button('← Zurück',self.previous))
        actions.addStretch(); self.next_button=button('Speichern' if self.step==4 else 'Weiter →',self.advance,'primary')
        self.next_button.setEnabled(bool(self.draft.get(field))); actions.addWidget(self.next_button); l.addLayout(actions)
    def select_option(self,value,checked):
        field=['Category','Subcategory','Color','Occasion','Season'][self.step]
        if self.step<3:
            if field=='Category' and value!=self.draft.get(field): self.draft.pop('Subcategory',None)
            self.draft[field]=value
            for v,b in self.options: b.setChecked(v==value)
        else: self.draft[field]=[v for v,b in self.options if b.isChecked()]
        self.next_button.setEnabled(bool(self.draft.get(field)))
    def previous(self): self.step-=1; self.wizard()
    def persist(self):
        try: self.store.save(); return True
        except OSError as e: QMessageBox.warning(self,'Speichern fehlgeschlagen',str(e)); return False
    def advance(self):
        if self.step<4: self.step+=1; self.wizard(); return
        try:
            wardrobe.add_item(self.store.items,self.draft['Category'],self.draft['Subcategory'],self.draft['Color'],self.draft['Occasion'],self.draft['Season'],path=self.store.path)
        except (OSError,wardrobe.ClothingDataError) as e:
            QMessageBox.warning(self,'Speichern fehlgeschlagen',str(e)); return
        self.filter='Alle'; self.show_page('wardrobe')
    def outfit_page(self):
        l=self.content(); l.addWidget(label('Dein nächstes Outfit','title'))
        l.addWidget(label('Wähle ein Kleidungsstück als Ausgangspunkt.','subtitle'))
        self.base=QComboBox()
        for item in self.store.items: self.base.addItem(item['Subcategory']+' · '+item['Color'],item['Clothing_ID'])
        if self.anchor: self.base.setCurrentIndex(max(0,self.base.findData(self.anchor)))
        row=QHBoxLayout(); row.addWidget(self.base,2); self.season=QComboBox(); self.season.addItems(SEASONS); self.season.setCurrentText('Autumn'); row.addWidget(self.season)
        self.style=QComboBox(); self.style.addItems(STYLES); self.style.setCurrentText('Casual'); row.addWidget(self.style); l.addLayout(row)
        l.addWidget(button('Outfit erstellen →',self.generate,'primary'))
        self.result=QVBoxLayout(); l.addLayout(self.result); l.addStretch()
    def generate(self):
        while self.result.count():
            w=self.result.takeAt(0).widget()
            if w: w.deleteLater()
        base=next((i for i in self.store.items if i['Clothing_ID']==self.base.currentData()),None)
        if not base: return
        season=self.season.currentText(); style=self.style.currentText()
        if season not in base['Season'] or style not in base['Occasion']:
            self.result.addWidget(label('Deine Basis passt nicht zur gewählten Jahreszeit oder zum Anlass. Ändere die Auswahl.','subtitle')); return
        selected=[base]; missing=[]
        for category in ['Top','Bottom','Footwear']:
            if base['Category']==category: continue
            candidates=[i for i in self.store.items if i['Category']==category and season in i['Season'] and style in i['Occasion']]
            # Prefer neutrals or the base color; randomize equally good candidates.
            random.shuffle(candidates)
            candidates.sort(key=lambda i:i['Color'] not in [*wardrobe.NEUTRAL_COLORS,base['Color']])
            if candidates: selected.append(candidates[0])
            else: missing.append(category)
        self.outfit=selected
        panel=QWidget(); grid=QGridLayout(panel)
        for n,item in enumerate(selected): grid.addWidget(self.item_card(item,lambda checked=False,i=item:self.choose(i)),n//3,n%3)
        self.result.addWidget(label(style+' · '+season,'eyebrow')); self.result.addWidget(panel)
        if missing: self.result.addWidget(label('Noch kein vollständiges Outfit. Passende Teile fehlen: '+', '.join(missing),'subtitle'))
        else:
            self.result.addWidget(button('Outfit speichern',self.save_outfit,'primary'))
            self.result.addWidget(button('Andere Kombination',self.generate))
    def save_outfit(self):
        record=dict(items=[i['Clothing_ID'] for i in self.outfit],style=self.style.currentText(),season=self.season.currentText())
        if record in self.store.outfits: QMessageBox.information(self,'Outfit','Dieses Outfit ist bereits gespeichert.'); return
        self.store.outfits.append(record)
        if self.persist(): QMessageBox.information(self,'Outfit gespeichert','Deine Kombination wurde gespeichert.')
        else: self.store.outfits.pop()


def main():
    app=QApplication(sys.argv); app.setApplicationName('Klamotten Kurator'); app.setOrganizationName('KlamottenKurator')
    app.setStyle('Fusion'); app.setStyleSheet(Path(__file__).with_name('style.qss').read_text(encoding='utf-8'))
    bundled=wardrobe.DEFAULT_PATH
    path=bundled if bundled.exists() else Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))/'clothing_curator_dataset.json'
    try: store=Store(path)
    except (OSError,ValueError,KeyError,TypeError,wardrobe.ClothingDataError) as e:
        QMessageBox.critical(None,'Datendatei nicht lesbar',f'{path}\n\n{e}\n\nDie Datei wurde nicht verändert.'); return 1
    window=Window(store); window.show(); return app.exec()

if __name__=='__main__': sys.exit(main())
