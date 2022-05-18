import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer

import docx
import string
import nltk
from nltk.corpus import stopwords
from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,

    Doc
)

class dictionaries:
    def __init__(self): 
        self.diction = []
        self.LoadDictionory()

    def SaveDictionary(self): #сохранение словаря в файл
        file = open('narkotiki.txt','w')
        for i in self.diction:
            line = i[0]+'#'
            for j in i[1]:
                line += j+'#'
            line+='\n'
            file.write(line)
        file.close()

    def LoadDictionory(self): #загрузка словаря из файля в систему
        file = open('narkotiki.txt','r',encoding='utf-8')
        filesdata = file.readlines()
        for i in filesdata:
            line = i.split('#')
            self.AddDict(line[0],line[1:-1])
        file.close()

    def AddDict(self,name,dict=[]): #добавление словаря
        if type(dict) != list:
            self.diction.append([name,[dict]])
        else:
            self.diction.append([name,dict])

    def AddWords(self,numb,words): #добавление слова/слов в словарь
        self.diction[numb][1].extend(words)

    def Show(self): #вывод словарей
        for i in self.diction:
            print("Словарь",i[0],":", i[1])


def normal(txt):
    doc=Doc(txt)
    doc.segment(segmenter) #разбивает на токены(слова, знаки припинания)
    doc.tag_morph(morph_tagger) #определяет часть речи
    for token in doc.tokens:    #приводит всё к начальной форме(слова, знаки и прочее)
        token.lemmatize(morph_vocab)

    doc.parse_syntax(syntax_parser)  #определяет связи
    doc.tag_ner(ner_tagger)  #извлечение сущностей
    for span in doc.spans:   #нормализация сущностей
            span.normalize(morph_vocab)

    text_new = ''    
    stop = stopwords.words("russian")
    rubbish = string.punctuation + '—' + '«' + '»'
    for _ in doc.tokens:                             #вывод слов без мусора
        if _.lemma in rubbish or _.lemma in stop or  _.lemma.isdigit():
            continue
        text_new += ' ' + _.lemma
    return text_new



class Page(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Label(
            text='Поле ввода текста',
            size_hint=(.001,.001),
            pos_hint={'x':.35,'y':.94}))

        self.textbar=TextInput(
            multiline=True,
            size_hint=(.6,.4),
            pos_hint={'x':.05,'y':.53})
        self.textbar.text='1. Введите текст или нажмите кнопку \"Файл\", чтобы загрузить файл.\n2. Нажмите кнопку \"Анализ\"'
        self.add_widget(self.textbar)

        self.butt1=Button(text="Анализ")
        self.butt1.size_hint=(.1,.01)
        self.butt1.pos_hint={'x':.765,'y':.7}
        self.butt1.bind(on_press=self.Analis)
        self.add_widget(self.butt1)

        self.butt2=Button(text="Файл")
        self.butt2.size_hint=(.1,.01)
        self.butt2.pos_hint={'x':.765,'y':.8}
        self.butt2.bind(on_press=self.FileChoose)
        self.add_widget(self.butt2)

        self.add_widget(Label(
            text='Результат:',
            size_hint=(0.001,0.001),
            pos_hint={'x':.35,'y':.46}))

        self.result=TextInput(multiline=True)
        self.result.readonly=True
        self.result.size_hint=(.6,.4)
        self.result.pos_hint={'x':.05,'y':.05}
        self.add_widget(self.result)

        self.add_widget(Label(
            text='Подозрительные слова',
            size_hint=(0.001,0.001),
            pos_hint={'x':.82,'y':.56}))

        self.suspic=TextInput(multiline=True)
        self.suspic.readonly=True
        self.suspic.size_hint=(.30,.50)
        self.suspic.pos_hint={'x':.67,'y':.05}
        self.add_widget(self.suspic)

    def Analis(self,instance):
        textt=normal(self.textbar.text)
        sustext=''
        restext=''
        results = model.predict([textt])
        for sentiment in results:
            neutral = sentiment.get('neutral')
            negative = sentiment.get('negative')
            positive = sentiment.get('positive')
            if neutral is None:
                neutral = 0
            if negative is None:
                negative = 0
            if positive is None:
                positive = 0
        resultskeyval=results[0].items()
        resultlist=list(resultskeyval)
        emotional=max(resultlist,key=lambda i : i[1])

        numb = len(dictionary.diction)
        NumbOfWords = len(textt.split())
        percents=[0]*numb
        counall=0
        for i in range (numb):
            coun = 0
            sustext+=dictionary.diction[i][0]+':\n'
            for j in dictionary.diction[i][1]:
                if (textt.find(j)!=-1):
                    coun += textt.count(j)
                    counall+=textt.count(j)
                    sustext+='       '+j+'->'+str(textt.count(j))+'\n'
            percents[i]=coun
        
        counal=0
        for i in percents[1:]:counal+=i

        counall=counall/NumbOfWords*100
        counal=counal/NumbOfWords*100
        perf=percents[0]/NumbOfWords*100
        print (emotional)

        if((perf>5 or perf<5 and counal>10 and (emotional[0]=='neutral' or emotional[0]=='positive')) and emotional[0]!='negative'):
            restext='Предварительная оценка: деструктивный контент\n'
        else:
            restext='Предварительная оценка: недеструктивный контент\n'

        restext+='1. Эмоциональная окраска: '+emotional[0]+'\n2. Деструктивные слова в тексте составляют '+str(f"{(round(counall,2)):.2f}")+'%\n3. Академическая тошнота '+str(f"{(round(perf,2)):.2f}")+'%'
        self.result.text=restext
        self.suspic.text=sustext

    def FileChoose(self, instance):
        self.lay=FileChooserLay()
        self.popup=FileChooser(content=self.lay)
        self.popup.open()
        self.lay.ids.butcl.bind(on_press=self.popup.dismiss)
        self.lay.ids.butop.bind(on_press=self.opendoc)

    def opendoc(self, instance):
        try:
            text=''
            fileDoc = docx.Document(self.lay.ids.file_chooser.selection[0]) #загрузка текста из вордовского документа в систему
            for paragraph in fileDoc.paragraphs:
                text+=paragraph.text+'\n'
            self.textbar.text=text
            self.popup.dismiss()
        except:
            pass
        try:
            filename=self.lay.ids.file_chooser.selection[0]
            repfilename=filename.replace("\\","\\\\")
            fopen=open(repfilename,'r',encoding='utf-8')
            flines=fopen.readlines()
            ftext=''
            for i in flines:
                ftext+=i
            fopen.close()
            self.textbar.text=ftext
            self.popup.dismiss()
        except:
            pass


class FileChooser(Popup):
    pass

class FileChooserLay(FloatLayout):
    pass
        

class AnalisApp(App):
    def build(self):
        self.load_kv('AnalizeTextsKivy.kv')
        return Page()

if __name__ == "__main__":
    dictionary = dictionaries()

    nltk.download('stopwords')

    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    names_extractor = NamesExtractor(morph_vocab)

    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)

    AnalisApp().run()